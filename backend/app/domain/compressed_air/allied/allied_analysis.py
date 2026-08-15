from decimal import Decimal

from app.domain.compressed_air.allied.allied_models import (
    AlliedEquipmentAnalysisInput,
    AlliedEquipmentAnalysisResult,
    EngineeringRecommendation,
    EquipmentAdequacyStatus,
    EquipmentCapacityEvaluation,
    RecommendationSeverity,
    RedundancyPhilosophy,
)
from app.domain.compressed_air.storage.receiver_sizing import (
    calculate_receiver_size,
)
from app.domain.compressed_air.treatment.air_treatment import (
    calculate_air_treatment,
)


class InvalidAlliedEquipmentInputError(ValueError):
    """Raised when allied-equipment engineering inputs are invalid."""


ZERO = Decimal("0")


def analyze_allied_equipment(
    inputs: AlliedEquipmentAnalysisInput,
) -> AlliedEquipmentAnalysisResult:
    """Analyze compressed-air allied equipment as one engineering workflow."""

    _validate_inputs(inputs)

    receiver_result = (
        calculate_receiver_size(inputs.receiver.sizing_input)
        if inputs.receiver is not None
        else None
    )

    treatment_result = (
        calculate_air_treatment(inputs.treatment.sizing_input)
        if inputs.treatment is not None
        else None
    )

    receiver_evaluation = None
    if inputs.receiver is not None and receiver_result is not None:
        receiver_evaluation = _evaluate_capacity(
            equipment_code="AIR_RECEIVER",
            required_capacity=receiver_result.recommended_receiver_volume_m3,
            selected_capacity=(
                inputs.receiver.selected_receiver_volume_m3 * inputs.receiver.receiver_quantity
                if inputs.receiver.selected_receiver_volume_m3 is not None
                else None
            ),
        )

    treatment_evaluation = None
    if inputs.treatment is not None and treatment_result is not None:
        treatment_evaluation = _evaluate_capacity(
            equipment_code="AIR_TREATMENT",
            required_capacity=(treatment_result.recommended_treatment_capacity_nm3_per_hr),
            selected_capacity=(
                inputs.treatment.selected_treatment_capacity_nm3_per_hr
                * inputs.treatment.duty_unit_count
                if inputs.treatment.selected_treatment_capacity_nm3_per_hr is not None
                else None
            ),
        )

    reference_flow_nm3_per_hr = _determine_reference_flow(
        inputs,
        treatment_result,
    )

    aftercooler_evaluation = None
    if inputs.aftercooler is not None:
        aftercooler_evaluation = _evaluate_capacity(
            equipment_code="AFTERCOOLER",
            required_capacity=reference_flow_nm3_per_hr,
            selected_capacity=(inputs.aftercooler.selected_flow_capacity_nm3_per_hr),
        )

    moisture_separator_evaluation = None
    if inputs.moisture_separator is not None:
        moisture_separator_evaluation = _evaluate_capacity(
            equipment_code="MOISTURE_SEPARATOR",
            required_capacity=reference_flow_nm3_per_hr,
            selected_capacity=(inputs.moisture_separator.selected_flow_capacity_nm3_per_hr),
        )

    filter_evaluations = tuple(
        _evaluate_capacity(
            equipment_code=f"FILTER:{stage.stage_code}",
            required_capacity=reference_flow_nm3_per_hr,
            selected_capacity=stage.selected_flow_capacity_nm3_per_hr,
        )
        for stage in inputs.filter_stages
    )

    total_additional_pressure_drop_bar = _calculate_additional_pressure_drop(inputs)

    evaluations = tuple(
        evaluation
        for evaluation in (
            receiver_evaluation,
            treatment_evaluation,
            aftercooler_evaluation,
            moisture_separator_evaluation,
            *filter_evaluations,
        )
        if evaluation is not None
    )

    recommendations = _build_recommendations(
        inputs=inputs,
        evaluations=evaluations,
        treatment_result=treatment_result,
        total_additional_pressure_drop_bar=(total_additional_pressure_drop_bar),
    )

    return AlliedEquipmentAnalysisResult(
        analysis_code=inputs.analysis_code.strip(),
        receiver_result=receiver_result,
        treatment_result=treatment_result,
        receiver_evaluation=receiver_evaluation,
        treatment_evaluation=treatment_evaluation,
        aftercooler_evaluation=aftercooler_evaluation,
        moisture_separator_evaluation=moisture_separator_evaluation,
        filter_evaluations=filter_evaluations,
        total_additional_pressure_drop_bar=(total_additional_pressure_drop_bar),
        recommendations=recommendations,
        notes=inputs.notes,
    )


def _evaluate_capacity(
    *,
    equipment_code: str,
    required_capacity: Decimal,
    selected_capacity: Decimal | None,
) -> EquipmentCapacityEvaluation:
    if required_capacity == ZERO:
        return EquipmentCapacityEvaluation(
            equipment_code=equipment_code,
            required_capacity=required_capacity,
            selected_capacity=selected_capacity,
            capacity_margin=selected_capacity,
            capacity_margin_fraction=None,
            status=EquipmentAdequacyStatus.NOT_REQUIRED,
        )

    if selected_capacity is None:
        return EquipmentCapacityEvaluation(
            equipment_code=equipment_code,
            required_capacity=required_capacity,
            selected_capacity=None,
            capacity_margin=None,
            capacity_margin_fraction=None,
            status=EquipmentAdequacyStatus.NOT_SELECTED,
        )

    capacity_margin = selected_capacity - required_capacity
    capacity_margin_fraction = capacity_margin / required_capacity

    status = (
        EquipmentAdequacyStatus.ADEQUATE
        if selected_capacity >= required_capacity
        else EquipmentAdequacyStatus.UNDERSIZED
    )

    return EquipmentCapacityEvaluation(
        equipment_code=equipment_code,
        required_capacity=required_capacity,
        selected_capacity=selected_capacity,
        capacity_margin=capacity_margin,
        capacity_margin_fraction=capacity_margin_fraction,
        status=status,
    )


def _determine_reference_flow(
    inputs: AlliedEquipmentAnalysisInput,
    treatment_result,
) -> Decimal:
    """Determine physical airflow basis for allied-equipment capacity review."""

    if treatment_result is not None:
        return treatment_result.gross_flow_before_purge_nm3_per_hr

    if inputs.receiver is not None:
        sizing_input = inputs.receiver.sizing_input
        return max(
            sizing_input.peak_demand_nm3_per_hr,
            sizing_input.available_compressor_flow_nm3_per_hr,
        )

    return ZERO


def _calculate_additional_pressure_drop(
    inputs: AlliedEquipmentAnalysisInput,
) -> Decimal:
    """Calculate allied-equipment pressure drop outside the treatment engine."""

    total_pressure_drop = ZERO

    if inputs.aftercooler is not None:
        total_pressure_drop += inputs.aftercooler.pressure_drop_bar

    if inputs.moisture_separator is not None:
        total_pressure_drop += inputs.moisture_separator.pressure_drop_bar

    total_pressure_drop += sum(
        (stage.pressure_drop_bar for stage in inputs.filter_stages),
        start=ZERO,
    )

    return total_pressure_drop


def _build_recommendations(
    *,
    inputs: AlliedEquipmentAnalysisInput,
    evaluations: tuple[EquipmentCapacityEvaluation, ...],
    treatment_result,
    total_additional_pressure_drop_bar: Decimal,
) -> tuple[EngineeringRecommendation, ...]:
    """Build deterministic and traceable engineering recommendations."""

    recommendations: list[EngineeringRecommendation] = []

    for evaluation in evaluations:
        code_suffix = evaluation.equipment_code.replace(":", "_")

        if evaluation.status == EquipmentAdequacyStatus.UNDERSIZED:
            recommendations.append(
                EngineeringRecommendation(
                    recommendation_code=f"{code_suffix}_UNDERSIZED",
                    severity=RecommendationSeverity.WARNING,
                    equipment_code=evaluation.equipment_code,
                    message=(
                        "Selected equipment capacity is below the calculated required capacity."
                    ),
                    rationale=(
                        f"Required capacity is {evaluation.required_capacity}; "
                        f"selected capacity is {evaluation.selected_capacity}."
                    ),
                )
            )

        elif evaluation.status == EquipmentAdequacyStatus.NOT_SELECTED:
            recommendations.append(
                EngineeringRecommendation(
                    recommendation_code=f"{code_suffix}_SELECTION_REQUIRED",
                    severity=RecommendationSeverity.ADVISORY,
                    equipment_code=evaluation.equipment_code,
                    message=(
                        "No selected equipment capacity is available for adequacy verification."
                    ),
                    rationale=(
                        f"The calculated required capacity is {evaluation.required_capacity}."
                    ),
                )
            )

    if inputs.treatment is not None:
        treatment = inputs.treatment

        if (
            treatment.redundancy_philosophy != RedundancyPhilosophy.NONE
            and treatment.installed_unit_count <= treatment.duty_unit_count
        ):
            recommendations.append(
                EngineeringRecommendation(
                    recommendation_code="AIR_TREATMENT_REDUNDANCY_REVIEW",
                    severity=RecommendationSeverity.WARNING,
                    equipment_code="AIR_TREATMENT",
                    message=(
                        "Selected treatment unit arrangement does not provide "
                        "a recorded spare unit."
                    ),
                    rationale=(
                        "A redundancy philosophy is specified, but installed "
                        "unit count is not greater than duty unit count."
                    ),
                )
            )

    if inputs.receiver is not None:
        receiver = inputs.receiver

        if (
            receiver.redundancy_philosophy != RedundancyPhilosophy.NONE
            and receiver.receiver_quantity < 2
        ):
            recommendations.append(
                EngineeringRecommendation(
                    recommendation_code="AIR_RECEIVER_REDUNDANCY_REVIEW",
                    severity=RecommendationSeverity.ADVISORY,
                    equipment_code="AIR_RECEIVER",
                    message=(
                        "Review receiver arrangement against the stated redundancy philosophy."
                    ),
                    rationale=(
                        "A redundancy philosophy is specified while only one receiver is recorded."
                    ),
                )
            )

    if (
        inputs.aftercooler is not None or inputs.moisture_separator is not None
    ) and not inputs.condensate_drains:
        recommendations.append(
            EngineeringRecommendation(
                recommendation_code="CONDENSATE_DRAIN_ARRANGEMENT_REVIEW",
                severity=RecommendationSeverity.ADVISORY,
                equipment_code="CONDENSATE_DRAIN",
                message=("Record and review the condensate drainage arrangement."),
                rationale=(
                    "Aftercooler or moisture-separation equipment is included "
                    "but no condensate drain is recorded in this analysis."
                ),
            )
        )

    if total_additional_pressure_drop_bar > ZERO:
        recommendations.append(
            EngineeringRecommendation(
                recommendation_code="ALLIED_PRESSURE_DROP_ACCOUNTING",
                severity=RecommendationSeverity.INFORMATION,
                equipment_code="ALLIED_SYSTEM",
                message=(
                    "Include allied-equipment pressure drop in the complete "
                    "compressed-air pressure budget."
                ),
                rationale=(
                    "Recorded additional allied-equipment pressure drop is "
                    f"{total_additional_pressure_drop_bar} bar."
                ),
            )
        )

    if treatment_result is not None and treatment_result.dryer_purge_loss_nm3_per_hr > ZERO:
        recommendations.append(
            EngineeringRecommendation(
                recommendation_code="DRYER_PURGE_FLOW_ACCOUNTING",
                severity=RecommendationSeverity.INFORMATION,
                equipment_code="AIR_TREATMENT",
                message=("Include dryer purge flow in compressor supply and energy assessment."),
                rationale=(
                    "Calculated dryer purge loss is "
                    f"{treatment_result.dryer_purge_loss_nm3_per_hr} Nm3/hr."
                ),
            )
        )

    return tuple(recommendations)


def _validate_inputs(
    inputs: AlliedEquipmentAnalysisInput,
) -> None:
    """Validate allied-equipment workflow inputs."""

    if not inputs.analysis_code.strip():
        raise InvalidAlliedEquipmentInputError("Analysis code is required.")

    if (
        inputs.receiver is None
        and inputs.treatment is None
        and inputs.aftercooler is None
        and inputs.moisture_separator is None
        and not inputs.filter_stages
        and not inputs.condensate_drains
    ):
        raise InvalidAlliedEquipmentInputError("At least one allied-equipment item is required.")

    if inputs.receiver is not None:
        receiver = inputs.receiver

        if receiver.receiver_quantity <= 0:
            raise InvalidAlliedEquipmentInputError("Receiver quantity must be greater than zero.")

        _validate_optional_positive(
            receiver.selected_receiver_volume_m3,
            "Selected receiver volume",
        )

        _validate_optional_positive(
            receiver.design_pressure_bar_g,
            "Receiver design pressure",
        )

    if inputs.treatment is not None:
        treatment = inputs.treatment

        if treatment.installed_unit_count <= 0:
            raise InvalidAlliedEquipmentInputError(
                "Installed treatment unit count must be greater than zero."
            )

        if treatment.duty_unit_count <= 0:
            raise InvalidAlliedEquipmentInputError(
                "Duty treatment unit count must be greater than zero."
            )

        if treatment.duty_unit_count > treatment.installed_unit_count:
            raise InvalidAlliedEquipmentInputError(
                "Duty treatment unit count cannot exceed installed unit count."
            )

        _validate_optional_positive(
            treatment.selected_treatment_capacity_nm3_per_hr,
            "Selected treatment capacity",
        )

    flow_rated_equipment_present = (
        inputs.aftercooler is not None
        or inputs.moisture_separator is not None
        or bool(inputs.filter_stages)
    )

    if flow_rated_equipment_present and inputs.receiver is None and inputs.treatment is None:
        raise InvalidAlliedEquipmentInputError(
            "Receiver or treatment sizing basis is required for flow-rated allied equipment."
        )

    if inputs.aftercooler is not None:
        aftercooler = inputs.aftercooler

        _validate_optional_positive(
            aftercooler.selected_flow_capacity_nm3_per_hr,
            "Selected aftercooler flow capacity",
        )

        _validate_non_negative(
            aftercooler.pressure_drop_bar,
            "Aftercooler pressure drop",
        )

    if inputs.moisture_separator is not None:
        separator = inputs.moisture_separator

        _validate_optional_positive(
            separator.selected_flow_capacity_nm3_per_hr,
            "Selected moisture separator flow capacity",
        )

        _validate_non_negative(
            separator.pressure_drop_bar,
            "Moisture separator pressure drop",
        )

    filter_codes: set[str] = set()

    for stage in inputs.filter_stages:
        stage_code = stage.stage_code.strip()

        if not stage_code:
            raise InvalidAlliedEquipmentInputError("Filter stage code is required.")

        normalized_code = stage_code.casefold()

        if normalized_code in filter_codes:
            raise InvalidAlliedEquipmentInputError(f"Duplicate filter stage code: {stage_code}.")

        filter_codes.add(normalized_code)

        _validate_optional_positive(
            stage.selected_flow_capacity_nm3_per_hr,
            f"Selected capacity for filter {stage_code}",
        )

        _validate_non_negative(
            stage.pressure_drop_bar,
            f"Pressure drop for filter {stage_code}",
        )

    drain_codes: set[str] = set()

    for drain in inputs.condensate_drains:
        drain_code = drain.drain_code.strip()

        if not drain_code:
            raise InvalidAlliedEquipmentInputError("Condensate drain code is required.")

        if not drain.location.strip():
            raise InvalidAlliedEquipmentInputError(
                f"Location is required for condensate drain {drain_code}."
            )

        normalized_code = drain_code.casefold()

        if normalized_code in drain_codes:
            raise InvalidAlliedEquipmentInputError(
                f"Duplicate condensate drain code: {drain_code}."
            )

        drain_codes.add(normalized_code)

        _validate_optional_positive(
            drain.selected_condensate_capacity_l_per_hr,
            f"Selected condensate capacity for drain {drain_code}",
        )


def _validate_non_negative(
    value: Decimal,
    field_name: str,
) -> None:
    if value < ZERO:
        raise InvalidAlliedEquipmentInputError(f"{field_name} cannot be negative.")


def _validate_optional_positive(
    value: Decimal | None,
    field_name: str,
) -> None:
    if value is not None and value <= ZERO:
        raise InvalidAlliedEquipmentInputError(
            f"{field_name} must be greater than zero when provided."
        )
