from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.compressed_air.skid.skid_models import (
    AirSkidAssessmentResult,
    AirSkidConfiguration,
    SkidArrangement,
    SkidComponent,
    SkidComponentType,
)
from app.domain.compressed_air.treatment.air_treatment import DryerType
from app.schemas.compressed_air_skid import (
    AirSkidAssessmentRequest,
    AirSkidAssessmentResponse,
    SkidComponentRequest,
)


def component_request() -> SkidComponentRequest:
    return SkidComponentRequest(
        component_code="DRYER-001",
        name="Desiccant Dryer",
        component_type=SkidComponentType.DRYER,
        rated_flow_nm3_per_hr=Decimal("1200"),
        rated_pressure_bar_g=Decimal("10"),
        pressure_drop_bar=Decimal("0.20"),
        quantity=1,
        equipment_source="Engineering schedule",
        model="Generic-D1200",
        notes="Vendor-neutral design data.",
    )


def assessment_request() -> AirSkidAssessmentRequest:
    return AirSkidAssessmentRequest(
        skid_code="SKID-001",
        arrangement=SkidArrangement.CENTRALIZED,
        design_flow_nm3_per_hr=Decimal("1000"),
        design_pressure_bar_g=Decimal("8"),
        dryer_type=DryerType.HEATLESS_DESICCANT,
        components=[component_request()],
        has_wet_receiver=True,
        has_dry_receiver=True,
        has_flow_metering=True,
        has_pressure_monitoring=True,
        has_dew_point_monitoring=True,
        master_control_enabled=True,
        description="Central compressed-air skid.",
    )


def test_component_request_converts_to_domain() -> None:
    result = component_request().to_domain()

    assert isinstance(result, SkidComponent)
    assert result.component_code == "DRYER-001"
    assert result.component_type is SkidComponentType.DRYER
    assert result.rated_flow_nm3_per_hr == Decimal("1200")
    assert result.rated_pressure_bar_g == Decimal("10")
    assert result.pressure_drop_bar == Decimal("0.20")
    assert result.equipment_source == "Engineering schedule"


def test_assessment_request_converts_to_domain_configuration() -> None:
    result = assessment_request().to_domain()

    assert isinstance(result, AirSkidConfiguration)
    assert result.skid_code == "SKID-001"
    assert result.arrangement is SkidArrangement.CENTRALIZED
    assert result.dryer_type is DryerType.HEATLESS_DESICCANT
    assert isinstance(result.components, tuple)
    assert len(result.components) == 1
    assert result.components[0].component_code == "DRYER-001"
    assert result.has_flow_metering is True
    assert result.master_control_enabled is True


def test_response_converts_domain_result() -> None:
    domain_result = AirSkidAssessmentResult(
        skid_code="SKID-001",
        design_flow_nm3_per_hr=Decimal("1000"),
        design_pressure_bar_g=Decimal("8"),
        total_component_count=14,
        total_pressure_drop_bar=Decimal("0.48"),
        minimum_component_flow_capacity_nm3_per_hr=Decimal("1100"),
        minimum_component_pressure_rating_bar_g=Decimal("10"),
        flow_capacity_is_adequate=True,
        pressure_rating_is_adequate=True,
        has_wet_receiver=True,
        has_dry_receiver=True,
        has_flow_metering=True,
        has_pressure_monitoring=True,
        has_dew_point_monitoring=True,
        master_control_enabled=True,
        instrumentation_is_complete=True,
        skid_is_adequate=True,
    )

    response = AirSkidAssessmentResponse.from_domain(domain_result)

    assert response.skid_code == "SKID-001"
    assert response.total_component_count == 14
    assert response.total_pressure_drop_bar == Decimal("0.48")
    assert response.minimum_component_flow_capacity_nm3_per_hr == Decimal("1100")
    assert response.instrumentation_is_complete is True
    assert response.skid_is_adequate is True


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("rated_flow_nm3_per_hr", Decimal("0")),
        ("rated_pressure_bar_g", Decimal("0")),
        ("pressure_drop_bar", Decimal("-0.01")),
        ("quantity", 0),
    ],
)
def test_component_request_rejects_invalid_values(
    field_name: str,
    invalid_value: Decimal | int,
) -> None:
    payload = {
        "component_code": "DRYER-001",
        "name": "Desiccant Dryer",
        "component_type": SkidComponentType.DRYER,
        "rated_flow_nm3_per_hr": Decimal("1200"),
        "rated_pressure_bar_g": Decimal("10"),
        "pressure_drop_bar": Decimal("0.20"),
        "quantity": 1,
    }
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        SkidComponentRequest(**payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "design_flow_nm3_per_hr",
        "design_pressure_bar_g",
    ],
)
def test_assessment_request_rejects_nonpositive_design_values(
    field_name: str,
) -> None:
    payload = assessment_request().model_dump()
    payload[field_name] = Decimal("0")

    with pytest.raises(ValidationError):
        AirSkidAssessmentRequest(**payload)


def test_assessment_request_rejects_empty_components() -> None:
    payload = assessment_request().model_dump()
    payload["components"] = []

    with pytest.raises(ValidationError):
        AirSkidAssessmentRequest(**payload)


def test_assessment_request_rejects_more_than_hundred_components() -> None:
    payload = assessment_request().model_dump()
    payload["components"] = [component_request().model_dump()] * 101

    with pytest.raises(ValidationError):
        AirSkidAssessmentRequest(**payload)
