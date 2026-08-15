from decimal import Decimal

import pytest

from app.domain.compressed_air.allied.allied_analysis import (
    InvalidAlliedEquipmentInputError,
)
from app.domain.compressed_air.allied.allied_models import (
    RedundancyPhilosophy,
)
from app.domain.compressed_air.consumers.consumer_models import AirQualityClass
from app.domain.compressed_air.treatment.air_treatment import DryerType
from app.schemas.compressed_air_allied import (
    AirTreatmentInputRequest,
    AlliedEquipmentAnalysisRequest,
    ReceiverConfigurationRequest,
    ReceiverSizingInputRequest,
    TreatmentConfigurationRequest,
)
from app.services.compressed_air_allied import (
    CompressedAirAlliedService,
    compressed_air_allied_service,
)


def test_service_analyzes_receiver_configuration() -> None:
    request = AlliedEquipmentAnalysisRequest(
        analysis_code="ALLIED-RECEIVER-001",
        receiver=ReceiverConfigurationRequest(
            sizing_input=ReceiverSizingInputRequest(
                peak_demand_nm3_per_hr=Decimal("1200"),
                available_compressor_flow_nm3_per_hr=Decimal("900"),
                event_duration_seconds=Decimal("30"),
                receiver_high_pressure_bar_g=Decimal("8"),
                receiver_low_pressure_bar_g=Decimal("7"),
                reserve_fraction=Decimal("0.10"),
            ),
            selected_receiver_volume_m3=Decimal("3"),
            receiver_quantity=1,
            design_pressure_bar_g=Decimal("10"),
            equipment_reference="AR-001",
        ),
        notes="Receiver service test.",
    )

    response = compressed_air_allied_service.analyze(request)

    assert response.analysis_code == "ALLIED-RECEIVER-001"
    assert response.receiver_result is not None
    assert response.receiver_result.flow_deficit_nm3_per_hr == Decimal("300")
    assert response.receiver_result.storage_required is True
    assert response.receiver_evaluation is not None
    assert response.receiver_evaluation.equipment_code == "AIR_RECEIVER"
    assert response.receiver_evaluation.status == "ADEQUATE"
    assert response.treatment_result is None
    assert response.notes == "Receiver service test."


def test_service_analyzes_treatment_configuration() -> None:
    request = AlliedEquipmentAnalysisRequest(
        analysis_code="ALLIED-TREATMENT-001",
        treatment=TreatmentConfigurationRequest(
            sizing_input=AirTreatmentInputRequest(
                required_delivered_flow_nm3_per_hr=Decimal("1000"),
                required_air_quality=AirQualityClass.INSTRUMENT_AIR,
                dryer_type=DryerType.HEATLESS_DESICCANT,
                dryer_correction_factor=Decimal("0.90"),
                dryer_purge_fraction=Decimal("0.10"),
                prefilter_pressure_drop_bar=Decimal("0.08"),
                afterfilter_pressure_drop_bar=Decimal("0.07"),
                dryer_pressure_drop_bar=Decimal("0.20"),
                treatment_capacity_margin_fraction=Decimal("0.10"),
            ),
            selected_treatment_capacity_nm3_per_hr=Decimal("1500"),
            installed_unit_count=2,
            duty_unit_count=1,
            redundancy_philosophy=RedundancyPhilosophy.DUTY_STANDBY,
            equipment_reference="DRYER-001",
        ),
    )

    response = compressed_air_allied_service.analyze(request)

    assert response.analysis_code == "ALLIED-TREATMENT-001"
    assert response.receiver_result is None
    assert response.treatment_result is not None
    assert response.treatment_result.dryer_type == "HEATLESS_DESICCANT"
    assert response.treatment_result.required_air_quality == "INSTRUMENT_AIR"
    assert response.treatment_result.total_treatment_pressure_drop_bar == Decimal("0.35")
    assert response.treatment_evaluation is not None
    assert response.treatment_evaluation.equipment_code == "AIR_TREATMENT"
    assert response.treatment_evaluation.status == "ADEQUATE"


def test_service_propagates_domain_validation_error() -> None:
    request = AlliedEquipmentAnalysisRequest(
        analysis_code="ALLIED-EMPTY-001",
    )

    with pytest.raises(
        InvalidAlliedEquipmentInputError,
        match="At least one allied-equipment item is required",
    ):
        compressed_air_allied_service.analyze(request)


def test_module_exposes_service_singleton() -> None:
    assert isinstance(
        compressed_air_allied_service,
        CompressedAirAlliedService,
    )
