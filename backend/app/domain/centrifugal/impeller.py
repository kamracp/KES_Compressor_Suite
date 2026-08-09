from decimal import Decimal

from app.domain.centrifugal.centrifugal_models import ImpellerSizingResult


class InvalidImpellerInputError(ValueError):
    """Raised when centrifugal impeller inputs are invalid."""


def calculate_impeller_sizing(
    total_polytropic_head_kj_per_kg: Decimal,
    number_of_impeller_stages: int,
    head_coefficient: Decimal,
    rotational_speed_rpm: Decimal,
) -> ImpellerSizingResult:
    """Calculate centrifugal compressor impeller sizing."""

    if total_polytropic_head_kj_per_kg <= 0:
        raise InvalidImpellerInputError("Total polytropic head must be greater than zero.")

    if number_of_impeller_stages < 1:
        raise InvalidImpellerInputError("Number of impeller stages must be at least one.")

    if head_coefficient <= 0:
        raise InvalidImpellerInputError("Head coefficient must be greater than zero.")

    if rotational_speed_rpm <= 0:
        raise InvalidImpellerInputError("Rotational speed must be greater than zero.")

    head_per_stage_kj_per_kg = total_polytropic_head_kj_per_kg / Decimal(number_of_impeller_stages)

    head_per_stage_j_per_kg = head_per_stage_kj_per_kg * Decimal("1000")

    impeller_tip_speed_m_per_s = Decimal(
        str((float(head_per_stage_j_per_kg) / float(head_coefficient)) ** 0.5)
    )

    pi = Decimal("3.141592653589793238462643383")

    impeller_diameter_m = Decimal("60") * impeller_tip_speed_m_per_s / (pi * rotational_speed_rpm)

    return ImpellerSizingResult(
        number_of_impeller_stages=number_of_impeller_stages,
        head_per_stage_kj_per_kg=head_per_stage_kj_per_kg,
        head_coefficient=head_coefficient,
        impeller_tip_speed_m_per_s=impeller_tip_speed_m_per_s,
        rotational_speed_rpm=rotational_speed_rpm,
        impeller_diameter_m=impeller_diameter_m,
    )
