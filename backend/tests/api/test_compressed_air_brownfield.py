from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def build_request() -> dict:
    return {
        "audit_code": "BF-API-001",
        "project_id": 1,
        "compressors": [
            {
                "unit_code": "AC-01",
                "manufacturer": "TEST",
                "model": "TEST-01",
                "technology": "ROTARY_SCREW_OIL_INJECTED",
                "control_mode": "LOAD_UNLOAD",
                "rated_fad_nm3_per_hr": "1800",
                "rated_discharge_pressure_bar_g": "7.0",
                "rated_motor_power_kw": "250",
                "available": True,
            },
            {
                "unit_code": "AC-02",
                "manufacturer": "TEST",
                "model": "TEST-02",
                "technology": "ROTARY_SCREW_OIL_INJECTED",
                "control_mode": "LOAD_UNLOAD",
                "rated_fad_nm3_per_hr": "1800",
                "rated_discharge_pressure_bar_g": "7.0",
                "rated_motor_power_kw": "250",
                "available": True,
            },
            {
                "unit_code": "AC-03",
                "manufacturer": "TEST",
                "model": "TEST-03",
                "technology": "ROTARY_SCREW_OIL_INJECTED",
                "control_mode": "LOAD_UNLOAD",
                "rated_fad_nm3_per_hr": "1800",
                "rated_discharge_pressure_bar_g": "7.0",
                "rated_motor_power_kw": "250",
                "available": True,
            },
        ],
        "compressor_measurements": [
            {
                "unit_code": "AC-01",
                "timestamp_label": "T1",
                "operating_state": "LOADED",
                "measured_flow_nm3_per_hr": "1500",
                "measured_discharge_pressure_bar_g": "7.1",
                "measured_power_kw": "225",
            },
            {
                "unit_code": "AC-02",
                "timestamp_label": "T1",
                "operating_state": "UNLOADED",
                "measured_flow_nm3_per_hr": "100",
                "measured_discharge_pressure_bar_g": "7.1",
                "measured_power_kw": "80",
            },
            {
                "unit_code": "AC-01",
                "timestamp_label": "T2",
                "operating_state": "LOADED",
                "measured_flow_nm3_per_hr": "1600",
                "measured_discharge_pressure_bar_g": "7.0",
                "measured_power_kw": "230",
            },
            {
                "unit_code": "AC-02",
                "timestamp_label": "T2",
                "operating_state": "UNLOADED",
                "measured_flow_nm3_per_hr": "120",
                "measured_discharge_pressure_bar_g": "7.0",
                "measured_power_kw": "82",
            },
        ],
        "system_measurements": [
            {
                "timestamp_label": "T1",
                "total_flow_nm3_per_hr": "2200",
                "header_pressure_bar_g": "7.1",
                "total_power_kw": "340",
                "production_state": "LOW",
            },
            {
                "timestamp_label": "T2",
                "total_flow_nm3_per_hr": "3000",
                "header_pressure_bar_g": "7.0",
                "total_power_kw": "450",
                "production_state": "NORMAL",
            },
            {
                "timestamp_label": "T3",
                "total_flow_nm3_per_hr": "4000",
                "header_pressure_bar_g": "6.9",
                "total_power_kw": "580",
                "production_state": "PEAK",
            },
        ],
        "leakage_summary": {
            "measured_leakage_flow_nm3_per_hr": "450",
            "survey_method": "Plant shutdown flow test",
            "estimated_repair_fraction": "0.80",
        },
        "electricity_tariff_per_kwh": "8",
        "annual_operating_hours": "8000",
        "optimized_discharge_pressure_bar_g": "6.5",
        "expected_leak_repair_fraction": "0.80",
        "power_penalty_fraction_per_bar": "0.07",
    }


def test_brownfield_audit_endpoint() -> None:
    response = client.post(
        "/api/v1/compressed-air/brownfield/audit",
        json=build_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["audit_code"] == "BF-API-001"
    assert data["project_id"] == 1

    assert data["installed_capacity_nm3_per_hr"] == "5400"
    assert data["available_capacity_nm3_per_hr"] == "5400"

    assert float(data["average_system_flow_nm3_per_hr"]) > 0
    assert data["peak_system_flow_nm3_per_hr"] == "4000"

    assert float(data["average_system_power_kw"]) > 0
    assert float(data["measured_specific_power_kw_per_nm3_per_min"]) > 0

    assert data["high_unloaded_running_detected"] is True
    assert data["significant_leakage_detected"] is True

    assert float(data["current_annual_energy_kwh"]) > 0
    assert float(data["current_annual_energy_cost"]) > 0

    assert float(data["estimated_total_power_saving_kw"]) > 0
    assert float(data["estimated_total_annual_energy_saving_kwh"]) > 0
    assert float(data["estimated_total_annual_cost_saving"]) > 0

    assert float(data["estimated_optimized_annual_energy_kwh"]) < float(
        data["current_annual_energy_kwh"]
    )

    assert data["opportunities"]


def test_brownfield_without_pressure_optimization() -> None:
    request = build_request()

    request["optimized_discharge_pressure_bar_g"] = None

    response = client.post(
        "/api/v1/compressed-air/brownfield/audit",
        json=request,
    )

    assert response.status_code == 200

    data = response.json()

    categories = {item["category"] for item in data["opportunities"]}

    assert "PRESSURE" not in categories


def test_invalid_project_id_returns_422() -> None:
    request = build_request()

    request["project_id"] = 0

    response = client.post(
        "/api/v1/compressed-air/brownfield/audit",
        json=request,
    )

    assert response.status_code == 422


def test_invalid_leak_repair_fraction_returns_422() -> None:
    request = build_request()

    request["expected_leak_repair_fraction"] = "1.10"

    response = client.post(
        "/api/v1/compressed-air/brownfield/audit",
        json=request,
    )

    assert response.status_code == 422


def test_empty_system_measurements_returns_422() -> None:
    request = build_request()

    request["system_measurements"] = []

    response = client.post(
        "/api/v1/compressed-air/brownfield/audit",
        json=request,
    )

    assert response.status_code == 422
