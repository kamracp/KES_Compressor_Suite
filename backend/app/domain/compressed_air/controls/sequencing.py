from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorUnit,
)


class InvalidSequencingInputError(ValueError):
    """Raised when compressor sequencing inputs are invalid."""


class UnitOperatingCommand(StrEnum):
    """Requested operating command for one compressor."""

    STOP = "STOP"
    BASE_LOAD = "BASE_LOAD"
    TRIM = "TRIM"
    FULL_LOAD = "FULL_LOAD"
    STANDBY = "STANDBY"


@dataclass(frozen=True, slots=True)
class SequencingUnitResult:
    """Operating instruction for one compressor unit."""

    unit_code: str

    duty_role: CompressorDutyRole
    control_mode: CompressorControlMode

    command: UnitOperatingCommand

    assigned_flow_nm3_per_hr: Decimal

    rated_fad_nm3_per_hr: Decimal
    minimum_stable_flow_nm3_per_hr: Decimal

    utilization_fraction: Decimal

    is_running: bool


@dataclass(frozen=True, slots=True)
class SequencingResult:
    """Compressor-station sequencing result for one demand point."""

    required_flow_nm3_per_hr: Decimal

    assigned_flow_nm3_per_hr: Decimal
    unmet_flow_nm3_per_hr: Decimal
    excess_running_capacity_nm3_per_hr: Decimal

    running_unit_count: int
    standby_unit_count: int

    vsd_trim_active: bool
    demand_is_fully_covered: bool

    unit_results: tuple[SequencingUnitResult, ...]


def sequence_compressors(
    *,
    units: tuple[CompressorUnit, ...],
    required_flow_nm3_per_hr: Decimal,
) -> SequencingResult:
    """Sequence available compressors to satisfy one factory demand point."""

    if required_flow_nm3_per_hr < 0:
        raise InvalidSequencingInputError("Required flow cannot be negative.")

    if not units:
        raise InvalidSequencingInputError("At least one compressor unit is required.")

    for unit in units:
        _validate_unit(unit)

    active_candidates = tuple(
        unit for unit in units if unit.available and unit.duty_role != CompressorDutyRole.STANDBY
    )

    standby_units = tuple(unit for unit in units if unit.duty_role == CompressorDutyRole.STANDBY)

    base_units = tuple(
        unit
        for unit in active_candidates
        if unit.duty_role
        in {
            CompressorDutyRole.BASE_LOAD,
            CompressorDutyRole.DUTY,
        }
        and unit.control_mode != CompressorControlMode.VSD
    )

    trim_units = tuple(
        unit
        for unit in active_candidates
        if unit.control_mode == CompressorControlMode.VSD
        or unit.duty_role == CompressorDutyRole.TRIM
    )

    remaining_flow = required_flow_nm3_per_hr

    assigned_flow_by_unit: dict[str, Decimal] = {}
    command_by_unit: dict[str, UnitOperatingCommand] = {}

    for unit in base_units:
        if remaining_flow <= 0:
            break

        if remaining_flow >= unit.rated_fad_nm3_per_hr:
            assigned = unit.rated_fad_nm3_per_hr
            command = UnitOperatingCommand.BASE_LOAD
        else:
            minimum_flow = unit.rated_fad_nm3_per_hr * unit.minimum_stable_flow_fraction

            if remaining_flow >= minimum_flow:
                assigned = remaining_flow
                command = UnitOperatingCommand.FULL_LOAD
            else:
                break

        assigned_flow_by_unit[unit.unit_code] = assigned
        command_by_unit[unit.unit_code] = command
        remaining_flow -= assigned

    for unit in trim_units:
        if remaining_flow <= 0:
            break

        minimum_flow = unit.rated_fad_nm3_per_hr * unit.minimum_stable_flow_fraction

        assigned = min(
            remaining_flow,
            unit.rated_fad_nm3_per_hr,
        )

        if assigned < minimum_flow and required_flow_nm3_per_hr > 0:
            assigned = minimum_flow

        assigned_flow_by_unit[unit.unit_code] = assigned
        command_by_unit[unit.unit_code] = UnitOperatingCommand.TRIM

        remaining_flow -= assigned

    if remaining_flow > 0:
        for unit in standby_units:
            if not unit.available:
                continue

            assigned = min(
                remaining_flow,
                unit.rated_fad_nm3_per_hr,
            )

            assigned_flow_by_unit[unit.unit_code] = assigned
            command_by_unit[unit.unit_code] = UnitOperatingCommand.FULL_LOAD

            remaining_flow -= assigned

            if remaining_flow <= 0:
                break

    unit_results: list[SequencingUnitResult] = []

    for unit in units:
        assigned_flow = assigned_flow_by_unit.get(
            unit.unit_code,
            Decimal("0"),
        )

        if unit.unit_code in command_by_unit:
            command = command_by_unit[unit.unit_code]
        elif unit.duty_role == CompressorDutyRole.STANDBY:
            command = UnitOperatingCommand.STANDBY
        else:
            command = UnitOperatingCommand.STOP

        minimum_stable_flow = unit.rated_fad_nm3_per_hr * unit.minimum_stable_flow_fraction

        utilization_fraction = (
            assigned_flow / unit.rated_fad_nm3_per_hr
            if unit.rated_fad_nm3_per_hr > 0
            else Decimal("0")
        )

        unit_results.append(
            SequencingUnitResult(
                unit_code=unit.unit_code,
                duty_role=unit.duty_role,
                control_mode=unit.control_mode,
                command=command,
                assigned_flow_nm3_per_hr=assigned_flow,
                rated_fad_nm3_per_hr=unit.rated_fad_nm3_per_hr,
                minimum_stable_flow_nm3_per_hr=minimum_stable_flow,
                utilization_fraction=utilization_fraction,
                is_running=assigned_flow > 0,
            )
        )

    assigned_flow = sum(
        (item.assigned_flow_nm3_per_hr for item in unit_results),
        start=Decimal("0"),
    )

    unmet_flow = max(
        required_flow_nm3_per_hr - assigned_flow,
        Decimal("0"),
    )

    running_capacity = sum(
        (item.rated_fad_nm3_per_hr for item in unit_results if item.is_running),
        start=Decimal("0"),
    )

    excess_running_capacity = max(
        running_capacity - required_flow_nm3_per_hr,
        Decimal("0"),
    )

    running_unit_count = sum(1 for item in unit_results if item.is_running)

    vsd_trim_active = any(
        item.is_running and item.control_mode == CompressorControlMode.VSD for item in unit_results
    )

    return SequencingResult(
        required_flow_nm3_per_hr=required_flow_nm3_per_hr,
        assigned_flow_nm3_per_hr=assigned_flow,
        unmet_flow_nm3_per_hr=unmet_flow,
        excess_running_capacity_nm3_per_hr=excess_running_capacity,
        running_unit_count=running_unit_count,
        standby_unit_count=len(standby_units),
        vsd_trim_active=vsd_trim_active,
        demand_is_fully_covered=unmet_flow == 0,
        unit_results=tuple(unit_results),
    )


def _validate_unit(
    unit: CompressorUnit,
) -> None:
    if not unit.unit_code.strip():
        raise InvalidSequencingInputError("Compressor unit code cannot be empty.")

    if unit.rated_fad_nm3_per_hr <= 0:
        raise InvalidSequencingInputError("Compressor rated FAD must be greater than zero.")

    if unit.minimum_stable_flow_fraction < 0 or unit.minimum_stable_flow_fraction > 1:
        raise InvalidSequencingInputError(
            "Minimum stable flow fraction must be between zero and one."
        )
