from dataclasses import dataclass
from decimal import Decimal

from app.domain.gas.gas_catalog import get_gas_component
from app.domain.gas.gas_models import GasMixture
from app.domain.gas.gas_properties import validate_gas_mixture


class MissingCriticalPropertyError(ValueError):
    """Raised when critical-property data is unavailable for a component."""


@dataclass(frozen=True, slots=True)
class PseudoCriticalProperties:
    """Pseudo-critical properties of a gas mixture."""

    temperature_k: Decimal
    pressure_bar: Decimal


def calculate_pseudocritical_properties(
    mixture: GasMixture,
) -> PseudoCriticalProperties:
    """Calculate pseudo-critical properties using Kay's mixing rule."""

    validate_gas_mixture(mixture)

    temperature_k = Decimal("0")
    pressure_bar = Decimal("0")

    for component in mixture.components:
        reference = get_gas_component(component.name)

        if reference.critical_temperature_k is None:
            raise MissingCriticalPropertyError(
                f"Critical temperature is unavailable for component '{component.name}'."
            )

        if reference.critical_pressure_bar is None:
            raise MissingCriticalPropertyError(
                f"Critical pressure is unavailable for component '{component.name}'."
            )

        temperature_k += component.mole_fraction * reference.critical_temperature_k
        pressure_bar += component.mole_fraction * reference.critical_pressure_bar

    return PseudoCriticalProperties(
        temperature_k=temperature_k,
        pressure_bar=pressure_bar,
    )
