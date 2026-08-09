from dataclasses import dataclass
from decimal import Decimal, localcontext

from app.domain.gas.reduced_properties import ReducedProperties


class InvalidReducedPropertyError(ValueError):
    """Raised when reduced properties are invalid for Z-factor calculation."""


@dataclass(frozen=True, slots=True)
class ZFactorResult:
    """Compressibility-factor calculation result."""

    z_factor: Decimal
    correlation: str


def calculate_papay_z_factor(
    reduced: ReducedProperties,
) -> ZFactorResult:
    """Calculate gas compressibility factor using the Papay correlation."""

    pr = reduced.reduced_pressure
    tr = reduced.reduced_temperature

    if pr <= 0:
        raise InvalidReducedPropertyError("Reduced pressure must be greater than zero.")

    if tr <= 0:
        raise InvalidReducedPropertyError("Reduced temperature must be greater than zero.")

    with localcontext() as context:
        context.prec = 28

        ten = Decimal("10")

        first_denominator = ten ** (Decimal("0.9813") * tr)
        second_denominator = ten ** (Decimal("0.8157") * tr)

        first_term = Decimal("3.52") * pr / first_denominator
        second_term = Decimal("0.274") * pr * pr / second_denominator

        z_factor = Decimal("1") - first_term + second_term

    if z_factor <= 0:
        raise InvalidReducedPropertyError("Calculated Z-factor must be greater than zero.")

    return ZFactorResult(
        z_factor=z_factor,
        correlation="Papay",
    )
