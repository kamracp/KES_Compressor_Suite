from decimal import Decimal

import pytest

from app.domain.compressed_air.skid.skid_assessment import (
    InvalidAirSkidInputError,
)
from app.domain.compressed_air.skid.skid_models import (
    SkidArrangement,
    SkidComponentType,
)
from app.domain.compressed_air.treatment.air_treatment import DryerType
from app.schemas.compressed_air_skid import (
    AirSkidAssessmentRequest,
    SkidComponentRequest,
)
from app.services.compressed_air_skid import (
    CompressedAirSkidService,
    compressed_air_skid_service,
)


def rated_component(
    component_code: str,
    component_type: SkidComponentType,
    pressure_drop_bar: str = "0",
) -> SkidComponentRequest:
    return SkidComponentRequest(
        component_code=component_code,
        name=component_type.value.replace("_", " ").title(),
        component_type=component_type,
        rated_flow_nm3_per_hr=Decimal("1200"),
        rated_pressure_bar_g=Decimal("10"),
        pressure_drop_bar=Decimal(pressure_drop_bar),
    )


def complete_components() -> list[SkidComponentRequest]:
    return [
        rated_component(
            "AC-001",
            SkidComponentType.AFTERCOOLER,
            "0.10",
        ),
        rated_component(
            "MS-001",
            SkidComponentType.MOISTURE_SEPARATOR,
            "0.05",
        ),
        rated_component(
            "WR-001",
            SkidComponentType.WET_RECEIVER,
        ),
        rated_component(
            "PF-001",
            SkidComponentType.PREFILTER,
            "0.08",
        ),
        rated_component(
            "DRYER-001",
            SkidComponentType.DRYER,
            "0.20",
        ),
        rated_component(
            "AF-001",
            SkidComponentType.AFTERFILTER,
            "0.08",
        ),
        rated_component(
            "DR-001",
            SkidComponentType.DRY_RECEIVER,
        ),
        rated_component(
            "FM-001",
            SkidComponentType.FLOW_METER,
            "0.05",
        ),
        SkidComponentRequest(
            component_code="PS-001",
            name="Pressure Sensor",
            component_type=SkidComponentType.PRESSURE_SENSOR,
        ),
        SkidComponentRequest(
            component_code="DPS-001",
            name="Dew Point Sensor",
            component_type=SkidComponentType.DEW_POINT_SENSOR,
        ),
        SkidComponentRequest(
            component_code="MC-001",
            name="Master Controller",
            component_type=SkidComponentType.MASTER_CONTROLLER,
        ),
    ]


def complete_request() -> AirSkidAssessmentRequest:
    return AirSkidAssessmentRequest(
        skid_code="SKID-001",
        arrangement=SkidArrangement.CENTRALIZED,
        design_flow_nm3_per_hr=Decimal("1000"),
        design_pressure_bar_g=Decimal("8"),
        dryer_type=DryerType.HEATLESS_DESICCANT,
        components=complete_components(),
        has_wet_receiver=True,
        has_dry_receiver=True,
        has_flow_metering=True,
        has_pressure_monitoring=True,
        has_dew_point_monitoring=True,
        master_control_enabled=True,
        description="Complete factory compressed-air skid.",
    )


def test_service_assesses_complete_skid() -> None:
    response = compressed_air_skid_service.assess(complete_request())

    assert response.skid_code == "SKID-001"
    assert response.total_component_count == 11
    assert response.total_pressure_drop_bar == Decimal("0.56")
    assert response.minimum_component_flow_capacity_nm3_per_hr == Decimal("1200")
    assert response.minimum_component_pressure_rating_bar_g == Decimal("10")
    assert response.flow_capacity_is_adequate is True
    assert response.pressure_rating_is_adequate is True
    assert response.instrumentation_is_complete is True
    assert response.skid_is_adequate is True


def test_service_reports_incomplete_instrumentation() -> None:
    request = complete_request().model_copy(update={"has_dew_point_monitoring": False})

    response = compressed_air_skid_service.assess(request)

    assert response.has_dew_point_monitoring is False
    assert response.instrumentation_is_complete is False
    assert response.skid_is_adequate is False


def test_service_propagates_duplicate_component_error() -> None:
    request = complete_request()
    duplicate = request.components[0].model_copy()
    request = request.model_copy(update={"components": [*request.components, duplicate]})

    with pytest.raises(
        InvalidAirSkidInputError,
        match="Duplicate skid component code: AC-001",
    ):
        compressed_air_skid_service.assess(request)


def test_module_exposes_service_singleton() -> None:
    assert isinstance(
        compressed_air_skid_service,
        CompressedAirSkidService,
    )
