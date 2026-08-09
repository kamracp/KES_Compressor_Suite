from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.profiles.demand_profile import DemandProfileResult
from app.domain.compressed_air.station.capacity import calculate_station_capacity
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorStationConfiguration,
)


class InvalidConfigurationOptimizerInputError(ValueError):
    """Raised when station configuration optimization inputs are invalid."""


@dataclass(frozen=True, slots=True)
class StationConfigurationAssessment:
    """Engineering assessment of one compressor station configuration."""

    station_code: str

    total_installed_fad_nm3_per_hr: Decimal
    available_fad_nm3_per_hr: Decimal

    minimum_controllable_flow_nm3_per_hr: Decimal
    maximum_available_flow_nm3_per_hr: Decimal

    minimum_profile_demand_nm3_per_hr: Decimal
    average_profile_demand_nm3_per_hr: Decimal
    maximum_profile_demand_nm3_per_hr: Decimal

    peak_capacity_margin_nm3_per_hr: Decimal

    has_vsd_trim: bool
    has_standby_unit: bool

    low_demand_is_controllable: bool
    peak_demand_is_covered: bool

    capacity_score: Decimal
    turndown_score: Decimal
    redundancy_score: Decimal
    control_score: Decimal

    overall_score: Decimal

    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StationOptimizationResult:
    """Comparison and ranking of compressor station configurations."""

    recommended_station_code: str
    assessments: tuple[StationConfigurationAssessment, ...]


def optimize_station_configurations(
    *,
    configurations: tuple[CompressorStationConfiguration, ...],
    demand_profile: DemandProfileResult,
) -> StationOptimizationResult:
    """Compare compressor station alternatives against the demand profile."""

    if not configurations:
        raise InvalidConfigurationOptimizerInputError(
            "At least one station configuration is required."
        )

    assessments = tuple(
        _assess_configuration(
            configuration=configuration,
            demand_profile=demand_profile,
        )
        for configuration in configurations
    )

    recommended = max(
        assessments,
        key=lambda item: (
            item.overall_score,
            item.peak_capacity_margin_nm3_per_hr,
        ),
    )

    return StationOptimizationResult(
        recommended_station_code=recommended.station_code,
        assessments=assessments,
    )


def _assess_configuration(
    *,
    configuration: CompressorStationConfiguration,
    demand_profile: DemandProfileResult,
) -> StationConfigurationAssessment:
    capacity = calculate_station_capacity(configuration)

    available_active_units = tuple(
        unit
        for unit in configuration.units
        if unit.available and unit.duty_role != CompressorDutyRole.STANDBY
    )

    if not available_active_units:
        minimum_controllable_flow = Decimal("0")
    else:
        minimum_controllable_flow = sum(
            (
                unit.rated_fad_nm3_per_hr * unit.minimum_stable_flow_fraction
                for unit in available_active_units
            ),
            start=Decimal("0"),
        )

    maximum_available_flow = capacity.available_fad_nm3_per_hr

    has_vsd_trim = any(
        unit.available
        and unit.control_mode == CompressorControlMode.VSD
        and unit.duty_role == CompressorDutyRole.TRIM
        for unit in configuration.units
    )

    has_standby_unit = any(
        unit.duty_role == CompressorDutyRole.STANDBY for unit in configuration.units
    )

    low_demand_is_controllable = (
        minimum_controllable_flow <= demand_profile.minimum_demand_nm3_per_hr
    )

    peak_demand_is_covered = maximum_available_flow >= demand_profile.maximum_demand_nm3_per_hr

    peak_capacity_margin = maximum_available_flow - demand_profile.maximum_demand_nm3_per_hr

    capacity_score = _capacity_score(
        peak_demand_is_covered=peak_demand_is_covered,
        peak_capacity_margin=peak_capacity_margin,
        maximum_demand=demand_profile.maximum_demand_nm3_per_hr,
    )

    turndown_score = _turndown_score(
        low_demand_is_controllable=low_demand_is_controllable,
        has_vsd_trim=has_vsd_trim,
    )

    redundancy_score = _redundancy_score(
        has_standby_unit=has_standby_unit,
        available_capacity_is_adequate=capacity.available_capacity_is_adequate,
    )

    control_score = _control_score(
        has_vsd_trim=has_vsd_trim,
        master_control_enabled=configuration.master_control_enabled,
    )

    overall_score = (
        capacity_score * Decimal("0.40")
        + turndown_score * Decimal("0.25")
        + redundancy_score * Decimal("0.20")
        + control_score * Decimal("0.15")
    )

    rationale = _build_rationale(
        peak_demand_is_covered=peak_demand_is_covered,
        low_demand_is_controllable=low_demand_is_controllable,
        has_vsd_trim=has_vsd_trim,
        has_standby_unit=has_standby_unit,
        master_control_enabled=configuration.master_control_enabled,
    )

    return StationConfigurationAssessment(
        station_code=configuration.station_code,
        total_installed_fad_nm3_per_hr=capacity.total_installed_fad_nm3_per_hr,
        available_fad_nm3_per_hr=capacity.available_fad_nm3_per_hr,
        minimum_controllable_flow_nm3_per_hr=minimum_controllable_flow,
        maximum_available_flow_nm3_per_hr=maximum_available_flow,
        minimum_profile_demand_nm3_per_hr=(demand_profile.minimum_demand_nm3_per_hr),
        average_profile_demand_nm3_per_hr=(demand_profile.average_demand_nm3_per_hr),
        maximum_profile_demand_nm3_per_hr=(demand_profile.maximum_demand_nm3_per_hr),
        peak_capacity_margin_nm3_per_hr=peak_capacity_margin,
        has_vsd_trim=has_vsd_trim,
        has_standby_unit=has_standby_unit,
        low_demand_is_controllable=low_demand_is_controllable,
        peak_demand_is_covered=peak_demand_is_covered,
        capacity_score=capacity_score,
        turndown_score=turndown_score,
        redundancy_score=redundancy_score,
        control_score=control_score,
        overall_score=overall_score,
        rationale=rationale,
    )


def _capacity_score(
    *,
    peak_demand_is_covered: bool,
    peak_capacity_margin: Decimal,
    maximum_demand: Decimal,
) -> Decimal:
    if not peak_demand_is_covered:
        return Decimal("0")

    if maximum_demand <= 0:
        return Decimal("100")

    margin_fraction = peak_capacity_margin / maximum_demand

    if margin_fraction <= Decimal("0.15"):
        return Decimal("100")

    if margin_fraction <= Decimal("0.30"):
        return Decimal("90")

    if margin_fraction <= Decimal("0.50"):
        return Decimal("75")

    return Decimal("60")


def _turndown_score(
    *,
    low_demand_is_controllable: bool,
    has_vsd_trim: bool,
) -> Decimal:
    if low_demand_is_controllable and has_vsd_trim:
        return Decimal("100")

    if low_demand_is_controllable:
        return Decimal("80")

    if has_vsd_trim:
        return Decimal("65")

    return Decimal("40")


def _redundancy_score(
    *,
    has_standby_unit: bool,
    available_capacity_is_adequate: bool,
) -> Decimal:
    if has_standby_unit and available_capacity_is_adequate:
        return Decimal("100")

    if available_capacity_is_adequate:
        return Decimal("75")

    return Decimal("25")


def _control_score(
    *,
    has_vsd_trim: bool,
    master_control_enabled: bool,
) -> Decimal:
    if has_vsd_trim and master_control_enabled:
        return Decimal("100")

    if has_vsd_trim or master_control_enabled:
        return Decimal("75")

    return Decimal("50")


def _build_rationale(
    *,
    peak_demand_is_covered: bool,
    low_demand_is_controllable: bool,
    has_vsd_trim: bool,
    has_standby_unit: bool,
    master_control_enabled: bool,
) -> tuple[str, ...]:
    rationale: list[str] = []

    if peak_demand_is_covered:
        rationale.append("Available compressor capacity covers the maximum demand profile.")
    else:
        rationale.append("Available compressor capacity does not cover the maximum demand profile.")

    if low_demand_is_controllable:
        rationale.append(
            "Minimum controllable station flow is compatible with low-demand operation."
        )
    else:
        rationale.append(
            "Low-demand operation may cause excessive unload, recycle, or inefficient control."
        )

    if has_vsd_trim:
        rationale.append("A VSD trim compressor is available for variable-demand control.")

    if has_standby_unit:
        rationale.append("Dedicated standby capacity is included in the station arrangement.")

    if master_control_enabled:
        rationale.append("Master control is enabled for coordinated compressor sequencing.")

    return tuple(rationale)
