from decimal import Decimal

import pytest

from app.domain.compressed_air.allied.allied_analysis import (
    InvalidAlliedEquipmentInputError,
    analyze_allied_equipment,
)
from app.domain.compressed_air.allied.allied_models import (
    AftercoolerConfiguration,
    AftercoolerType,
    AlliedEquipmentAnalysisInput,
    CondensateDrainConfiguration,
    CondensateDrainType,
    EquipmentAdequacyStatus,
    FilterStageConfiguration,
    FilterStageType,
    MoistureSeparatorConfiguration,
    MoistureSeparatorType,
    ReceiverConfiguration,
    RedundancyPhilosophy,
    TreatmentConfiguration,
)
from app.domain.compressed_air.consumers.consumer_models import AirQualityClass
from app.domain.compressed_air.storage.receiver_sizing import ReceiverSizingInput
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    DryerType,
)


def _receiver_input() -> ReceiverSizingInput:
    return ReceiverSizingInput(
        peak_demand_nm3_per_hr=Decimal("3600"),
        available_compressor_flow_nm3_per_hr=Decimal("3000"),
        event_duration_seconds=Decimal("30"),
        receiver_high_pressure_bar_g=Decimal("7.0"),
        receiver_low_pressure_bar_g=Decimal("6.5"),
        reserve_fraction=Decimal("0.20"),
    )


def _treatment_input(
    *,
    dryer_type: DryerType = DryerType.REFRIGERATED,
    purge_fraction: Decimal = Decimal("0"),
) -> AirTreatmentInput:
    return AirTreatmentInput(
        required_delivered_flow_nm3_per_hr=Decimal("3000"),
        required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
        dryer_type=dryer_type,
        dryer_correction_factor=Decimal("0.95"),
        dryer_purge_fraction=purge_fraction,
        treatment_capacity_margin_fraction=Decimal("0.10"),
    )


def test_multiple_receivers_are_evaluated_using_total_selected_volume() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-001",
            receiver=ReceiverConfiguration(
                sizing_input=_receiver_input(),
                selected_receiver_volume_m3=Decimal("7"),
                receiver_quantity=2,
            ),
        )
    )

    assert result.receiver_evaluation is not None
    assert result.receiver_evaluation.selected_capacity == Decimal("14")
    assert result.receiver_evaluation.status == EquipmentAdequacyStatus.ADEQUATE


def test_treatment_uses_total_duty_unit_capacity() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-002",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(),
                selected_treatment_capacity_nm3_per_hr=Decimal("1800"),
                installed_unit_count=3,
                duty_unit_count=2,
                redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
            ),
        )
    )

    assert result.treatment_evaluation is not None
    assert result.treatment_evaluation.selected_capacity == Decimal("3600")
    assert result.treatment_evaluation.status == EquipmentAdequacyStatus.ADEQUATE


def test_undersized_aftercooler_is_identified() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-003",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(),
            ),
            aftercooler=AftercoolerConfiguration(
                aftercooler_type=AftercoolerType.AIR_COOLED,
                selected_flow_capacity_nm3_per_hr=Decimal("2500"),
            ),
        )
    )

    assert result.aftercooler_evaluation is not None
    assert result.aftercooler_evaluation.status == EquipmentAdequacyStatus.UNDERSIZED

    codes = {item.recommendation_code for item in result.recommendations}
    assert "AFTERCOOLER_UNDERSIZED" in codes


def test_additional_pressure_drop_is_aggregated() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-004",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(),
            ),
            aftercooler=AftercoolerConfiguration(
                aftercooler_type=AftercoolerType.WATER_COOLED,
                selected_flow_capacity_nm3_per_hr=Decimal("3500"),
                pressure_drop_bar=Decimal("0.08"),
            ),
            moisture_separator=MoistureSeparatorConfiguration(
                separator_type=MoistureSeparatorType.CYCLONIC,
                selected_flow_capacity_nm3_per_hr=Decimal("3500"),
                pressure_drop_bar=Decimal("0.04"),
            ),
            filter_stages=(
                FilterStageConfiguration(
                    stage_code="F-01",
                    stage_type=FilterStageType.COALESCING,
                    selected_flow_capacity_nm3_per_hr=Decimal("3500"),
                    pressure_drop_bar=Decimal("0.05"),
                ),
            ),
        )
    )

    assert result.total_additional_pressure_drop_bar == Decimal("0.17")


def test_dryer_purge_loss_generates_accounting_recommendation() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-005",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(
                    dryer_type=DryerType.HEATLESS_DESICCANT,
                    purge_fraction=Decimal("0.15"),
                ),
            ),
        )
    )

    assert result.treatment_result is not None
    assert result.treatment_result.dryer_purge_loss_nm3_per_hr > Decimal("0")

    codes = {item.recommendation_code for item in result.recommendations}
    assert "DRYER_PURGE_FLOW_ACCOUNTING" in codes


def test_treatment_redundancy_mismatch_generates_warning() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-006",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(),
                installed_unit_count=1,
                duty_unit_count=1,
                redundancy_philosophy=RedundancyPhilosophy.DUTY_STANDBY,
            ),
        )
    )

    codes = {item.recommendation_code for item in result.recommendations}
    assert "AIR_TREATMENT_REDUNDANCY_REVIEW" in codes


def test_recorded_condensate_drain_avoids_missing_drain_recommendation() -> None:
    result = analyze_allied_equipment(
        AlliedEquipmentAnalysisInput(
            analysis_code="AE-007",
            treatment=TreatmentConfiguration(
                sizing_input=_treatment_input(),
            ),
            aftercooler=AftercoolerConfiguration(
                aftercooler_type=AftercoolerType.AIR_COOLED,
                selected_flow_capacity_nm3_per_hr=Decimal("3500"),
            ),
            condensate_drains=(
                CondensateDrainConfiguration(
                    drain_code="D-01",
                    location="Aftercooler outlet",
                    drain_type=CondensateDrainType.ZERO_LOSS,
                ),
            ),
        )
    )

    codes = {item.recommendation_code for item in result.recommendations}
    assert "CONDENSATE_DRAIN_ARRANGEMENT_REVIEW" not in codes


def test_flow_rated_equipment_requires_sizing_basis() -> None:
    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="Receiver or treatment sizing basis is required",
    ):
        analyze_allied_equipment(
            AlliedEquipmentAnalysisInput(
                analysis_code="AE-008",
                aftercooler=AftercoolerConfiguration(
                    aftercooler_type=AftercoolerType.AIR_COOLED,
                    selected_flow_capacity_nm3_per_hr=Decimal("3000"),
                ),
            )
        )


def test_duplicate_filter_stage_code_is_rejected() -> None:
    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="Duplicate filter stage code",
    ):
        analyze_allied_equipment(
            AlliedEquipmentAnalysisInput(
                analysis_code="AE-009",
                treatment=TreatmentConfiguration(
                    sizing_input=_treatment_input(),
                ),
                filter_stages=(
                    FilterStageConfiguration(
                        stage_code="F-01",
                        stage_type=FilterStageType.PARTICULATE,
                    ),
                    FilterStageConfiguration(
                        stage_code="f-01",
                        stage_type=FilterStageType.COALESCING,
                    ),
                ),
            )
        )


def test_duty_unit_count_cannot_exceed_installed_units() -> None:
    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="Duty treatment unit count cannot exceed installed unit count",
    ):
        analyze_allied_equipment(
            AlliedEquipmentAnalysisInput(
                analysis_code="AE-010",
                treatment=TreatmentConfiguration(
                    sizing_input=_treatment_input(),
                    installed_unit_count=1,
                    duty_unit_count=2,
                ),
            )
        )


def test_negative_aftercooler_pressure_drop_is_rejected() -> None:
    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="Aftercooler pressure drop cannot be negative",
    ):
        analyze_allied_equipment(
            AlliedEquipmentAnalysisInput(
                analysis_code="AE-011",
                treatment=TreatmentConfiguration(
                    sizing_input=_treatment_input(),
                ),
                aftercooler=AftercoolerConfiguration(
                    aftercooler_type=AftercoolerType.AIR_COOLED,
                    selected_flow_capacity_nm3_per_hr=Decimal("3500"),
                    pressure_drop_bar=Decimal("-0.01"),
                ),
            )
        )


def test_blank_analysis_code_is_rejected() -> None:
    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="Analysis code is required",
    ):
        analyze_allied_equipment(
            AlliedEquipmentAnalysisInput(
                analysis_code="   ",
                receiver=ReceiverConfiguration(
                    sizing_input=_receiver_input(),
                ),
            )
        )
