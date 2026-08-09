from dataclasses import dataclass
from decimal import Decimal

from app.domain.gas.gas_models import GasMixture

AIR_MOLECULAR_WEIGHT = Decimal("28.96546")
MOLE_FRACTION_TOLERANCE = Decimal("0.000001")


class InvalidGasMixtureError(ValueError):
    """Raised when a gas mixture is invalid for property calculations."""


@dataclass(frozen=True, slots=True)
class GasMixtureProperties:
    """Calculated bulk properties of a gas mixture."""

    molecular_weight: Decimal
    specific_gravity: Decimal


def validate_gas_mixture(mixture: GasMixture) -> None:
    """Validate a gas mixture before engineering calculations."""

    if not mixture.components:
        raise InvalidGasMixtureError("Gas mixture must contain at least one component.")

    for component in mixture.components:
        if component.molecular_weight <= 0:
            raise InvalidGasMixtureError(
                f"Molecular weight must be positive for component '{component.name}'."
            )

        if component.mole_fraction < 0:
            raise InvalidGasMixtureError(
                f"Mole fraction cannot be negative for component '{component.name}'."
            )

    deviation = abs(mixture.total_mole_fraction - Decimal("1"))

    if deviation > MOLE_FRACTION_TOLERANCE:
        raise InvalidGasMixtureError("Gas mixture mole fractions must sum to 1.0.")


def calculate_mixture_properties(
    mixture: GasMixture,
) -> GasMixtureProperties:
    """Calculate molecular weight and gas specific gravity."""

    validate_gas_mixture(mixture)

    molecular_weight = mixture.molecular_weight
    specific_gravity = molecular_weight / AIR_MOLECULAR_WEIGHT

    return GasMixtureProperties(
        molecular_weight=molecular_weight,
        specific_gravity=specific_gravity,
    )
