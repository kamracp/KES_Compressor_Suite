from decimal import Decimal

from app.domain.rotary_screw.models import RotaryScrewStandardAirCorrectionResult


class InvalidStandardAirCorrectionInputError(ValueError):
    """Raised when standard-air correction inputs are invalid."""


def correct_fad_to_standard_air(
    rated_fad_m3_per_min: Decimal,
    reference_pressure_bar_a: Decimal,
    reference_temperature_k: Decimal,
    site_inlet_pressure_bar_a: Decimal,
    site_inlet_temperature_k: Decimal,
) -> RotaryScrewStandardAirCorrectionResult:
    """Correct a rated free-air-delivery figure to actual site inlet conditions.

    A positive-displacement compressor delivers an approximately constant
    volumetric flow referred to its own inlet (fixed geometry, fixed speed),
    but the equivalent quantity of standard air this represents changes with
    site altitude, temperature, and pressure, because air density changes
    with those conditions (ideal gas law: density is proportional to P/T).

    This applies the standard density-ratio correction used industry-wide
    for compressed-air equipment (see, for example, CAGI / Compressed Air
    Challenge reference material). The precise ISO 1217 clause wording has
    not been verified against an authorised copy of the standard; treat this
    as the well-established ideal-gas correction, not a verbatim
    reproduction of a specific standard's clause text.
    """

    if rated_fad_m3_per_min <= 0:
        raise InvalidStandardAirCorrectionInputError("Rated FAD must be greater than zero.")
    if reference_pressure_bar_a <= 0 or site_inlet_pressure_bar_a <= 0:
        raise InvalidStandardAirCorrectionInputError(
            "Pressures must be absolute and greater than zero."
        )
    if reference_temperature_k <= 0 or site_inlet_temperature_k <= 0:
        raise InvalidStandardAirCorrectionInputError(
            "Temperatures must be in Kelvin and greater than zero."
        )

    corrected_fad = (
        rated_fad_m3_per_min
        * (site_inlet_pressure_bar_a / reference_pressure_bar_a)
        * (reference_temperature_k / site_inlet_temperature_k)
    )

    return RotaryScrewStandardAirCorrectionResult(
        reference_pressure_bar_a=reference_pressure_bar_a,
        reference_temperature_k=reference_temperature_k,
        corrected_fad_m3_per_min=corrected_fad,
    )
