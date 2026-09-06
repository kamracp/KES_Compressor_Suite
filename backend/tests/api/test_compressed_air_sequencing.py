from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)

URL = "/api/v1/compressed-air/sequencing/assess"


def machine(code: str, low: str, high: str, *, vsd: bool = False, idle: bool = False) -> dict:
    payload = {
        "unit_code": code,
        "control_mode": "VARIABLE_SPEED" if vsd else "FIXED_SPEED_LOAD_UNLOAD",
        "rated_fad_nm3_per_hr": "1000",
        "rated_power_kw": "100",
        "band": {"load_pressure_bar_g": low, "unload_pressure_bar_g": high},
        "unload_power_fraction": "0.2" if vsd else "0.25",
        "standby_runs_unloaded": idle,
    }
    if vsd:
        payload["minimum_flow_fraction"] = "0.3"
        payload["minimum_flow_power_fraction"] = "0.4"
    return payload


def request_body() -> dict:
    return {
        "analysis_code": "SEQ-API-001",
        "baseline_machines": [
            machine("A", "6.8", "7.3"),
            machine("B", "6.5", "7.0", idle=True),
            machine("C", "6.2", "6.7", vsd=True, idle=True),
        ],
        "demand_profile": [
            {
                "period_index": 1,
                "label": "shift",
                "demand_nm3_per_hr": "1500",
                "required_pressure_bar_g": "6",
                "duration_hours": "10",
            }
        ],
        "receiver_volume_m3": "1",
        "electricity_tariff_per_kwh": "8",
        "proposed_band": {"load_pressure_bar_g": "6.3", "unload_pressure_bar_g": "6.6"},
        "annual_operating_hours": "8000",
    }


def test_assess_sequencing_returns_component_savings() -> None:
    _, _, headers = prepare_authenticated_tenant(client)
    response = client.post(URL, headers=headers, json=request_body())
    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["baseline"]["periods"][0]["total_power_kw"] == "182.5000"
    assert data["proposed"]["periods"][0]["total_power_kw"] == "157.1429"
    assert [m["unit_code"] for m in data["proposed_machines"]] == ["A", "B", "C"]
    assert data["proposed_machines"][2]["control_mode"] == "VARIABLE_SPEED"
    assert data["standby_saving_kwh"] == "160000.0000"  # 20 kW x 10 h x 800
    assert data["saving_claimed"] is True
    assert data["total_annual_cost_saving"] != "0.0000"


def test_assess_sequencing_rejects_an_unload_fraction_outside_the_evidence_band() -> None:
    _, _, headers = prepare_authenticated_tenant(client)
    body = request_body()
    body["baseline_machines"][0]["unload_power_fraction"] = "0.5"
    response = client.post(URL, headers=headers, json=body)
    assert response.status_code == 422
    assert "unload_power_fraction" in response.text


def test_assess_sequencing_requires_authentication() -> None:
    assert client.post(URL, json=request_body()).status_code == 401
