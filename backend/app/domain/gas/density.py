from dataclasses import dataclass
from decimal import Decimal, localcontext

UNIVERSAL_GAS_CONSTANT_J_PER_KMOL_K = Decimal("8314.462618")
BAR_TO_PA = Decimal("100000")


class InvalidDensityInputError(ValueError):
    """Raised when inputs are invalid for gas-density calculation."""


@dataclass(frozen=True, slots=True)
class GasDensityResult:
    """Calculated real-gas density."""

    density_kg_per_m3: Decimal


def calculate_real_gas_density(
    pressure_bar: Decimal,
    temperature_k: Decimal,
    molecular_weight_kg_per_kmol: Decimal,
    z_factor: Decimal,
) -> GasDensityResult:
    """Calculate real-gas density from the real-gas equation of state."""

    if pressure_bar <= 0:
        raise InvalidDensityInputError("Absolute pressure must be greater than zero.")

    if temperature_k <= 0:
        raise InvalidDensityInputError("Absolute temperature must be greater than zero.")

    if molecular_weight_kg_per_kmol <= 0:
        raise InvalidDensityInputError("Molecular weight must be greater than zero.")

    if z_factor <= 0:
        raise InvalidDensityInputError("Z-factor must be greater than zero.")

    with localcontext() as context:
        context.prec = 28

        pressure_pa = pressure_bar * BAR_TO_PA

        density = (
            pressure_pa
            * molecular_weight_kg_per_kmol
            / (z_factor * UNIVERSAL_GAS_CONSTANT_J_PER_KMOL_K * temperature_k)
        )

    return GasDensityResult(
        density_kg_per_m3=density,
    )
