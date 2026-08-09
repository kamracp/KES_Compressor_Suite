from dataclasses import dataclass
from decimal import Decimal

from app.domain.gas.pseudocritical import PseudoCriticalProperties


class InvalidOperatingConditionError(ValueError):
    """Raised when operating conditions are invalid for reduced-property calculations."""


@dataclass(frozen=True, slots=True)
class ReducedProperties:
    """Reduced pressure and reduced temperature."""

    reduced_pressure: Decimal
    reduced_temperature: Decimal


def calculate_reduced_properties(
    pressure_bar: Decimal,
    temperature_k: Decimal,
    pseudocritical: PseudoCriticalProperties,
) -> ReducedProperties:
    """Calculate reduced pressure and reduced temperature."""

    if pressure_bar <= 0:
        raise InvalidOperatingConditionError("Absolute pressure must be greater than zero.")

    if temperature_k <= 0:
        raise InvalidOperatingConditionError("Absolute temperature must be greater than zero.")

    if pseudocritical.pressure_bar <= 0:
        raise InvalidOperatingConditionError("Pseudo-critical pressure must be greater than zero.")

    if pseudocritical.temperature_k <= 0:
        raise InvalidOperatingConditionError(
            "Pseudo-critical temperature must be greater than zero."
        )

    reduced_pressure = pressure_bar / pseudocritical.pressure_bar
    reduced_temperature = temperature_k / pseudocritical.temperature_k

    return ReducedProperties(
        reduced_pressure=reduced_pressure,
        reduced_temperature=reduced_temperature,
    )
