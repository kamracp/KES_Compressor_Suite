from decimal import Decimal

from app.domain.selection.selection_models import (
    CompressorOptionAssessment,
    CompressorSelectionCriteria,
    CompressorSelectionResult,
    CompressorType,
    SelectionRating,
)


class InvalidSelectionInputError(ValueError):
    """Raised when compressor selection inputs are invalid."""


RATING_SCORE = {
    SelectionRating.EXCELLENT: Decimal("4"),
    SelectionRating.GOOD: Decimal("3"),
    SelectionRating.ACCEPTABLE: Decimal("2"),
    SelectionRating.POOR: Decimal("1"),
}


def _validate_criteria(criteria: CompressorSelectionCriteria) -> None:
    """Validate compressor selection criteria."""

    if criteria.required_flow_m3_per_hr <= 0:
        raise InvalidSelectionInputError("Required flow must be greater than zero.")

    if criteria.suction_pressure_bar <= 0:
        raise InvalidSelectionInputError("Suction absolute pressure must be greater than zero.")

    if criteria.discharge_pressure_bar <= criteria.suction_pressure_bar:
        raise InvalidSelectionInputError(
            "Discharge pressure must be greater than suction pressure."
        )

    if criteria.required_turndown_fraction <= 0 or criteria.required_turndown_fraction > 1:
        raise InvalidSelectionInputError(
            "Required turndown fraction must be greater than zero and not exceed one."
        )

    if criteria.gas_molecular_weight <= 0:
        raise InvalidSelectionInputError("Gas molecular weight must be greater than zero.")

    if criteria.estimated_operating_hours_per_year < 0:
        raise InvalidSelectionInputError("Annual operating hours cannot be negative.")


def _score_assessment(
    ratings: tuple[SelectionRating, ...],
) -> Decimal:
    """Calculate normalized compressor assessment score."""

    total = sum(
        (RATING_SCORE[rating] for rating in ratings),
        start=Decimal("0"),
    )

    maximum = Decimal(len(ratings)) * Decimal("4")

    return total / maximum * Decimal("100")


def _assess_reciprocating(
    criteria: CompressorSelectionCriteria,
) -> CompressorOptionAssessment:
    """Assess reciprocating compressor suitability."""

    overall_ratio = criteria.discharge_pressure_bar / criteria.suction_pressure_bar

    rationale: list[str] = []

    if criteria.required_flow_m3_per_hr <= Decimal("10000"):
        capacity_rating = SelectionRating.EXCELLENT
        rationale.append("Required flow is well suited to positive-displacement compression.")
    elif criteria.required_flow_m3_per_hr <= Decimal("30000"):
        capacity_rating = SelectionRating.GOOD
        rationale.append("Required flow is feasible with multiple cylinders or compressor frames.")
    else:
        capacity_rating = SelectionRating.ACCEPTABLE
        rationale.append("High flow may require multiple cylinders, frames, or parallel machines.")

    if overall_ratio >= Decimal("4"):
        pressure_ratio_rating = SelectionRating.EXCELLENT
        rationale.append("Reciprocating compression is well suited to high pressure ratios.")
    elif overall_ratio >= Decimal("2"):
        pressure_ratio_rating = SelectionRating.GOOD
        rationale.append("Pressure ratio is suitable for staged reciprocating compression.")
    else:
        pressure_ratio_rating = SelectionRating.ACCEPTABLE
        rationale.append("Low pressure ratio does not strongly favor reciprocating compression.")

    if criteria.required_turndown_fraction <= Decimal("0.50"):
        turndown_rating = SelectionRating.EXCELLENT
        rationale.append("Wide turndown requirement favors reciprocating capacity control.")
    elif criteria.required_turndown_fraction <= Decimal("0.75"):
        turndown_rating = SelectionRating.GOOD
        rationale.append("Required turndown is compatible with reciprocating control methods.")
    else:
        turndown_rating = SelectionRating.ACCEPTABLE

    efficiency_rating = SelectionRating.GOOD

    if criteria.continuous_operation:
        maintenance_rating = SelectionRating.ACCEPTABLE
        rationale.append(
            "Continuous-duty reciprocating service requires higher maintenance attention."
        )
    else:
        maintenance_rating = SelectionRating.GOOD

    ratings = (
        capacity_rating,
        pressure_ratio_rating,
        turndown_rating,
        efficiency_rating,
        maintenance_rating,
    )

    return CompressorOptionAssessment(
        compressor_type=CompressorType.RECIPROCATING,
        capacity_rating=capacity_rating,
        pressure_ratio_rating=pressure_ratio_rating,
        turndown_rating=turndown_rating,
        efficiency_rating=efficiency_rating,
        maintenance_rating=maintenance_rating,
        overall_score=_score_assessment(ratings),
        rationale=tuple(rationale),
    )


def _assess_centrifugal(
    criteria: CompressorSelectionCriteria,
) -> CompressorOptionAssessment:
    """Assess centrifugal compressor suitability."""

    overall_ratio = criteria.discharge_pressure_bar / criteria.suction_pressure_bar

    rationale: list[str] = []

    if criteria.required_flow_m3_per_hr >= Decimal("15000"):
        capacity_rating = SelectionRating.EXCELLENT
        rationale.append("High continuous gas flow favors centrifugal compression.")
    elif criteria.required_flow_m3_per_hr >= Decimal("7000"):
        capacity_rating = SelectionRating.GOOD
        rationale.append("Required flow is within a practical centrifugal compressor range.")
    else:
        capacity_rating = SelectionRating.ACCEPTABLE
        rationale.append("Relatively low flow may reduce centrifugal compressor suitability.")

    if overall_ratio <= Decimal("3"):
        pressure_ratio_rating = SelectionRating.EXCELLENT
        rationale.append("Moderate overall pressure ratio is well suited to centrifugal staging.")
    elif overall_ratio <= Decimal("6"):
        pressure_ratio_rating = SelectionRating.GOOD
        rationale.append("Pressure ratio is feasible with multiple centrifugal stages.")
    else:
        pressure_ratio_rating = SelectionRating.ACCEPTABLE
        rationale.append("High pressure ratio may require multiple sections or casings.")

    if criteria.required_turndown_fraction >= Decimal("0.70"):
        turndown_rating = SelectionRating.GOOD
    elif criteria.required_turndown_fraction >= Decimal("0.50"):
        turndown_rating = SelectionRating.ACCEPTABLE
        rationale.append("Wide turndown may require recycle or variable-speed control.")
    else:
        turndown_rating = SelectionRating.POOR
        rationale.append("Very wide turndown can be difficult without significant recycle.")

    if criteria.continuous_operation:
        efficiency_rating = SelectionRating.EXCELLENT
        maintenance_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Continuous high-utilization duty favors centrifugal compressor operation."
        )
    else:
        efficiency_rating = SelectionRating.GOOD
        maintenance_rating = SelectionRating.GOOD

    ratings = (
        capacity_rating,
        pressure_ratio_rating,
        turndown_rating,
        efficiency_rating,
        maintenance_rating,
    )

    return CompressorOptionAssessment(
        compressor_type=CompressorType.CENTRIFUGAL,
        capacity_rating=capacity_rating,
        pressure_ratio_rating=pressure_ratio_rating,
        turndown_rating=turndown_rating,
        efficiency_rating=efficiency_rating,
        maintenance_rating=maintenance_rating,
        overall_score=_score_assessment(ratings),
        rationale=tuple(rationale),
    )


def select_compressor_type(
    criteria: CompressorSelectionCriteria,
) -> CompressorSelectionResult:
    """Compare reciprocating and centrifugal compressor suitability."""

    _validate_criteria(criteria)

    reciprocating = _assess_reciprocating(criteria)
    centrifugal = _assess_centrifugal(criteria)

    if reciprocating.overall_score >= centrifugal.overall_score:
        recommended_type = CompressorType.RECIPROCATING
        recommendation_summary = (
            "Reciprocating compressor has the higher suitability score for the "
            "specified operating criteria."
        )
    else:
        recommended_type = CompressorType.CENTRIFUGAL
        recommendation_summary = (
            "Centrifugal compressor has the higher suitability score for the "
            "specified operating criteria."
        )

    score_difference = abs(reciprocating.overall_score - centrifugal.overall_score)

    return CompressorSelectionResult(
        recommended_type=recommended_type,
        reciprocating=reciprocating,
        centrifugal=centrifugal,
        score_difference=score_difference,
        recommendation_summary=recommendation_summary,
    )
