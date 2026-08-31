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

    if criteria.oil_free_air_required:
        air_quality_rating = SelectionRating.ACCEPTABLE
        rationale.append(
            "Non-lubricated reciprocating designs can meet oil-free duty but with "
            "reduced ring life relative to standard lubricated machines."
        )
    else:
        air_quality_rating = SelectionRating.GOOD

    if criteria.required_turndown_fraction <= Decimal("0.50"):
        lifecycle_energy_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Step/unloader capacity control tracks part-load duty efficiently over a "
            "wide turndown range."
        )
    else:
        lifecycle_energy_rating = SelectionRating.GOOD

    ratings = (
        capacity_rating,
        pressure_ratio_rating,
        turndown_rating,
        efficiency_rating,
        maintenance_rating,
        air_quality_rating,
        lifecycle_energy_rating,
    )

    return CompressorOptionAssessment(
        compressor_type=CompressorType.RECIPROCATING,
        capacity_rating=capacity_rating,
        pressure_ratio_rating=pressure_ratio_rating,
        turndown_rating=turndown_rating,
        efficiency_rating=efficiency_rating,
        maintenance_rating=maintenance_rating,
        air_quality_rating=air_quality_rating,
        lifecycle_energy_rating=lifecycle_energy_rating,
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

    air_quality_rating = SelectionRating.EXCELLENT
    rationale.append(
        "Centrifugal compressors are inherently oil-free in the gas path, since "
        "lubricated bearings and seals are isolated from the process gas."
    )

    if criteria.required_turndown_fraction >= Decimal("0.70"):
        lifecycle_energy_rating = SelectionRating.GOOD
        rationale.append(
            "Narrow required turndown keeps operation near the efficient design point."
        )
    else:
        lifecycle_energy_rating = SelectionRating.POOR
        rationale.append(
            "Wide turndown against a centrifugal machine is typically met with "
            "recycle or blow-off, wasting compression energy at part load."
        )

    ratings = (
        capacity_rating,
        pressure_ratio_rating,
        turndown_rating,
        efficiency_rating,
        maintenance_rating,
        air_quality_rating,
        lifecycle_energy_rating,
    )

    return CompressorOptionAssessment(
        compressor_type=CompressorType.CENTRIFUGAL,
        capacity_rating=capacity_rating,
        pressure_ratio_rating=pressure_ratio_rating,
        turndown_rating=turndown_rating,
        efficiency_rating=efficiency_rating,
        maintenance_rating=maintenance_rating,
        air_quality_rating=air_quality_rating,
        lifecycle_energy_rating=lifecycle_energy_rating,
        overall_score=_score_assessment(ratings),
        rationale=tuple(rationale),
    )


def _assess_rotary_screw(
    criteria: CompressorSelectionCriteria,
) -> CompressorOptionAssessment:
    """Assess rotary screw compressor suitability.

    Rotary screw compressors dominate small-to-medium industrial
    compressed-air and gas duty at low-to-moderate pressure ratios, offer
    strong turndown (particularly with variable-speed drive), and have
    fewer wearing parts than reciprocating machines since they carry no
    suction/discharge valves or piston rings.
    """

    overall_ratio = criteria.discharge_pressure_bar / criteria.suction_pressure_bar

    rationale: list[str] = []

    if criteria.required_flow_m3_per_hr <= Decimal("8000"):
        capacity_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Required flow is well within a single-package rotary screw compressor range."
        )
    elif criteria.required_flow_m3_per_hr <= Decimal("20000"):
        capacity_rating = SelectionRating.GOOD
        rationale.append(
            "Required flow is feasible with a larger package or multiple parallel "
            "screw compressors."
        )
    else:
        capacity_rating = SelectionRating.ACCEPTABLE
        rationale.append("Very high flow is more typically served by centrifugal compression.")

    if overall_ratio <= Decimal("4"):
        pressure_ratio_rating = SelectionRating.EXCELLENT
        rationale.append("Pressure ratio is typical of standard single-stage rotary screw duty.")
    elif overall_ratio <= Decimal("8"):
        pressure_ratio_rating = SelectionRating.GOOD
        rationale.append("Pressure ratio is feasible with a two-stage rotary screw package.")
    else:
        pressure_ratio_rating = SelectionRating.ACCEPTABLE
        rationale.append("Very high pressure ratio is uncommon for standard rotary screw packages.")

    if criteria.required_turndown_fraction <= Decimal("0.60"):
        turndown_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Wide turndown is well matched to variable-speed-drive rotary screw control."
        )
    else:
        turndown_rating = SelectionRating.GOOD

    efficiency_rating = SelectionRating.GOOD

    maintenance_rating = SelectionRating.EXCELLENT
    rationale.append(
        "Rotary screw compressors have no suction/discharge valves or piston rings, "
        "reducing wearing-part maintenance relative to reciprocating machines."
    )

    if criteria.oil_free_air_required:
        air_quality_rating = SelectionRating.GOOD
        rationale.append(
            "Oil-free (dry) rotary screw packages are a mature, widely available "
            "technology for oil-free air-quality duty."
        )
    else:
        air_quality_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Standard oil-injected rotary screw is the most common and lowest-cost "
            "configuration where oil-free air is not required."
        )

    if criteria.required_turndown_fraction <= Decimal("0.60"):
        lifecycle_energy_rating = SelectionRating.EXCELLENT
        rationale.append(
            "Variable-speed-drive rotary screw control tracks part-load duty with "
            "minimal energy penalty across a wide turndown range."
        )
    else:
        lifecycle_energy_rating = SelectionRating.GOOD

    ratings = (
        capacity_rating,
        pressure_ratio_rating,
        turndown_rating,
        efficiency_rating,
        maintenance_rating,
        air_quality_rating,
        lifecycle_energy_rating,
    )

    return CompressorOptionAssessment(
        compressor_type=CompressorType.ROTARY_SCREW,
        capacity_rating=capacity_rating,
        pressure_ratio_rating=pressure_ratio_rating,
        turndown_rating=turndown_rating,
        efficiency_rating=efficiency_rating,
        maintenance_rating=maintenance_rating,
        air_quality_rating=air_quality_rating,
        lifecycle_energy_rating=lifecycle_energy_rating,
        overall_score=_score_assessment(ratings),
        rationale=tuple(rationale),
    )


def select_compressor_type(
    criteria: CompressorSelectionCriteria,
) -> CompressorSelectionResult:
    """Compare reciprocating, centrifugal, and rotary screw compressor suitability."""

    _validate_criteria(criteria)

    reciprocating = _assess_reciprocating(criteria)
    centrifugal = _assess_centrifugal(criteria)
    rotary_screw = _assess_rotary_screw(criteria)

    assessments = (reciprocating, centrifugal, rotary_screw)
    best_assessment = max(assessments, key=lambda assessment: assessment.overall_score)
    recommended_type = best_assessment.compressor_type

    recommendation_summary = (
        f"{recommended_type.value.replace('_', ' ').title()} compressor has the "
        "highest suitability score among the evaluated technologies for the "
        "specified operating criteria."
    )

    scores = tuple(assessment.overall_score for assessment in assessments)
    score_difference = max(scores) - min(scores)

    return CompressorSelectionResult(
        recommended_type=recommended_type,
        reciprocating=reciprocating,
        centrifugal=centrifugal,
        rotary_screw=rotary_screw,
        score_difference=score_difference,
        recommendation_summary=recommendation_summary,
    )
