from decimal import Decimal

from app.domain.rotary_screw.models import (
    RotaryScrewDisplacementResult,
    RotaryScrewRotorGeometry,
)


class InvalidRotaryScrewGeometryError(ValueError):
    """Raised when rotary screw rotor geometry inputs are invalid."""


def calculate_theoretical_displacement(
    geometry: RotaryScrewRotorGeometry,
    rotational_speed_rpm: Decimal,
) -> RotaryScrewDisplacementResult:
    """Calculate theoretical (ideal) rotor displacement, API 619 convention.

    Theoretical displacement per male-rotor revolution is the rotor-profile
    area-utilisation coefficient times the male rotor diameter squared times
    the rotor length (V_th = C-theta * D^2 * L). Multiplying by rotational
    speed gives theoretical volumetric flow, before any volumetric-efficiency
    loss is applied.

    ``geometry.area_utilisation_coefficient`` must come from the
    manufacturer's published rotor-profile data or a documented textbook
    range -- it is not assumed by this function.
    """

    if geometry.male_rotor_diameter_mm <= 0:
        raise InvalidRotaryScrewGeometryError("Male rotor diameter must be greater than zero.")

    if geometry.rotor_length_mm <= 0:
        raise InvalidRotaryScrewGeometryError("Rotor length must be greater than zero.")

    if geometry.area_utilisation_coefficient <= 0:
        raise InvalidRotaryScrewGeometryError(
            "Rotor area utilisation coefficient must be greater than zero."
        )

    if rotational_speed_rpm <= 0:
        raise InvalidRotaryScrewGeometryError("Rotational speed must be greater than zero.")

    diameter_m = geometry.male_rotor_diameter_mm / Decimal("1000")
    length_m = geometry.rotor_length_mm / Decimal("1000")

    displacement_per_rev_m3 = (
        geometry.area_utilisation_coefficient * diameter_m * diameter_m * length_m
    )

    theoretical_displacement_m3_per_min = displacement_per_rev_m3 * rotational_speed_rpm

    return RotaryScrewDisplacementResult(
        theoretical_displacement_m3_per_min=theoretical_displacement_m3_per_min,
    )
