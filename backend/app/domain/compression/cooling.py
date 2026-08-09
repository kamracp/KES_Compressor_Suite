from dataclasses import dataclass
from decimal import Decimal


WATER_SPECIFIC_HEAT_KJ_PER_KG_K = Decimal("4.186")
WATER_DENSITY_KG_PER_M3 = Decimal("997")


class InvalidCoolingInputError(ValueError):
    """Raised when compressor cooling inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CoolingResult:
    """Compressor cooling-duty calculation result."""

    cooling_duty_kw: Decimal
    cooling_water_mass_flow_kg_per_s: Decimal
    cooling_water_flow_m3_per_hr: Decimal


def calculate_cooling_duty(
    gas_mass_flow_kg_per_s: Decimal,
    gas_specific_heat_kj_per_kg_k: Decimal,
    gas_inlet_temperature_k: Decimal,
    gas_outlet_temperature_k: Decimal,
    cooling_water_inlet_temperature_k: Decimal,
    cooling_water_outlet_temperature_k: Decimal,
) -> CoolingResult:
    """Calculate compressor cooler duty and cooling-water flow."""

    if gas_mass_flow_kg_per_s <= 0:
        raise InvalidCoolingInputError("Gas mass flow must be greater than zero.")

    if gas_specific_heat_kj_per_kg_k <= 0:
        raise InvalidCoolingInputError("Gas specific heat capacity must be greater than zero.")

    if gas_inlet_temperature_k <= gas_outlet_temperature_k:
        raise InvalidCoolingInputError(
            "Gas inlet temperature must be greater than gas outlet temperature."
        )

    if cooling_water_inlet_temperature_k <= 0:
        raise InvalidCoolingInputError("Cooling-water inlet temperature must be greater than zero.")

    if cooling_water_outlet_temperature_k <= cooling_water_inlet_temperature_k:
        raise InvalidCoolingInputError(
            "Cooling-water outlet temperature must exceed inlet temperature."
        )

    gas_temperature_drop = gas_inlet_temperature_k - gas_outlet_temperature_k

    cooling_duty_kw = gas_mass_flow_kg_per_s * gas_specific_heat_kj_per_kg_k * gas_temperature_drop

    cooling_water_temperature_rise = (
        cooling_water_outlet_temperature_k - cooling_water_inlet_temperature_k
    )

    cooling_water_mass_flow_kg_per_s = cooling_duty_kw / (
        WATER_SPECIFIC_HEAT_KJ_PER_KG_K * cooling_water_temperature_rise
    )

    cooling_water_flow_m3_per_hr = (
        cooling_water_mass_flow_kg_per_s * Decimal("3600") / WATER_DENSITY_KG_PER_M3
    )

    return CoolingResult(
        cooling_duty_kw=cooling_duty_kw,
        cooling_water_mass_flow_kg_per_s=cooling_water_mass_flow_kg_per_s,
        cooling_water_flow_m3_per_hr=cooling_water_flow_m3_per_hr,
    )
