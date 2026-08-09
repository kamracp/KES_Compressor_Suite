from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING


class InvalidCapacityInputError(ValueError):
    """Raised when reciprocating capacity inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReciprocatingCapacitySizingResult:
    """Reciprocating compressor capacity sizing result."""

    required_flow_m3_per_hr: Decimal
    delivered_flow_per_cylinder_m3_per_hr: Decimal
    required_cylinders: int
    installed_capacity_m3_per_hr: Decimal
    capacity_margin_m3_per_hr: Decimal
    capacity_margin_fraction: Decimal
    capacity_is_adequate: bool


def calculate_required_cylinders(
    required_flow_m3_per_hr: Decimal,
    delivered_flow_per_cylinder_m3_per_hr: Decimal,
) -> ReciprocatingCapacitySizingResult:
    """Calculate minimum cylinder count required to satisfy compressor capacity."""

    if required_flow_m3_per_hr <= 0:
        raise InvalidCapacityInputError("Required flow must be greater than zero.")

    if delivered_flow_per_cylinder_m3_per_hr <= 0:
        raise InvalidCapacityInputError("Delivered flow per cylinder must be greater than zero.")

    cylinder_ratio = required_flow_m3_per_hr / delivered_flow_per_cylinder_m3_per_hr

    required_cylinders = int(cylinder_ratio.to_integral_value(rounding=ROUND_CEILING))

    installed_capacity_m3_per_hr = delivered_flow_per_cylinder_m3_per_hr * Decimal(
        required_cylinders
    )

    capacity_margin_m3_per_hr = installed_capacity_m3_per_hr - required_flow_m3_per_hr

    capacity_margin_fraction = capacity_margin_m3_per_hr / required_flow_m3_per_hr

    capacity_is_adequate = installed_capacity_m3_per_hr >= required_flow_m3_per_hr

    return ReciprocatingCapacitySizingResult(
        required_flow_m3_per_hr=required_flow_m3_per_hr,
        delivered_flow_per_cylinder_m3_per_hr=delivered_flow_per_cylinder_m3_per_hr,
        required_cylinders=required_cylinders,
        installed_capacity_m3_per_hr=installed_capacity_m3_per_hr,
        capacity_margin_m3_per_hr=capacity_margin_m3_per_hr,
        capacity_margin_fraction=capacity_margin_fraction,
        capacity_is_adequate=capacity_is_adequate,
    )
