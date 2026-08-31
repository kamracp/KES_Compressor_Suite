from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/compressed-air/leakage/analyze"


def valid_request() -> dict[str, object]:
    return {
        "analysis_code": "LEAK-API-001",
        "specific_power_kw_per_nm3_per_min": "6",
        "annual_operating_hours": "8000",
        "electricity_tariff_per_kwh": "8",
        "average_system_demand_nm3_per_hr": "5000",
        "notes": "Compressed-air leakage survey.",
        "leaks": [
            {
                "leak_code": "L-001",
                "location": "Compressor House",
                "area": "Utility",
                "equipment_tag": "AIR-HDR-01",
                "component_description": "Header fitting",
                "baseline_leakage_flow_nm3_per_hr": "600",
                "quantification_basis": "ULTRASONIC_ESTIMATE",
                "source_category": "FITTING",
                "survey_pressure_bar_g": "7",
                "expected_repair_fraction": "0.80",
                "repair_status": "OPEN",
                "estimated_repair_cost": "100000",
                "survey_method_reference": "Ultrasonic survey",
            },
            {
                "leak_code": "L-002",
                "location": "Production Line 1",
                "area": "Production",
                "equipment_tag": "QC-101",
                "component_description": "Quick coupling",
                "baseline_leakage_flow_nm3_per_hr": "400",
                "quantification_basis": "FLOW_METER",
                "source_category": "QUICK_COUPLING",
                "survey_pressure_bar_g": "6.5",
                "expected_repair_fraction": "0.50",
                "repair_status": "VERIFIED",
                "verified_post_repair_flow_nm3_per_hr": "100",
            },
        ],
    }


def test_analyze_leakage_management_returns_200() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_code"] == "LEAK-API-001"
    assert data["leak_count"] == 2
    assert len(data["items"]) == 2


def test_analyze_leakage_management_aggregates_energy_and_cost() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_registered_leakage_flow_nm3_per_hr"]) == Decimal("1000")

    assert Decimal(data["leakage_fraction_of_average_system_demand"]) == Decimal("0.2")

    assert Decimal(data["total_wasted_power_kw"]) == Decimal("100")

    assert Decimal(data["total_annual_wasted_energy_kwh"]) == Decimal("800000")

    assert Decimal(data["total_annual_wasted_energy_cost"]) == Decimal("6400000")

    assert Decimal(data["total_recoverable_leakage_flow_nm3_per_hr"]) == Decimal("680")

    assert Decimal(data["total_recoverable_power_kw"]) == Decimal("68")

    assert Decimal(data["total_annual_energy_saving_kwh"]) == Decimal("544000")

    assert Decimal(data["total_annual_cost_saving"]) == Decimal("4352000")

    assert Decimal(data["total_residual_leakage_flow_nm3_per_hr"]) == Decimal("320")


def test_analyze_leakage_management_returns_priority_and_verification() -> None:
    response = client.post(
        ENDPOINT,
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    first = data["items"][0]
    second = data["items"][1]

    assert first["priority"] == "CRITICAL"
    assert second["priority"] == "CRITICAL"

    assert second["repair_status"] == "VERIFIED"

    assert data["verified_leak_count"] == 1

    assert Decimal(data["verified_flow_reduction_nm3_per_hr"]) == Decimal("300")

    assert Decimal(second["verified_flow_reduction_nm3_per_hr"]) == Decimal("300")

    assert Decimal(second["verified_repair_fraction"]) == Decimal("0.75")


def test_duplicate_leak_code_returns_422() -> None:
    request = valid_request()

    leaks = request["leaks"]
    assert isinstance(leaks, list)

    second = leaks[1]
    assert isinstance(second, dict)

    second["leak_code"] = "L-001"

    response = client.post(
        ENDPOINT,
        json=request,
    )

    assert response.status_code == 422

    data = response.json()

    assert "Duplicate leak code" in data["detail"]


def test_empty_leak_register_returns_422() -> None:
    request = valid_request()
    request["leaks"] = []

    response = client.post(
        ENDPOINT,
        json=request,
    )

    assert response.status_code == 422


def test_control_factor_halves_electrical_savings_via_api() -> None:
    ideal_payload = valid_request()

    half_payload = valid_request()
    half_payload["demand_saving_control_factor"] = "0.5"

    ideal = client.post(ENDPOINT, json=ideal_payload)
    half = client.post(ENDPOINT, json=half_payload)

    assert ideal.status_code == 200
    assert half.status_code == 200

    ideal_item = ideal.json()["items"][0]
    half_item = half.json()["items"][0]

    assert Decimal(half_item["energy"]["annual_cost_saving"]) == (
        Decimal(ideal_item["energy"]["annual_cost_saving"]) / 2
    )

    # Air quantities are unchanged by the control factor.
    assert (
        half_item["energy"]["recoverable_leakage_flow_nm3_per_hr"]
        == (ideal_item["energy"]["recoverable_leakage_flow_nm3_per_hr"])
    )

    assert Decimal(half_item["energy"]["demand_saving_control_factor"]) == Decimal("0.5")
