from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.compressed_air.allied.allied_models import (
    AftercoolerType,
    AlliedEquipmentAnalysisInput,
    AlliedEquipmentAnalysisResult,
    CondensateDrainType,
    EngineeringRecommendation,
    EquipmentAdequacyStatus,
    EquipmentCapacityEvaluation,
    FilterStageType,
    RecommendationSeverity,
    RedundancyPhilosophy,
)
from app.domain.compressed_air.consumers.consumer_models import AirQualityClass
from app.domain.compressed_air.storage.receiver_sizing import ReceiverSizingResult
from app.domain.compressed_air.treatment.air_treatment import DryerType
from app.schemas.compressed_air_allied import (
    AftercoolerConfigurationRequest,
    AirTreatmentInputRequest,
    AlliedEquipmentAnalysisRequest,
    AlliedEquipmentAnalysisResponse,
    CondensateDrainConfigurationRequest,
    FilterStageConfigurationRequest,
    MoistureSeparatorConfigurationRequest,
    ReceiverConfigurationRequest,
    ReceiverSizingInputRequest,
    TreatmentConfigurationRequest,
)


def test_receiver_configuration_converts_to_domain() -> None:
    request = ReceiverConfigurationRequest(
        sizing_input=ReceiverSizingInputRequest(
            peak_demand_nm3_per_hr=Decimal("1200"),
            available_compressor_flow_nm3_per_hr=Decimal("900"),
            event_duration_seconds=Decimal("30"),
            receiver_high_pressure_bar_g=Decimal("8"),
            receiver_low_pressure_bar_g=Decimal("7"),
            reserve_fraction=Decimal("0.15"),
        ),
        selected_receiver_volume_m3=Decimal("4.5"),
        receiver_quantity=2,
        design_pressure_bar_g=Decimal("10"),
        redundancy_philosophy=RedundancyPhilosophy.MULTIPLE_DUTY,
        equipment_reference="AR-001",
        notes="Two equal air receivers.",
    )

    result = request.to_domain()

    assert result.sizing_input.peak_demand_nm3_per_hr == Decimal("1200")
    assert result.sizing_input.reserve_fraction == Decimal("0.15")
    assert result.selected_receiver_volume_m3 == Decimal("4.5")
    assert result.receiver_quantity == 2
    assert result.redundancy_philosophy is RedundancyPhilosophy.MULTIPLE_DUTY
    assert result.equipment_reference == "AR-001"


def test_treatment_configuration_converts_to_domain() -> None:
    request = TreatmentConfigurationRequest(
        sizing_input=AirTreatmentInputRequest(
            required_delivered_flow_nm3_per_hr=Decimal("1000"),
            required_air_quality=AirQualityClass.INSTRUMENT_AIR,
            dryer_type=DryerType.HEATLESS_DESICCANT,
            dryer_correction_factor=Decimal("0.85"),
            dryer_purge_fraction=Decimal("0.15"),
            prefilter_pressure_drop_bar=Decimal("0.08"),
            afterfilter_pressure_drop_bar=Decimal("0.07"),
            dryer_pressure_drop_bar=Decimal("0.20"),
            treatment_capacity_margin_fraction=Decimal("0.10"),
        ),
        selected_treatment_capacity_nm3_per_hr=Decimal("1600"),
        installed_unit_count=2,
        duty_unit_count=1,
        redundancy_philosophy=RedundancyPhilosophy.DUTY_STANDBY,
        equipment_reference="DRYER-001",
    )

    result = request.to_domain()

    assert result.sizing_input.required_air_quality is AirQualityClass.INSTRUMENT_AIR
    assert result.sizing_input.dryer_type is DryerType.HEATLESS_DESICCANT
    assert result.sizing_input.dryer_purge_fraction == Decimal("0.15")
    assert result.selected_treatment_capacity_nm3_per_hr == Decimal("1600")
    assert result.installed_unit_count == 2
    assert result.duty_unit_count == 1
    assert result.redundancy_philosophy is RedundancyPhilosophy.DUTY_STANDBY


def test_complete_request_converts_collections_to_domain_tuples() -> None:
    request = AlliedEquipmentAnalysisRequest(
        analysis_code="ALLIED-001",
        aftercooler=AftercoolerConfigurationRequest(
            aftercooler_type=AftercoolerType.AIR_COOLED,
            selected_flow_capacity_nm3_per_hr=Decimal("1250"),
            pressure_drop_bar=Decimal("0.12"),
            inlet_temperature_c=Decimal("90"),
            outlet_temperature_c=Decimal("40"),
        ),
        moisture_separator=MoistureSeparatorConfigurationRequest(
            separator_type="CYCLONIC",
            selected_flow_capacity_nm3_per_hr=Decimal("1250"),
            pressure_drop_bar=Decimal("0.05"),
        ),
        filter_stages=[
            FilterStageConfigurationRequest(
                stage_code="F-001",
                stage_type=FilterStageType.COALESCING,
                selected_flow_capacity_nm3_per_hr=Decimal("1200"),
                pressure_drop_bar=Decimal("0.08"),
            ),
            FilterStageConfigurationRequest(
                stage_code="F-002",
                stage_type=FilterStageType.ACTIVATED_CARBON,
                selected_flow_capacity_nm3_per_hr=Decimal("1200"),
                pressure_drop_bar=Decimal("0.06"),
            ),
        ],
        condensate_drains=[
            CondensateDrainConfigurationRequest(
                drain_code="D-001",
                location="Wet receiver",
                drain_type=CondensateDrainType.ZERO_LOSS,
                selected_condensate_capacity_l_per_hr=Decimal("25"),
            )
        ],
        notes="Complete allied-equipment request.",
    )

    result = request.to_domain()

    assert isinstance(result, AlliedEquipmentAnalysisInput)
    assert result.analysis_code == "ALLIED-001"
    assert result.aftercooler is not None
    assert result.aftercooler.aftercooler_type is AftercoolerType.AIR_COOLED
    assert result.moisture_separator is not None
    assert result.moisture_separator.separator_type.value == "CYCLONIC"
    assert isinstance(result.filter_stages, tuple)
    assert len(result.filter_stages) == 2
    assert result.filter_stages[1].stage_code == "F-002"
    assert isinstance(result.condensate_drains, tuple)
    assert result.condensate_drains[0].drain_code == "D-001"


def test_request_uses_independent_default_collections() -> None:
    first = AlliedEquipmentAnalysisRequest(analysis_code="ALLIED-001")
    second = AlliedEquipmentAnalysisRequest(analysis_code="ALLIED-002")

    first.filter_stages.append(
        FilterStageConfigurationRequest(
            stage_code="F-001",
            stage_type=FilterStageType.PARTICULATE,
        )
    )

    assert len(first.filter_stages) == 1
    assert second.filter_stages == []
    assert second.condensate_drains == []


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("event_duration_seconds", Decimal("0")),
        ("receiver_low_pressure_bar_g", Decimal("-0.01")),
        ("reserve_fraction", Decimal("1.01")),
    ],
)
def test_receiver_input_rejects_invalid_values(
    field_name: str,
    invalid_value: Decimal,
) -> None:
    payload = {
        "peak_demand_nm3_per_hr": Decimal("1200"),
        "available_compressor_flow_nm3_per_hr": Decimal("900"),
        "event_duration_seconds": Decimal("30"),
        "receiver_high_pressure_bar_g": Decimal("8"),
        "receiver_low_pressure_bar_g": Decimal("7"),
        "reserve_fraction": Decimal("0.10"),
    }
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        ReceiverSizingInputRequest(**payload)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("required_delivered_flow_nm3_per_hr", Decimal("0")),
        ("dryer_correction_factor", Decimal("0")),
        ("dryer_purge_fraction", Decimal("1")),
    ],
)
def test_treatment_input_rejects_invalid_values(
    field_name: str,
    invalid_value: Decimal,
) -> None:
    payload = {
        "required_delivered_flow_nm3_per_hr": Decimal("1000"),
        "required_air_quality": AirQualityClass.GENERAL_PLANT_AIR,
        "dryer_type": DryerType.REFRIGERATED,
        "dryer_correction_factor": Decimal("1"),
        "dryer_purge_fraction": Decimal("0"),
    }
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        AirTreatmentInputRequest(**payload)


def test_request_rejects_more_than_twenty_filter_stages() -> None:
    filter_stage = FilterStageConfigurationRequest(
        stage_code="F-001",
        stage_type=FilterStageType.PARTICULATE,
    )

    with pytest.raises(ValidationError):
        AlliedEquipmentAnalysisRequest(
            analysis_code="ALLIED-001",
            filter_stages=[filter_stage] * 21,
        )


def test_response_converts_nested_domain_result() -> None:
    receiver_result = ReceiverSizingResult(
        peak_demand_nm3_per_hr=Decimal("1200"),
        available_compressor_flow_nm3_per_hr=Decimal("900"),
        flow_deficit_nm3_per_hr=Decimal("300"),
        event_duration_seconds=Decimal("30"),
        receiver_high_pressure_bar_g=Decimal("8"),
        receiver_low_pressure_bar_g=Decimal("7"),
        pressure_band_bar=Decimal("1"),
        base_receiver_volume_m3=Decimal("2.50"),
        reserve_fraction=Decimal("0.10"),
        recommended_receiver_volume_m3=Decimal("2.75"),
        storage_required=True,
    )
    evaluation = EquipmentCapacityEvaluation(
        equipment_code="RECEIVER",
        required_capacity=Decimal("2.75"),
        selected_capacity=Decimal("3.00"),
        capacity_margin=Decimal("0.25"),
        capacity_margin_fraction=Decimal("0.090909"),
        status=EquipmentAdequacyStatus.ADEQUATE,
    )
    recommendation = EngineeringRecommendation(
        recommendation_code="REC-001",
        severity=RecommendationSeverity.INFORMATION,
        equipment_code="RECEIVER",
        message="Selected receiver capacity is adequate.",
        rationale="Selected capacity exceeds required capacity.",
    )
    domain_result = AlliedEquipmentAnalysisResult(
        analysis_code="ALLIED-001",
        receiver_result=receiver_result,
        treatment_result=None,
        receiver_evaluation=evaluation,
        treatment_evaluation=None,
        aftercooler_evaluation=None,
        moisture_separator_evaluation=None,
        filter_evaluations=(evaluation,),
        total_additional_pressure_drop_bar=Decimal("0.23"),
        recommendations=(recommendation,),
        notes="Completed analysis.",
    )

    response = AlliedEquipmentAnalysisResponse.from_domain(domain_result)

    assert response.analysis_code == "ALLIED-001"
    assert response.receiver_result is not None
    assert response.receiver_result.storage_required is True
    assert response.receiver_result.recommended_receiver_volume_m3 == Decimal("2.75")
    assert response.receiver_evaluation is not None
    assert response.receiver_evaluation.status == "ADEQUATE"
    assert response.filter_evaluations[0].equipment_code == "RECEIVER"
    assert response.recommendations[0].severity == "INFORMATION"
    assert response.total_additional_pressure_drop_bar == Decimal("0.23")
