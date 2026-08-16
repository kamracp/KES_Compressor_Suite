from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/compressed-air/allied/analyze"


def valid_request() -> dict[str, object]:
    return {
        "analysis_code": "ALLIED-API-001",
        "receiver": {
            "sizing_input": {
                "peak_demand_nm3_per_hr": "3600",
                "available_compressor_flow_nm3_per_hr": "3000",
                "event_duration_seconds": "30",
                "receiver_high_pressure_bar_g": "7.0",
                "receiver_low_pressure_bar_g": "6.5",
                "reserve_fraction": "0.20",
            },
            "selected_receiver_volume_m3": "7",
            "receiver_quantity": 2,
            "design_pressure_bar_g": "10",
            "redundancy_philosophy": "NONE",
        },
        "treatment": {
            "sizing_input": {
                "required_delivered_flow_nm3_per_hr": "3000",
                "required_air_quality": "GENERAL_PLANT_AIR",
                "dryer_type": "REFRIGERATED",
                "dryer_correction_factor": "0.95",
                "dryer_purge_fraction": "0",
                "prefilter_pressure_drop_bar": "0.05",
                "afterfilter_pressure_drop_bar": "0.05",
                "dryer_pressure_drop_bar": "0.10",
                "treatment_capacity_margin_fraction": "0.10",
            },
            "selected_treatment_capacity_nm3_per_hr": "1800",
            "installed_unit_count": 3,
            "duty_unit_count": 2,
            "redundancy_philosophy": "N_PLUS_1",
        },
        "aftercooler": {
            "aftercooler_type": "AIR_COOLED",
            "selected_flow_capacity_nm3_per_hr": "2500",
            "pressure_drop_bar": "0.08",
            "inlet_temperature_c": "90",
            "outlet_temperature_c": "40",
        },
        "moisture_separator": {
            "separator_type": "CYCLONIC",
            "selected_flow_capacity_nm3_per_hr": "3500",
            "pressure_drop_bar": "0.04",
        },
        "filter_stages": [
            {
                "stage_code": "F-01",
                "stage_type": "COALESCING",
                "selected_flow_capacity_nm3_per_hr": "3500",
                "pressure_drop_bar": "0.05",
            }
        ],
        "condensate_drains": [
            {
                "drain_code": "D-01",
                "location": "Aftercooler outlet",
                "drain_type": "ZERO_LOSS",
            }
        ],
        "notes": "Allied-equipment API engineering analysis.",
    }


def test_analyze_allied_equipment_returns_200() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_code"] == "ALLIED-API-001"
    assert data["receiver_result"] is not None
    assert data["treatment_result"] is not None
    assert len(data["filter_evaluations"]) == 1


def test_allied_api_uses_quantity_aware_capacity_evaluation() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    receiver = data["receiver_evaluation"]
    treatment = data["treatment_evaluation"]

    assert Decimal(receiver["selected_capacity"]) == Decimal("14")
    assert receiver["status"] == "ADEQUATE"

    assert Decimal(treatment["selected_capacity"]) == Decimal("3600")
    assert treatment["status"] == "ADEQUATE"


def test_allied_api_reports_pressure_drop_and_undersized_aftercooler() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_additional_pressure_drop_bar"]) == Decimal("0.17")

    aftercooler = data["aftercooler_evaluation"]

    assert aftercooler["status"] == "UNDERSIZED"

    codes = {item["recommendation_code"] for item in data["recommendations"]}

    assert "AFTERCOOLER_UNDERSIZED" in codes
    assert "ALLIED_PRESSURE_DROP_ACCOUNTING" in codes


def test_allied_api_reports_dryer_purge_recommendation() -> None:
    request = valid_request()

    treatment = request["treatment"]
    assert isinstance(treatment, dict)

    sizing_input = treatment["sizing_input"]
    assert isinstance(sizing_input, dict)

    sizing_input["dryer_type"] = "HEATLESS_DESICCANT"
    sizing_input["dryer_purge_fraction"] = "0.15"

    response = client.post(ENDPOINT, json=request)

    assert response.status_code == 200

    data = response.json()

    codes = {item["recommendation_code"] for item in data["recommendations"]}

    assert "DRYER_PURGE_FLOW_ACCOUNTING" in codes


def test_invalid_duty_unit_count_returns_422() -> None:
    request = valid_request()

    treatment = request["treatment"]
    assert isinstance(treatment, dict)

    treatment["installed_unit_count"] = 1
    treatment["duty_unit_count"] = 2

    response = client.post(ENDPOINT, json=request)

    assert response.status_code == 422
    assert (
        "Duty treatment unit count cannot exceed installed unit count"
        in (response.json()["detail"])
    )


def test_invalid_receiver_event_duration_returns_422() -> None:
    request = valid_request()

    receiver = request["receiver"]
    assert isinstance(receiver, dict)

    sizing_input = receiver["sizing_input"]
    assert isinstance(sizing_input, dict)

    sizing_input["event_duration_seconds"] = "0"

    response = client.post(ENDPOINT, json=request)

    assert response.status_code == 422
