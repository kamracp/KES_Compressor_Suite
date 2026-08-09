from dataclasses import dataclass
from decimal import Decimal, localcontext

SECONDS_PER_HOUR = Decimal("3600")


class InvalidFlowInputError(ValueError):
    """Raised when flow-conversion inputs are invalid."""


@dataclass(frozen=True, slots=True)
class GasFlowResult:
    """Calculated gas-flow quantities."""

    actual_flow_m3_per_hr: Decimal
    actual_flow_m3_per_s: Decimal
    mass_flow_kg_per_hr: Decimal
    mass_flow_kg_per_s: Decimal


def calculate_actual_flow(
    standard_flow_m3_per_hr: Decimal,
    standard_pressure_bar: Decimal,
    standard_temperature_k: Decimal,
    actual_pressure_bar: Decimal,
    actual_temperature_k: Decimal,
    actual_z_factor: Decimal,
    standard_z_factor: Decimal = Decimal("1"),
) -> Decimal:
    """Convert standard volumetric flow to actual volumetric flow."""

    values = {
        "Standard flow": standard_flow_m3_per_hr,
        "Standard pressure": standard_pressure_bar,
        "Standard temperature": standard_temperature_k,
        "Actual pressure": actual_pressure_bar,
        "Actual temperature": actual_temperature_k,
        "Actual Z-factor": actual_z_factor,
        "Standard Z-factor": standard_z_factor,
    }

    for name, value in values.items():
        if value <= 0:
            raise InvalidFlowInputError(f"{name} must be greater than zero.")

    with localcontext() as context:
        context.prec = 28

        actual_flow = (
            standard_flow_m3_per_hr
            * (standard_pressure_bar / actual_pressure_bar)
            * (actual_temperature_k / standard_temperature_k)
            * (actual_z_factor / standard_z_factor)
        )

    return actual_flow


def calculate_flow_result(
    standard_flow_m3_per_hr: Decimal,
    standard_pressure_bar: Decimal,
    standard_temperature_k: Decimal,
    actual_pressure_bar: Decimal,
    actual_temperature_k: Decimal,
    actual_z_factor: Decimal,
    density_kg_per_m3: Decimal,
    standard_z_factor: Decimal = Decimal("1"),
) -> GasFlowResult:
    """Calculate actual volumetric flow and mass flow."""

    if density_kg_per_m3 <= 0:
        raise InvalidFlowInputError("Gas density must be greater than zero.")

    actual_flow_m3_per_hr = calculate_actual_flow(
        standard_flow_m3_per_hr=standard_flow_m3_per_hr,
        standard_pressure_bar=standard_pressure_bar,
        standard_temperature_k=standard_temperature_k,
        actual_pressure_bar=actual_pressure_bar,
        actual_temperature_k=actual_temperature_k,
        actual_z_factor=actual_z_factor,
        standard_z_factor=standard_z_factor,
    )

    actual_flow_m3_per_s = actual_flow_m3_per_hr / SECONDS_PER_HOUR
    mass_flow_kg_per_hr = actual_flow_m3_per_hr * density_kg_per_m3
    mass_flow_kg_per_s = mass_flow_kg_per_hr / SECONDS_PER_HOUR

    return GasFlowResult(
        actual_flow_m3_per_hr=actual_flow_m3_per_hr,
        actual_flow_m3_per_s=actual_flow_m3_per_s,
        mass_flow_kg_per_hr=mass_flow_kg_per_hr,
        mass_flow_kg_per_s=mass_flow_kg_per_s,
    )
