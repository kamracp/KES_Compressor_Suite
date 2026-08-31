from decimal import Decimal

from app.domain.rotary_screw.models import RotaryScrewPerformanceResult


class InvalidPerformanceInputError(ValueError):
    """Raised when rotary screw performance verification inputs are invalid."""


def verify_manufacturer_performance(
    rated_fad_m3_per_min: Decimal,
    package_input_power_kw: Decimal,
) -> RotaryScrewPerformanceResult:
    """Compute specific power from manufacturer-supplied, CAGI-tested data.

    This function performs no estimation or prediction: it takes the rated
    free air delivery and package input power exactly as published on a
    manufacturer's CAGI-verified datasheet (tested to ISO 1217 Annex C) and
    computes specific power as their ratio. It does not benchmark the result
    against an industry-typical range, since no numeric range has been
    verified against a primary CAGI publication for this codebase; that
    remains a documented follow-up rather than an assumed constant.
    """

    if rated_fad_m3_per_min <= 0:
        raise InvalidPerformanceInputError("Rated FAD must be greater than zero.")

    if package_input_power_kw <= 0:
        raise InvalidPerformanceInputError("Package input power must be greater than zero.")

    specific_power = package_input_power_kw / rated_fad_m3_per_min

    return RotaryScrewPerformanceResult(
        rated_fad_m3_per_min=rated_fad_m3_per_min,
        package_input_power_kw=package_input_power_kw,
        specific_power_kw_per_m3_min=specific_power,
    )
