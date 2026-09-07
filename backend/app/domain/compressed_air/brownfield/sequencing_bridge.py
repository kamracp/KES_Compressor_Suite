"""Bridge from a brownfield audit case to the sequencing assessment (C-7d).

The audit already carries the machine register (rated FAD, rated power,
control mode, availability) and the system measurement campaign. Only what
the register does not hold is added here: per-machine control settings
(pressure band, unload power fraction, priority, VSD minimum-flow data) and
the proposal (common band, receiver volume). No machine datum is entered
twice.

Demand profile derivation is a structural weighting, not an engineering
constant: every system measurement point becomes one demand period of equal
duration (1 h) at its measured total flow and header pressure. Because the
assessment annualises by annual_operating_hours / profile_hours, equal
weighting means exactly "each measurement represents the same share of the
year". A campaign with uneven spacing should use the standalone
/compressed-air/sequencing/assess endpoint, where durations are explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.brownfield.audit_models import (
    BrownfieldAuditCase,
    ExistingCompressor,
)
from app.domain.compressed_air.performance.part_load import BelowTurndownMode
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.sequencing_assessment import (
    SequencingAssessmentInput,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    PressureBand,
    SequencedMachine,
)
from app.domain.compressed_air.station.station_models import CompressorControlMode

# Equal-duration weighting of measurement points (see module docstring).
MEASUREMENT_PERIOD_DURATION_HOURS = Decimal("1")


class InvalidBrownfieldSequencingInputError(ValueError):
    """Raised when the audit cannot be turned into a sequencing case."""


@dataclass(frozen=True, slots=True)
class BrownfieldSequencingSettings:
    """Control settings of one audited machine, keyed by its unit code."""

    unit_code: str
    band: PressureBand
    unload_power_fraction: Decimal | None
    priority: int | None = None
    minimum_flow_fraction: Decimal | None = None
    minimum_flow_power_fraction: Decimal | None = None
    standby_runs_unloaded: bool = False
    # C-8 part-load inputs (mode specific; validated by part_load).
    modulation_floor_capacity_fraction: Decimal | None = None
    turndown_flow_fraction: Decimal | None = None
    power_fraction_at_turndown: Decimal | None = None
    below_turndown: BelowTurndownMode | None = None
    unload_blowdown_seconds: Decimal | None = None


@dataclass(frozen=True, slots=True)
class BrownfieldSequencingProposal:
    """Central-sequencer proposal evaluated against the as-found baseline."""

    proposed_band: PressureBand
    receiver_volume_m3: Decimal
    machine_settings: tuple[BrownfieldSequencingSettings, ...]


# C-8: every register control mode maps onto a part_load curve.
_CONTROL_MODE_MAP: dict[CompressorControlMode, ControlMode] = {
    CompressorControlMode.FIXED_SPEED: ControlMode.FIXED_SPEED_LOAD_UNLOAD,
    CompressorControlMode.LOAD_UNLOAD: ControlMode.FIXED_SPEED_LOAD_UNLOAD,
    CompressorControlMode.VSD: ControlMode.VARIABLE_SPEED,
    CompressorControlMode.MODULATION: ControlMode.MODULATION,
    CompressorControlMode.VARIABLE_DISPLACEMENT: ControlMode.VARIABLE_DISPLACEMENT,
    CompressorControlMode.INLET_GUIDE_VANE: ControlMode.INLET_GUIDE_VANE,
}


def sequencing_control_mode(mode: CompressorControlMode) -> ControlMode:
    """Map the audit register's control mode onto the simulator's modes."""
    try:
        return _CONTROL_MODE_MAP[mode]
    except KeyError as exc:
        raise InvalidBrownfieldSequencingInputError(
            f"Control mode {mode.value} has no part-load curve."
        ) from exc


def _machine(
    compressor: ExistingCompressor,
    settings: BrownfieldSequencingSettings,
) -> SequencedMachine:
    return SequencedMachine(
        unit_code=compressor.unit_code,
        control_mode=sequencing_control_mode(compressor.control_mode),
        rated_fad_nm3_per_hr=compressor.rated_fad_nm3_per_hr,
        rated_power_kw=compressor.rated_motor_power_kw,
        band=settings.band,
        unload_power_fraction=settings.unload_power_fraction,
        priority=settings.priority,
        minimum_flow_fraction=settings.minimum_flow_fraction,
        minimum_flow_power_fraction=settings.minimum_flow_power_fraction,
        standby_runs_unloaded=settings.standby_runs_unloaded,
        modulation_floor_capacity_fraction=settings.modulation_floor_capacity_fraction,
        turndown_flow_fraction=settings.turndown_flow_fraction,
        power_fraction_at_turndown=settings.power_fraction_at_turndown,
        below_turndown=settings.below_turndown,
        unload_blowdown_seconds=settings.unload_blowdown_seconds,
    )


def build_sequencing_assessment_input(
    audit: BrownfieldAuditCase,
    proposal: BrownfieldSequencingProposal,
) -> SequencingAssessmentInput:
    """Assemble the sequencing case from the audit and the proposal."""
    if not audit.system_measurements:
        raise InvalidBrownfieldSequencingInputError(
            "Sequencing assessment needs at least one system measurement point."
        )

    settings_by_code = {s.unit_code: s for s in proposal.machine_settings}
    if len(settings_by_code) != len(proposal.machine_settings):
        raise InvalidBrownfieldSequencingInputError("Sequencing settings repeat a unit code.")

    available = tuple(c for c in audit.compressors if c.available)
    if not available:
        raise InvalidBrownfieldSequencingInputError(
            "Sequencing assessment needs at least one available compressor."
        )
    available_codes = {c.unit_code for c in available}

    unknown = sorted(set(settings_by_code) - available_codes)
    if unknown:
        raise InvalidBrownfieldSequencingInputError(
            "Sequencing settings given for units not in the available "
            f"register: {', '.join(unknown)}."
        )
    missing = sorted(available_codes - set(settings_by_code))
    if missing:
        raise InvalidBrownfieldSequencingInputError(
            f"Sequencing settings missing for available units: {', '.join(missing)}."
        )

    priorities = [settings_by_code[c.unit_code].priority for c in available]
    if any(p is None for p in priorities) and any(p is not None for p in priorities):
        raise InvalidBrownfieldSequencingInputError(
            "Priority must be set on every available unit or on none."
        )

    machines = tuple(_machine(c, settings_by_code[c.unit_code]) for c in available)
    profile = tuple(
        DemandProfilePoint(
            period_index=index,
            label=point.timestamp_label,
            demand_nm3_per_hr=point.total_flow_nm3_per_hr,
            required_pressure_bar_g=point.header_pressure_bar_g,
            duration_hours=MEASUREMENT_PERIOD_DURATION_HOURS,
        )
        for index, point in enumerate(audit.system_measurements)
    )

    return SequencingAssessmentInput(
        analysis_code=f"{audit.audit_code}-SEQ",
        baseline_machines=machines,
        demand_profile=profile,
        receiver_volume_m3=proposal.receiver_volume_m3,
        electricity_tariff_per_kwh=audit.electricity_tariff_per_kwh,
        proposed_band=proposal.proposed_band,
        annual_operating_hours=audit.annual_operating_hours,
    )
