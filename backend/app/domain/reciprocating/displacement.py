from decimal import Decimal, localcontext

from app.domain.reciprocating.recip_models import (
    CylinderAction,
    ReciprocatingCylinderGeometry,
    ReciprocatingDisplacementResult,
)

MM_TO_M = Decimal("0.001")
MINUTES_PER_HOUR = Decimal("60")


class InvalidReciprocatingGeometryError(ValueError):
    """Raised when reciprocating compressor geometry is invalid."""


def calculate_displacement(
    geometry: ReciprocatingCylinderGeometry,
) -> ReciprocatingDisplacementResult:
    """Calculate swept displacement for a reciprocating compressor cylinder."""

    if geometry.bore_mm <= 0:
        raise InvalidReciprocatingGeometryError("Cylinder bore must be greater than zero.")

    if geometry.stroke_mm <= 0:
        raise InvalidReciprocatingGeometryError("Stroke length must be greater than zero.")

    if geometry.rod_diameter_mm < 0:
        raise InvalidReciprocatingGeometryError("Rod diameter cannot be negative.")

    if geometry.rod_diameter_mm >= geometry.bore_mm:
        raise InvalidReciprocatingGeometryError("Rod diameter must be smaller than cylinder bore.")

    if geometry.speed_rpm <= 0:
        raise InvalidReciprocatingGeometryError("Compressor speed must be greater than zero.")

    with localcontext() as context:
        context.prec = 28

        pi = Decimal("3.141592653589793238462643383")

        bore_m = geometry.bore_mm * MM_TO_M
        stroke_m = geometry.stroke_mm * MM_TO_M
        rod_diameter_m = geometry.rod_diameter_mm * MM_TO_M

        piston_area_m2 = pi * bore_m * bore_m / Decimal("4")
        rod_area_m2 = pi * rod_diameter_m * rod_diameter_m / Decimal("4")

        head_end_displacement_m3_per_min = piston_area_m2 * stroke_m * geometry.speed_rpm

        if geometry.action == CylinderAction.DOUBLE_ACTING:
            crank_end_area_m2 = piston_area_m2 - rod_area_m2

            crank_end_displacement_m3_per_min = crank_end_area_m2 * stroke_m * geometry.speed_rpm
        else:
            crank_end_displacement_m3_per_min = Decimal("0")

        total_displacement_m3_per_min = (
            head_end_displacement_m3_per_min + crank_end_displacement_m3_per_min
        )

        total_displacement_m3_per_hr = total_displacement_m3_per_min * MINUTES_PER_HOUR

    return ReciprocatingDisplacementResult(
        piston_area_m2=piston_area_m2,
        rod_area_m2=rod_area_m2,
        head_end_displacement_m3_per_min=head_end_displacement_m3_per_min,
        crank_end_displacement_m3_per_min=crank_end_displacement_m3_per_min,
        total_displacement_m3_per_min=total_displacement_m3_per_min,
        total_displacement_m3_per_hr=total_displacement_m3_per_hr,
    )
