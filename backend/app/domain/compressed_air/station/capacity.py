from decimal import Decimal

from app.domain.compressed_air.station.station_models import (
    CompressorDutyRole,
    CompressorStationCapacityResult,
    CompressorStationConfiguration,
)


class InvalidStationCapacityInputError(ValueError):
    """Raised when compressor station capacity inputs are invalid."""


def calculate_station_capacity(
    configuration: CompressorStationConfiguration,
) -> CompressorStationCapacityResult:
    """Calculate installed and available compressor-station capacity."""

    if not configuration.station_code.strip():
        raise InvalidStationCapacityInputError("Station code cannot be empty.")

    if not configuration.units:
        raise InvalidStationCapacityInputError("At least one compressor unit is required.")

    if configuration.design_flow_nm3_per_hr <= 0:
        raise InvalidStationCapacityInputError("Design flow must be greater than zero.")

    if configuration.minimum_required_pressure_bar_g < 0:
        raise InvalidStationCapacityInputError("Minimum required pressure cannot be negative.")

    for unit in configuration.units:
        _validate_unit(unit)

    total_installed_fad = sum(
        (unit.rated_fad_nm3_per_hr for unit in configuration.units),
        start=Decimal("0"),
    )

    available_units = tuple(unit for unit in configuration.units if unit.available)

    available_fad = sum(
        (unit.rated_fad_nm3_per_hr for unit in available_units),
        start=Decimal("0"),
    )

    duty_fad = sum(
        (
            unit.rated_fad_nm3_per_hr
            for unit in available_units
            if unit.duty_role
            in {
                CompressorDutyRole.BASE_LOAD,
                CompressorDutyRole.DUTY,
            }
        ),
        start=Decimal("0"),
    )

    trim_fad = sum(
        (
            unit.rated_fad_nm3_per_hr
            for unit in available_units
            if unit.duty_role == CompressorDutyRole.TRIM
        ),
        start=Decimal("0"),
    )

    standby_fad = sum(
        (
            unit.rated_fad_nm3_per_hr
            for unit in configuration.units
            if unit.duty_role == CompressorDutyRole.STANDBY
        ),
        start=Decimal("0"),
    )

    installed_capacity_margin = total_installed_fad - configuration.design_flow_nm3_per_hr

    available_capacity_margin = available_fad - configuration.design_flow_nm3_per_hr

    design_capacity_is_adequate = total_installed_fad >= configuration.design_flow_nm3_per_hr

    available_capacity_is_adequate = available_fad >= configuration.design_flow_nm3_per_hr

    active_unit_count = sum(
        1 for unit in available_units if unit.duty_role != CompressorDutyRole.STANDBY
    )

    standby_unit_count = sum(
        1 for unit in configuration.units if unit.duty_role == CompressorDutyRole.STANDBY
    )

    return CompressorStationCapacityResult(
        total_installed_fad_nm3_per_hr=total_installed_fad,
        available_fad_nm3_per_hr=available_fad,
        duty_fad_nm3_per_hr=duty_fad,
        standby_fad_nm3_per_hr=standby_fad,
        trim_fad_nm3_per_hr=trim_fad,
        design_flow_nm3_per_hr=configuration.design_flow_nm3_per_hr,
        installed_capacity_margin_nm3_per_hr=installed_capacity_margin,
        available_capacity_margin_nm3_per_hr=available_capacity_margin,
        design_capacity_is_adequate=design_capacity_is_adequate,
        available_capacity_is_adequate=available_capacity_is_adequate,
        active_unit_count=active_unit_count,
        standby_unit_count=standby_unit_count,
    )


def _validate_unit(unit) -> None:
    if not unit.unit_code.strip():
        raise InvalidStationCapacityInputError("Compressor unit code cannot be empty.")

    if unit.rated_fad_nm3_per_hr <= 0:
        raise InvalidStationCapacityInputError("Compressor rated FAD must be greater than zero.")

    if unit.minimum_stable_flow_fraction < 0 or (unit.minimum_stable_flow_fraction > 1):
        raise InvalidStationCapacityInputError(
            "Minimum stable flow fraction must be between zero and one."
        )

    if unit.rated_discharge_pressure_bar_g < 0:
        raise InvalidStationCapacityInputError("Rated discharge pressure cannot be negative.")

    if unit.rated_motor_power_kw is not None and unit.rated_motor_power_kw <= 0:
        raise InvalidStationCapacityInputError("Rated motor power must be greater than zero.")

    if (
        unit.specific_power_kw_per_nm3_per_min is not None
        and unit.specific_power_kw_per_nm3_per_min <= 0
    ):
        raise InvalidStationCapacityInputError("Specific power must be greater than zero.")
