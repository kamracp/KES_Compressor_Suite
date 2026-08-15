from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/compressed-air/allied/analyze"


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def receiver_payload() -> dict[str, object]:
    return {
        "analysis_code": "ALLIED-API-RECEIVER-001",
        "receiver": {
            "sizing_input": {
                "peak_demand_nm3_per_hr": "1200",
                "available_compressor_flow_nm3_per_hr": "900",
                "event_duration_seconds": "30",
                "receiver_high_pressure_bar_g": "8",
                "receiver_low_pressure_bar_g": "7",
                "reserve_fraction": "0.10",
            },
            "selected_receiver_volume_m3": "3",
            "receiver_quantity": 1,
            "design_pressure_bar_g": "10",
            "redundancy_philosophy": "NONE",
            "equipment_reference": "AR-001",
        },
        "notes": "Receiver API test.",
    }


def treatment_payload() -> dict[str, object]:
    return {
        "analysis_code": "ALLIED-API-TREATMENT-001",
        "treatment": {
            "sizing_input": {
                "required_delivered_flow_nm3_per_hr": "1000",
                "required_air_quality": "INSTRUMENT_AIR",
                "dryer_type": "HEATLESS_DESICCANT",
                "dryer_correction_factor": "0.90",
                "dryer_purge_fraction": "0.10",
                "prefilter_pressure_drop_bar": "0.08",
                "afterfilter_pressure_drop_bar": "0.07",
                "dryer_pressure_drop_bar": "0.20",
                "treatment_capacity_margin_fraction": "0.10",
            },
            "selected_treatment_capacity_nm3_per_hr": "1500",
            "installed_unit_count": 2,
            "duty_unit_count": 1,
            "redundancy_philosophy": "DUTY_STANDBY",
            "equipment_reference": "DRYER-001",
        },
    }


def test_allied_receiver_analysis_returns_engineering_result() -> None:
    response = client.post(
        ENDPOINT,
        json=receiver_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_code"] == "ALLIED-API-RECEIVER-001"
    assert data["receiver_result"] is not None
    assert as_decimal(data["receiver_result"]["flow_deficit_nm3_per_hr"]) == Decimal("300")
    assert data["receiver_result"]["storage_required"] is True
    assert data["receiver_evaluation"] is not None
    assert data["receiver_evaluation"]["status"] == "ADEQUATE"
    assert data["treatment_result"] is None
    assert data["filter_evaluations"] == []
    assert data["notes"] == "Receiver API test."


def test_allied_treatment_analysis_returns_engineering_result() -> None:
    response = client.post(
        ENDPOINT,
        json=treatment_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_code"] == "ALLIED-API-TREATMENT-001"
    assert data["receiver_result"] is None
    assert data["treatment_result"] is not None
    assert data["treatment_result"]["dryer_type"] == "HEATLESS_DESICCANT"
    assert data["treatment_result"]["required_air_quality"] == "INSTRUMENT_AIR"
    assert as_decimal(data["treatment_result"]["total_treatment_pressure_drop_bar"]) == Decimal(
        "0.35"
    )
    assert data["treatment_evaluation"] is not None
    assert data["treatment_evaluation"]["status"] == "ADEQUATE"


def test_allied_analysis_rejects_empty_equipment_scope() -> None:
    response = client.post(
        ENDPOINT,
        json={"analysis_code": "ALLIED-API-EMPTY-001"},
    )

    assert response.status_code == 422
    assert "At least one allied-equipment item is required" in response.json()["detail"]


def test_allied_analysis_rejects_invalid_receiver_pressure_band() -> None:
    payload = receiver_payload()
    receiver = payload["receiver"]

    assert isinstance(receiver, dict)

    sizing_input = receiver["sizing_input"]

    assert isinstance(sizing_input, dict)

    sizing_input["receiver_high_pressure_bar_g"] = "7"
    sizing_input["receiver_low_pressure_bar_g"] = "7"

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422
    assert (
        "Receiver high pressure must be greater than receiver low pressure"
        in response.json()["detail"]
    )


def test_allied_analysis_rejects_invalid_equipment_enum() -> None:
    response = client.post(
        ENDPOINT,
        json={
            "analysis_code": "ALLIED-API-INVALID-001",
            "aftercooler": {
                "aftercooler_type": "UNKNOWN_TYPE",
            },
        },
    )

    assert response.status_code == 422


def test_allied_route_is_registered_in_openapi() -> None:
    openapi_schema = app.openapi()

    assert ENDPOINT in openapi_schema["paths"]
    assert "post" in openapi_schema["paths"][ENDPOINT]
