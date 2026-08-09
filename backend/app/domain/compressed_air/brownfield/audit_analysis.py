from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
)


class InvalidBrownfieldAuditInputError(ValueError):
    """Raised when brownfield compressed-air audit inputs are invalid."""


MINUTES_PER_HOUR = Decimal("60")


@dataclass(frozen=True, slots=True)
class BrownfieldAuditAnalysisResult:
    """Engineering summary of an existing compressed-air system."""

    audit_code: str
    project_id: int

    installed_capacity_nm3_per_hr: Decimal
    available_capacity_nm3_per_hr: Decimal

    average_system_flow_nm3_per_hr: Decimal
    peak_system_flow_nm3_per_hr: Decimal
    minimum_system_flow_nm3_per_hr: Decimal

    average_system_power_kw: Decimal
    peak_system_power_kw: Decimal

    average_header_pressure_bar_g: Decimal
    maximum_header_pressure_bar_g: Decimal
    minimum_header_pressure_bar_g: Decimal

    average_capacity_utilization_fraction: Decimal
    peak_capacity_utilization_fraction: Decimal

    measured_specific_power_kw_per_nm3_per_min: Decimal | None

    unloaded_measurement_fraction: Decimal

    leakage_flow_nm3_per_hr: Decimal
    leakage_fraction_of_average_demand: Decimal

    annual_operating_hours: Decimal
    electricity_tariff_per_kwh: Decimal

    estimated_annual_energy_kwh: Decimal
    estimated_annual_energy_cost: Decimal

    installed_capacity_is_sufficient_for_peak: bool
    high_unloaded_running_detected: bool
    significant_leakage_detected: bool


def analyze_brownfield_audit(
    audit: BrownfieldAuditCase,
) -> BrownfieldAuditAnalysisResult:
    """Analyze an existing factory compressed-air system."""

    _validate_audit(audit)

    installed_capacity = sum(
        (compressor.rated_fad_nm3_per_hr for compressor in audit.compressors),
        start=Decimal("0"),
    )

    available_capacity = sum(
        (
            compressor.rated_fad_nm3_per_hr
            for compressor in audit.compressors
            if compressor.available
        ),
        start=Decimal("0"),
    )

    system_measurements = audit.system_measurements

    average_system_flow = _average(
        tuple(point.total_flow_nm3_per_hr for point in system_measurements)
    )

    peak_system_flow = max(point.total_flow_nm3_per_hr for point in system_measurements)

    minimum_system_flow = min(point.total_flow_nm3_per_hr for point in system_measurements)

    average_system_power = _average(tuple(point.total_power_kw for point in system_measurements))

    peak_system_power = max(point.total_power_kw for point in system_measurements)

    average_header_pressure = _average(
        tuple(point.header_pressure_bar_g for point in system_measurements)
    )

    maximum_header_pressure = max(point.header_pressure_bar_g for point in system_measurements)

    minimum_header_pressure = min(point.header_pressure_bar_g for point in system_measurements)

    if available_capacity > 0:
        average_capacity_utilization_fraction = average_system_flow / available_capacity

        peak_capacity_utilization_fraction = peak_system_flow / available_capacity
    else:
        average_capacity_utilization_fraction = Decimal("0")
        peak_capacity_utilization_fraction = Decimal("0")

    if average_system_flow > 0:
        average_system_flow_nm3_per_min = average_system_flow / MINUTES_PER_HOUR

        measured_specific_power = average_system_power / average_system_flow_nm3_per_min
    else:
        measured_specific_power = None

    compressor_measurements = audit.compressor_measurements

    if compressor_measurements:
        unloaded_count = sum(
            1
            for point in compressor_measurements
            if point.operating_state == AuditOperatingState.UNLOADED
        )

        unloaded_measurement_fraction = Decimal(unloaded_count) / Decimal(
            len(compressor_measurements)
        )
    else:
        unloaded_measurement_fraction = Decimal("0")

    if audit.leakage_summary is None:
        leakage_flow = Decimal("0")
    else:
        leakage_flow = audit.leakage_summary.measured_leakage_flow_nm3_per_hr

    if average_system_flow > 0:
        leakage_fraction_of_average_demand = leakage_flow / average_system_flow
    else:
        leakage_fraction_of_average_demand = Decimal("0")

    estimated_annual_energy_kwh = average_system_power * audit.annual_operating_hours

    estimated_annual_energy_cost = estimated_annual_energy_kwh * audit.electricity_tariff_per_kwh

    installed_capacity_is_sufficient_for_peak = available_capacity >= peak_system_flow

    high_unloaded_running_detected = unloaded_measurement_fraction >= Decimal("0.20")

    significant_leakage_detected = leakage_fraction_of_average_demand >= Decimal("0.10")

    return BrownfieldAuditAnalysisResult(
        audit_code=audit.audit_code,
        project_id=audit.project_id,
        installed_capacity_nm3_per_hr=installed_capacity,
        available_capacity_nm3_per_hr=available_capacity,
        average_system_flow_nm3_per_hr=average_system_flow,
        peak_system_flow_nm3_per_hr=peak_system_flow,
        minimum_system_flow_nm3_per_hr=minimum_system_flow,
        average_system_power_kw=average_system_power,
        peak_system_power_kw=peak_system_power,
        average_header_pressure_bar_g=average_header_pressure,
        maximum_header_pressure_bar_g=maximum_header_pressure,
        minimum_header_pressure_bar_g=minimum_header_pressure,
        average_capacity_utilization_fraction=(average_capacity_utilization_fraction),
        peak_capacity_utilization_fraction=(peak_capacity_utilization_fraction),
        measured_specific_power_kw_per_nm3_per_min=measured_specific_power,
        unloaded_measurement_fraction=unloaded_measurement_fraction,
        leakage_flow_nm3_per_hr=leakage_flow,
        leakage_fraction_of_average_demand=(leakage_fraction_of_average_demand),
        annual_operating_hours=audit.annual_operating_hours,
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        estimated_annual_energy_kwh=estimated_annual_energy_kwh,
        estimated_annual_energy_cost=estimated_annual_energy_cost,
        installed_capacity_is_sufficient_for_peak=(installed_capacity_is_sufficient_for_peak),
        high_unloaded_running_detected=high_unloaded_running_detected,
        significant_leakage_detected=significant_leakage_detected,
    )


def _average(
    values: tuple[Decimal, ...],
) -> Decimal:
    if not values:
        raise InvalidBrownfieldAuditInputError("At least one measurement value is required.")

    return sum(
        values,
        start=Decimal("0"),
    ) / Decimal(len(values))


def _validate_audit(
    audit: BrownfieldAuditCase,
) -> None:
    if not audit.audit_code.strip():
        raise InvalidBrownfieldAuditInputError("Audit code cannot be empty.")

    if audit.project_id <= 0:
        raise InvalidBrownfieldAuditInputError("Project id must be greater than zero.")

    if not audit.compressors:
        raise InvalidBrownfieldAuditInputError("At least one existing compressor is required.")

    if not audit.system_measurements:
        raise InvalidBrownfieldAuditInputError("At least one system measurement is required.")

    if audit.annual_operating_hours <= 0:
        raise InvalidBrownfieldAuditInputError("Annual operating hours must be greater than zero.")

    if audit.electricity_tariff_per_kwh < 0:
        raise InvalidBrownfieldAuditInputError("Electricity tariff cannot be negative.")

    for compressor in audit.compressors:
        if compressor.rated_fad_nm3_per_hr <= 0:
            raise InvalidBrownfieldAuditInputError(
                "Existing compressor rated FAD must be greater than zero."
            )

        if compressor.rated_motor_power_kw <= 0:
            raise InvalidBrownfieldAuditInputError(
                "Existing compressor motor power must be greater than zero."
            )

    for point in audit.system_measurements:
        if point.total_flow_nm3_per_hr < 0:
            raise InvalidBrownfieldAuditInputError("Measured system flow cannot be negative.")

        if point.header_pressure_bar_g < 0:
            raise InvalidBrownfieldAuditInputError("Measured header pressure cannot be negative.")

        if point.total_power_kw < 0:
            raise InvalidBrownfieldAuditInputError("Measured system power cannot be negative.")

    if audit.leakage_summary is not None:
        if audit.leakage_summary.measured_leakage_flow_nm3_per_hr < 0:
            raise InvalidBrownfieldAuditInputError("Measured leakage flow cannot be negative.")

        if (
            audit.leakage_summary.estimated_repair_fraction < 0
            or audit.leakage_summary.estimated_repair_fraction > 1
        ):
            raise InvalidBrownfieldAuditInputError(
                "Estimated repair fraction must be between zero and one."
            )
