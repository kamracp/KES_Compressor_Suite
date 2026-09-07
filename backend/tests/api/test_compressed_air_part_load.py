from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)

URL = "/api/v1/compressed-air/performance/part-load"


def body() -> dict:
    return {
        "analysis_code": "PL-API-001",
        "rated_fad_nm3_per_hr": "1000",
        "rated_power_kw": "100",
        "candidates": [
            {"label": "load/unload", "mode": "LOAD_UNLOAD", "unload_power_fraction": "0.25"},
            {"label": "modulation", "mode": "MODULATION", "unload_power_fraction": "0.25"},
            {
                "label": "igv",
                "mode": "INLET_GUIDE_VANE",
                "turndown_flow_fraction": "0.25",
                "power_fraction_at_turndown": "0.8",
            },
        ],
        "load_duration": [{"capacity_fraction": "0.5", "hours": "4000"}],
        "electricity_tariff_per_kwh": "7",
    }


def test_part_load_comparison_returns_curves_and_winners() -> None:
    _, _, headers = prepare_authenticated_tenant(client)
    response = client.post(URL, headers=headers, json=body())
    assert response.status_code == 200, response.json()

    data = response.json()
    by_label = {c["label"]: c for c in data["candidates"]}
    assert by_label["modulation"]["points"][1]["power_kw"] == "85.0000"
    assert by_label["igv"]["points"][1]["regime"] == "blow-off"
    assert by_label["igv"]["annual_blow_off_volume_nm3"] == "1000000.0000"
    assert data["lowest_annual_energy_label"] == "load/unload"
    assert data["profile_hours"] == "4000.0000"


def test_screw_mode_without_unload_fraction_returns_422() -> None:
    _, _, headers = prepare_authenticated_tenant(client)
    payload = body()
    del payload["candidates"][0]["unload_power_fraction"]

    response = client.post(URL, headers=headers, json=payload)
    assert response.status_code == 422
    assert "load/unload: unload_power_fraction" in response.json()["detail"]


def test_unauthenticated_returns_401() -> None:
    assert client.post(URL, json=body()).status_code == 401
