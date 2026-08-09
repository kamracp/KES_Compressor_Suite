from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CentrifugalDriverType(StrEnum):
    ELECTRIC_MOTOR = "ELECTRIC_MOTOR"
    GAS_TURBINE = "GAS_TURBINE"
    STEAM_TURBINE = "STEAM_TURBINE"


@dataclass(frozen=True, slots=True)
class CentrifugalOperatingPoint:
    """Operating conditions for a centrifugal compressor."""

    suction_pressure_bar: Decimal
    discharge_pressure_bar: Decimal
    suction_temperature_k: Decimal
    mass_flow_kg_per_s: Decimal
    actual_flow_m3_per_s: Decimal
    molecular_weight_kg_per_kmol: Decimal
    suction_z_factor: Decimal
    discharge_z_factor: Decimal
    isentropic_exponent: Decimal
    polytropic_efficiency: Decimal


@dataclass(frozen=True, slots=True)
class PolytropicHeadResult:
    """Calculated centrifugal compressor polytropic head."""

    average_z_factor: Decimal
    polytropic_exponent: Decimal
    overall_compression_ratio: Decimal
    polytropic_head_kj_per_kg: Decimal


@dataclass(frozen=True, slots=True)
class ImpellerSizingResult:
    """Calculated centrifugal compressor impeller sizing result."""

    number_of_impeller_stages: int
    head_per_stage_kj_per_kg: Decimal
    head_coefficient: Decimal
    impeller_tip_speed_m_per_s: Decimal
    rotational_speed_rpm: Decimal
    impeller_diameter_m: Decimal


@dataclass(frozen=True, slots=True)
class CentrifugalPowerResult:
    """Calculated centrifugal compressor power result."""

    gas_power_kw: Decimal
    shaft_power_kw: Decimal
    required_driver_power_kw: Decimal
    selected_driver_power_kw: Decimal
    driver_is_adequate: bool
    driver_type: CentrifugalDriverType


@dataclass(frozen=True, slots=True)
class CentrifugalSizingResult:
    """Combined centrifugal compressor sizing result."""

    operating_point: CentrifugalOperatingPoint
    head: PolytropicHeadResult
    impeller: ImpellerSizingResult
    power: CentrifugalPowerResult
