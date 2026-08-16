from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/compressed-air/skid/assess"


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def rated_component(
    component_code: str,
    component_type: str,
    pressure_drop_bar: str = "0",
) -> dict[str, object]:
    return {
        "component_code": component_code,
        "name": component_type.replace("_", " ").title(),
        "component_type": component_type,
        "rated_flow_nm3_per_hr": "1200",
        "rated_pressure_bar_g": "10",
        "pressure_drop_bar": pressure_drop_bar,
        "quantity": 1,
    }


def complete_payload() -> dict[str, object]:
    return {
        "skid_code": "SKID-API-001",
        "arrangement": "CENTRALIZED",
        "design_flow_nm3_per_hr": "1000",
        "design_pressure_bar_g": "8",
        "dryer_type": "HEATLESS_DESICCANT",
        "components": [
            rated_component("AC-001", "AFTERCOOLER", "0.10"),
            rated_component("MS-001", "MOISTURE_SEPARATOR", "0.05"),
            rated_component("WR-001", "WET_RECEIVER"),
            rated_component("PF-001", "PREFILTER", "0.08"),
            rated_component("DRYER-001", "DRYER", "0.20"),
            rated_component("AF-001", "AFTERFILTER", "0.08"),
            rated_component("DR-001", "DRY_RECEIVER"),
            rated_component("FM-001", "FLOW_METER", "0.05"),
            {
                "component_code": "PS-001",
                "name": "Pressure Sensor",
                "component_type": "PRESSURE_SENSOR",
            },
            {
                "component_code": "DPS-001",
                "name": "Dew Point Sensor",
                "component_type": "DEW_POINT_SENSOR",
            },
            {
                "component_code": "MC-001",
                "name": "Master Controller",
                "component_type": "MASTER_CONTROLLER",
            },
        ],
        "has_wet_receiver": True,
        "has_dry_receiver": True,
        "has_flow_metering": True,
        "has_pressure_monitoring": True,
        "has_dew_point_monitoring": True,
        "master_control_enabled": True,
        "description": "Complete factory compressed-air skid.",
    }


def test_skid_assessment_returns_engineering_result() -> None:
    response = client.post(
        ENDPOINT,
        json=complete_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["skid_code"] == "SKID-API-001"
    assert data["total_component_count"] == 11
    assert as_decimal(data["total_pressure_drop_bar"]) == Decimal("0.56")
    assert as_decimal(data["minimum_component_flow_capacity_nm3_per_hr"]) == Decimal("1200")
    assert as_decimal(data["minimum_component_pressure_rating_bar_g"]) == Decimal("10")
    assert data["flow_capacity_is_adequate"] is True
    assert data["pressure_rating_is_adequate"] is True
    assert data["instrumentation_is_complete"] is True
    assert data["skid_is_adequate"] is True


def test_skid_assessment_reports_incomplete_instrumentation() -> None:
    payload = complete_payload()
    payload["has_dew_point_monitoring"] = False

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["has_dew_point_monitoring"] is False
    assert data["instrumentation_is_complete"] is False
    assert data["skid_is_adequate"] is False


def test_skid_assessment_rejects_duplicate_component_codes() -> None:
    payload = complete_payload()
    components = payload["components"]

    assert isinstance(components, list)

    first_component = components[0]

    assert isinstance(first_component, dict)

    components.append(first_component.copy())

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422
    assert "Duplicate skid component code: AC-001" in response.json()["detail"]


def test_skid_assessment_rejects_nonpositive_design_flow() -> None:
    payload = complete_payload()
    payload["design_flow_nm3_per_hr"] = "0"

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422


def test_skid_assessment_rejects_empty_components() -> None:
    payload = complete_payload()
    payload["components"] = []

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422


def test_skid_route_is_registered_in_openapi() -> None:
    openapi_schema = app.openapi()

    assert ENDPOINT in openapi_schema["paths"]
    assert "post" in openapi_schema["paths"][ENDPOINT]
