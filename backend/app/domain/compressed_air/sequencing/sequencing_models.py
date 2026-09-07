"""Models for multi-compressor sequencing over a stepped demand profile (C-7).

Each machine holds one pressure band. Fixed-speed load/unload units cycle
between the band's load and unload pressures; VSD units follow demand inside
their band down to a minimum flow fraction. Demand is piecewise constant per
DemandProfilePoint, so every period resolves in closed form - no time stepping.

Evidence: DOE-CAC-SOURCEBOOK-2003 (unloaded screw draws 15-35 % of full-load
power), MFR-KAESER / MFR-COMPAIR sets (VSD turndown up to 86 %).

C-8: modulation, variable-displacement and inlet-guide-vane (centrifugal)
units trim through performance/part_load.py; part_load_curve() maps a
SequencedMachine onto that module's per-machine curve.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.performance.part_load import (
    BelowTurndownMode,
    PartLoadCurve,
    PartLoadMode,
)
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.schemas._bounds import DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION


class InvalidSequencingInputError(ValueError):
    """Raised when sequencing inputs are physically or structurally invalid."""


class ControlMode(StrEnum):
    FIXED_SPEED_LOAD_UNLOAD = "FIXED_SPEED_LOAD_UNLOAD"
    VARIABLE_SPEED = "VARIABLE_SPEED"
    MODULATION = "MODULATION"
    VARIABLE_DISPLACEMENT = "VARIABLE_DISPLACEMENT"
    INLET_GUIDE_VANE = "INLET_GUIDE_VANE"


_PART_LOAD_MODE: dict[ControlMode, PartLoadMode] = {
    ControlMode.FIXED_SPEED_LOAD_UNLOAD: PartLoadMode.LOAD_UNLOAD,
    ControlMode.VARIABLE_SPEED: PartLoadMode.VARIABLE_SPEED,
    ControlMode.MODULATION: PartLoadMode.MODULATION,
    ControlMode.VARIABLE_DISPLACEMENT: PartLoadMode.VARIABLE_DISPLACEMENT,
    ControlMode.INLET_GUIDE_VANE: PartLoadMode.INLET_GUIDE_VANE,
}


class DutyRole(StrEnum):
    BASE = "BASE"
    TRIM = "TRIM"
    STANDBY = "STANDBY"


@dataclass(frozen=True, slots=True)
class PressureBand:
    """Load (lower) and unload (upper) setpoints of one machine, bar g."""

    load_pressure_bar_g: Decimal
    unload_pressure_bar_g: Decimal

    @property
    def width_bar(self) -> Decimal:
        return self.unload_pressure_bar_g - self.load_pressure_bar_g


@dataclass(frozen=True, slots=True)
class SequencedMachine:
    unit_code: str
    control_mode: ControlMode
    rated_fad_nm3_per_hr: Decimal
    rated_power_kw: Decimal
    band: PressureBand
    # Fixed-speed only: unloaded power as a fraction of rated power
    # (DOE-CAC-SOURCEBOOK-2003 band 0.15-0.35, from nameplate or measurement).
    unload_power_fraction: Decimal | None = None
    # VSD only: minimum stable flow as a fraction of rated FAD (1 - turndown).
    minimum_flow_fraction: Decimal | None = None
    # VSD only: power at minimum flow as a fraction of rated power; the power
    # curve between minimum and rated flow is taken as linear in flow.
    minimum_flow_power_fraction: Decimal | None = None
    # Central-sequencer priority (1 loads first). None -> order by band pressure,
    # i.e. the as-found local cascade.
    priority: int | None = None
    # As-found plants often leave the units below the trim running unloaded
    # until an unload timer stops them; a sequencer with auto-standby stops them.
    standby_runs_unloaded: bool = False
    # MODULATION only (C-8): capacity fraction where throttling ends and the
    # unit unloads; None -> DOE-CAC-SOURCEBOOK-2003 Fig. 2.6 default (0.40).
    modulation_floor_capacity_fraction: Decimal | None = None
    # INLET_GUIDE_VANE only (C-8, machine specific per CAGI): turndown as a
    # fraction of rated FAD, power at that turndown, and what happens below it.
    turndown_flow_fraction: Decimal | None = None
    power_fraction_at_turndown: Decimal | None = None
    below_turndown: BelowTurndownMode | None = None  # None -> BLOW_OFF
    # FIXED_SPEED_LOAD_UNLOAD only, optional manufacturer figure: sump
    # blowdown time. Reproduces the DOE storage-dependent penalty.
    unload_blowdown_seconds: Decimal | None = None


def part_load_curve(machine: SequencedMachine) -> PartLoadCurve:
    """Map a sequenced machine onto its part-load curve description."""

    return PartLoadCurve(
        mode=_PART_LOAD_MODE[machine.control_mode],
        unload_power_fraction=machine.unload_power_fraction,
        modulation_floor_capacity_fraction=(
            machine.modulation_floor_capacity_fraction
            if machine.modulation_floor_capacity_fraction is not None
            else DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION
        ),
        minimum_flow_fraction=machine.minimum_flow_fraction,
        minimum_flow_power_fraction=machine.minimum_flow_power_fraction,
        turndown_flow_fraction=machine.turndown_flow_fraction,
        power_fraction_at_turndown=machine.power_fraction_at_turndown,
        below_turndown=(
            machine.below_turndown
            if machine.below_turndown is not None
            else BelowTurndownMode.BLOW_OFF
        ),
        unload_blowdown_seconds=machine.unload_blowdown_seconds,
    )


@dataclass(frozen=True, slots=True)
class SequencingInput:
    analysis_code: str
    machines: tuple[SequencedMachine, ...]
    demand_profile: tuple[DemandProfilePoint, ...]
    receiver_volume_m3: Decimal
    electricity_tariff_per_kwh: Decimal


@dataclass(frozen=True, slots=True)
class MachinePeriodResult:
    unit_code: str
    period_index: int
    duty_role: DutyRole
    delivered_flow_nm3_per_hr: Decimal
    load_fraction: Decimal  # share of the period spent loaded (fixed-speed) or 1 for VSD
    cycles_per_hour: Decimal | None  # fixed-speed only
    average_power_kw: Decimal
    energy_kwh: Decimal
    # C-8: centrifugal blow-off vents this much of the unit's output.
    wasted_flow_nm3_per_hr: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class PeriodResult:
    period_index: int
    label: str
    demand_nm3_per_hr: Decimal
    duration_hours: Decimal
    supplied_flow_nm3_per_hr: Decimal
    shortfall_nm3_per_hr: Decimal
    average_header_pressure_bar_g: Decimal
    total_power_kw: Decimal
    energy_kwh: Decimal
    machines: tuple[MachinePeriodResult, ...]


@dataclass(frozen=True, slots=True)
class SequencingResult:
    analysis_code: str
    periods: tuple[PeriodResult, ...]
    total_energy_kwh: Decimal
    total_energy_cost: Decimal
    specific_power_kw_per_nm3_per_min: Decimal
    unload_energy_kwh: Decimal  # trim units unloaded, producing no air
    standby_energy_kwh: Decimal  # standby units left running unloaded
    unmet_demand_hours: Decimal
