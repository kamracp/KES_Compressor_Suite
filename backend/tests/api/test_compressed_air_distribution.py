from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.calculation_case import CalculationCase
from app.models.project import Project
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)

CALCULATE_ENDPOINT = "/api/v1/compressed-air/distribution/calculate"
EXECUTE_ENDPOINT = "/api/v1/compressed-air/distribution/execute"


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def build_calculation_payload(
    *,
    with_candidates: bool = False,
) -> dict:
    payload: dict = {
        "network_code": "NET-API-001",
        "topology": "DEAD_END",
        "design_source_pressure_bar_g": "7.5",
        "air_density_kg_per_m3": "8.5",
        "darcy_friction_factor": "0.02",
        "nodes": [
            {
                "node_code": "CS-01",
                "name": "Compressor Station",
                "node_type": "COMPRESSOR_STATION",
            },
            {
                "node_code": "HJ-01",
                "name": "Main Header Junction",
                "node_type": "HEADER_JUNCTION",
            },
            {
                "node_code": "CN-01",
                "name": "Assembly Line Consumer",
                "node_type": "CONSUMER",
                "demand_nm3_per_hr": "600",
                "minimum_pressure_bar_g": "6.0",
            },
        ],
        "segments": [
            {
                "segment_code": "SEG-01",
                "name": "Station to Header",
                "role": "MAIN_HEADER",
                "start_node_code": "CS-01",
                "end_node_code": "HJ-01",
                "length_m": "60",
                "equivalent_fitting_length_m": "12",
                "internal_diameter_mm": "80",
                "roughness_mm": "0.045",
                "design_flow_nm3_per_hr": "600",
                "operating_pressure_bar_g": "7.5",
                "operating_temperature_k": "308.15",
            },
            {
                "segment_code": "SEG-02",
                "name": "Header to Consumer",
                "role": "BRANCH",
                "start_node_code": "HJ-01",
                "end_node_code": "CN-01",
                "length_m": "40",
                "equivalent_fitting_length_m": "8",
                "internal_diameter_mm": "50",
                "roughness_mm": "0.045",
                "design_flow_nm3_per_hr": "600",
                "operating_pressure_bar_g": "7.3",
                "operating_temperature_k": "308.15",
            },
        ],
        "paths": [
            {
                "path_code": "PATH-01",
                "node_codes": ["CS-01", "HJ-01", "CN-01"],
                "segment_codes": ["SEG-01", "SEG-02"],
            },
        ],
    }

    if with_candidates:
        payload["candidate_internal_diameters_mm"] = [
            "50",
            "65",
            "80",
            "100",
            "125",
        ]

    return payload


def test_calculate_returns_validation_and_hydraulics() -> None:
    response = client.post(
        CALCULATE_ENDPOINT,
        json=build_calculation_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    validation = body["validation"]
    assert validation["network_code"] == "NET-API-001"
    assert validation["is_structurally_valid"] is True
    assert validation["node_count"] == 3
    assert validation["segment_count"] == 2
    assert validation["source_node_count"] == 1
    assert validation["consumer_node_count"] == 1

    hydraulics = body["hydraulics"]
    assert hydraulics["total_paths"] == 1
    assert hydraulics["worst_pressure_path_code"] == "PATH-01"
    assert as_decimal(hydraulics["maximum_path_pressure_drop_bar"]) > 0

    path_result = hydraulics["path_results"][0]
    assert path_result["source_node_code"] == "CS-01"
    assert path_result["destination_node_code"] == "CN-01"
    assert len(path_result["segment_results"]) == 2

    destination_pressure = as_decimal(path_result["destination_pressure_bar_g"])
    total_drop = as_decimal(path_result["total_pressure_drop_bar"])
    assert destination_pressure == as_decimal("7.5") - total_drop

    assert body["optimization"] is None


def test_calculate_runs_optimization_when_candidates_supplied() -> None:
    response = client.post(
        CALCULATE_ENDPOINT,
        json=build_calculation_payload(with_candidates=True),
    )

    assert response.status_code == 200

    body = response.json()

    optimization = body["optimization"]
    assert optimization is not None
    assert optimization["network_code"] == "NET-API-001"
    assert isinstance(optimization["optimization_required"], bool)
    assert isinstance(optimization["recommendations"], list)


def test_calculate_rejects_orphan_segment() -> None:
    payload = build_calculation_payload()
    payload["segments"][1]["end_node_code"] = "MISSING-NODE"

    response = client.post(
        CALCULATE_ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422
    assert "structurally valid" in response.json()["detail"]


def test_calculate_rejects_unknown_path_segment() -> None:
    payload = build_calculation_payload()
    payload["paths"][0]["segment_codes"] = ["SEG-01", "SEG-MISSING"]

    response = client.post(
        CALCULATE_ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422


def test_execute_requires_authentication() -> None:
    response = client.post(
        EXECUTE_ENDPOINT,
        json={
            "calculation": build_calculation_payload(),
            "execution": {"persist_result": False},
        },
    )

    assert response.status_code in (401, 403)


def test_execute_persists_distribution_calculation_case() -> None:
    reset_data()

    _, _, headers = prepare_authenticated_tenant(client)

    project_response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": "KESC-DIST-API-001",
            "project_name": "Distribution Network API Test",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    response = client.post(
        EXECUTE_ENDPOINT,
        headers=headers,
        json={
            "calculation": build_calculation_payload(),
            "execution": {
                "persist_result": True,
                "project_id": project_id,
                "calculation_code": "DIST-CALC-001",
                "title": "Plant Air Distribution Analysis",
            },
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["calculation_case_id"] is not None
    assert body["result"]["validation"]["is_structurally_valid"] is True

    case_response = client.get(
        f"/api/v1/calculation-cases/{body['calculation_case_id']}",
        headers=headers,
    )
    assert case_response.status_code == 200
    case = case_response.json()
    assert case["calculation_type"] == "DISTRIBUTION"
    assert case["status"] == "COMPLETED"


def test_preferred_velocity_default_is_bcas_cagi_calibrated() -> None:
    from decimal import Decimal as _Decimal

    from app.schemas.compressed_air_distribution import (
        DistributionNetworkCalculationRequest,
    )

    field = DistributionNetworkCalculationRequest.model_fields["maximum_preferred_velocity_m_per_s"]

    assert field.default == _Decimal("6")
