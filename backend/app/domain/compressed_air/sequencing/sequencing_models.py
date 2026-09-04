"""Models for multi-compressor sequencing over a stepped demand profile (C-7).

Each machine holds one pressure band. Fixed-speed load/unload units cycle
between the band's load and unload pressures; VSD units follow demand inside
their band down to a minimum flow fraction. Demand is piecewise constant per
DemandProfilePoint, so every period resolves in closed form - no time stepping.

Evidence: DOE-CAC-SOURCEBOOK-2003 (unloaded screw draws 15-35 % of full-load
power), MFR-KAESER / MFR-COMPAIR sets (VSD turndown up to 86 %).
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint


class InvalidSequencingInputError(ValueError):
    """Raised when sequencing inputs are physically or structurally invalid."""


class ControlMode(StrEnum):
    FIXED_SPEED_LOAD_UNLOAD = "FIXED_SPEED_LOAD_UNLOAD"
    VARIABLE_SPEED = "VARIABLE_SPEED"


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
    unload_energy_kwh: Decimal  # energy spent producing no air
    unmet_demand_hours: Decimal
