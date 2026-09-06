"""C-7d: sequencing proposal carried inside the brownfield audit request."""

from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from tests.api.test_compressed_air_brownfield import build_request

client = TestClient(app)

URL = "/api/v1/compressed-air/brownfield/audit"


def settings(low: str, high: str, priority: int) -> dict:
    return {
        "band": {"load_pressure_bar_g": low, "unload_pressure_bar_g": high},
        "unload_power_fraction": "0.25",
        "priority": priority,
    }


def request_with_proposal() -> dict:
    body = build_request()
    bands = [("6.6", "7.4"), ("6.5", "7.3"), ("6.4", "7.2")]
    for index, (item, (low, high)) in enumerate(zip(body["compressors"], bands, strict=True)):
        item["sequencing"] = settings(low, high, index + 1)
    body["sequencing_proposal"] = {
        "proposed_band": {"load_pressure_bar_g": "6.5", "unload_pressure_bar_g": "7.0"},
        "receiver_volume_m3": "10",
    }
    return body


def test_audit_with_proposal_returns_assessment_and_opportunity() -> None:
    body = request_with_proposal()
    response = client.post(URL, json=body)
    assert response.status_code == 200, response.json()

    data = response.json()
    assessment = data["sequencing_assessment"]
    assert assessment is not None
    assert assessment["analysis_code"] == "BF-API-001-SEQ"
    assert Decimal(assessment["profile_hours"]) == len(body["system_measurements"])
    assert [m["unit_code"] for m in assessment["proposed_machines"]] == ["AC-01", "AC-02", "AC-03"]

    codes = [o["opportunity_code"] for o in data["opportunities"]]
    assert "CENTRAL-SEQUENCER" in codes


def test_audit_without_proposal_has_no_assessment() -> None:
    response = client.post(URL, json=build_request())
    assert response.status_code == 200

    data = response.json()
    assert data["sequencing_assessment"] is None
    assert "CENTRAL-SEQUENCER" not in [o["opportunity_code"] for o in data["opportunities"]]


def test_missing_settings_on_available_unit_returns_422() -> None:
    body = request_with_proposal()
    del body["compressors"][2]["sequencing"]

    response = client.post(URL, json=body)
    assert response.status_code == 422
    assert "AC-03" in response.json()["detail"]


def test_unload_fraction_outside_doe_range_returns_422() -> None:
    body = request_with_proposal()
    body["compressors"][0]["sequencing"]["unload_power_fraction"] = "0.5"

    assert client.post(URL, json=body).status_code == 422


def test_vsd_unit_without_minimum_flow_fields_returns_422() -> None:
    body = request_with_proposal()
    body["compressors"][0]["control_mode"] = "VSD"

    assert client.post(URL, json=body).status_code == 422


def test_modulation_unit_returns_422_as_c8_scope() -> None:
    body = request_with_proposal()
    body["compressors"][0]["control_mode"] = "MODULATION"

    response = client.post(URL, json=body)
    assert response.status_code == 422
    assert "C-8" in response.json()["detail"]
