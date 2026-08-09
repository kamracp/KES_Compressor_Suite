from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CompressorTechnology(StrEnum):
    """Compressed-air compressor technology."""

    ROTARY_SCREW_OIL_INJECTED = "ROTARY_SCREW_OIL_INJECTED"
    ROTARY_SCREW_OIL_FREE = "ROTARY_SCREW_OIL_FREE"
    RECIPROCATING = "RECIPROCATING"
    CENTRIFUGAL = "CENTRIFUGAL"
    SCROLL = "SCROLL"


class CompressorControlMode(StrEnum):
    """Primary compressor capacity-control mode."""

    FIXED_SPEED = "FIXED_SPEED"
    VSD = "VSD"
    LOAD_UNLOAD = "LOAD_UNLOAD"
    MODULATION = "MODULATION"
    INLET_GUIDE_VANE = "INLET_GUIDE_VANE"


class CompressorDutyRole(StrEnum):
    """Operational role of a compressor within a station."""

    BASE_LOAD = "BASE_LOAD"
    TRIM = "TRIM"
    DUTY = "DUTY"
    STANDBY = "STANDBY"


class RedundancyPhilosophy(StrEnum):
    """Station redundancy philosophy."""

    NONE = "NONE"
    N_PLUS_1 = "N_PLUS_1"
    N_PLUS_2 = "N_PLUS_2"
    FULL_STANDBY = "FULL_STANDBY"


@dataclass(frozen=True, slots=True)
class CompressorUnit:
    """One compressor unit within a compressed-air station."""

    unit_code: str
    technology: CompressorTechnology
    control_mode: CompressorControlMode
    duty_role: CompressorDutyRole

    rated_fad_nm3_per_hr: Decimal
    minimum_stable_flow_fraction: Decimal

    rated_discharge_pressure_bar_g: Decimal

    rated_motor_power_kw: Decimal | None = None
    specific_power_kw_per_nm3_per_min: Decimal | None = None

    available: bool = True
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CompressorStationConfiguration:
    """Compressed-air station arrangement."""

    station_code: str

    units: tuple[CompressorUnit, ...]

    redundancy_philosophy: RedundancyPhilosophy

    minimum_required_pressure_bar_g: Decimal
    design_flow_nm3_per_hr: Decimal

    master_control_enabled: bool = False


@dataclass(frozen=True, slots=True)
class CompressorStationCapacityResult:
    """Capacity summary for a compressor station configuration."""

    total_installed_fad_nm3_per_hr: Decimal
    available_fad_nm3_per_hr: Decimal

    duty_fad_nm3_per_hr: Decimal
    standby_fad_nm3_per_hr: Decimal
    trim_fad_nm3_per_hr: Decimal

    design_flow_nm3_per_hr: Decimal

    installed_capacity_margin_nm3_per_hr: Decimal
    available_capacity_margin_nm3_per_hr: Decimal

    design_capacity_is_adequate: bool
    available_capacity_is_adequate: bool

    active_unit_count: int
    standby_unit_count: int
