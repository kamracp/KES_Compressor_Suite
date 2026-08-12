from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.compressed_air_assessment import CompressedAirAssessment
from app.models.project import Project
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CompressedAirAssessment))
        db.execute(delete(Project))
        db.commit()


def prepare_context() -> tuple[dict, dict[str, str], int]:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": f"SYS-{uuid4().hex[:8]}",
            "project_name": "Compressed Air System Summary Test Project",
        },
    )

    assert response.status_code == 201

    return organization, headers, response.json()["id"]


def create_assessment(
    *,
    headers: dict[str, str],
    project_id: int,
    assessment_type: str = "GREENFIELD",
) -> dict:
    payload = {
        "project_id": project_id,
        "assessment_code": f"CA-SYS-{uuid4().hex[:10]}",
        "assessment_type": assessment_type,
        "status": "COMPLETED",
        "title": "Compressed Air Engineering Assessment",
        "engineering_basis": ("Vendor-neutral compressed-air engineering basis."),
        "input_payload": {
            "design_basis": {
                "required_flow_nm3_per_hr": "3000",
                "required_pressure_bar_g": "7.0",
            }
        },
        "result_payload": {
            "demand_and_capacity": {
                "design_flow_nm3_per_hr": "3300",
            },
            "pressure": {
                "minimum_required_pressure_bar_g": "7.0",
            },
            "air_treatment": {
                "required_pressure_dew_point_c": "3",
            },
            "storage": {
                "receiver_volume_m3": "5",
            },
            "distribution": {
                "maximum_pressure_drop_bar": "0.3",
            },
            "energy": {
                "annual_energy_kwh": "1000000",
            },
            "equipment_selection": {
                "selection_basis": "vendor-neutral",
            },
            "recommendations": {
                "items": [
                    "Monitor system specific power.",
                    "Maintain the lowest practical operating pressure.",
                ]
            },
        },
        "standards_snapshot": {
            "formal_compliance_claim_available": False,
        },
        "calculation_version": "S11-M39",
        "created_by": "test-suite",
    }

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


def get_summary(
    *,
    headers: dict[str, str],
    assessment_id: int,
):
    return client.get(
        f"/api/v1/compressed-air/system-summary/assessment/{assessment_id}",
        headers=headers,
    )


def test_build_system_summary_from_assessment() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == assessment["project_id"]
    assert data["assessment_mode"] == "GREENFIELD"
    assert data["assessment_code"] == assessment["assessment_code"]
    assert data["calculation_version"] == "S11-M39"
    assert data["available_capability_count"] > 0
    assert data["total_capability_count"] == 13


def test_summary_preserves_vendor_neutral_equipment_information() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    equipment = next(
        item for item in response.json()["capabilities"] if item["name"] == "equipment"
    )

    assert equipment["available"] is True
    assert equipment["data"]["selection_basis"] == "vendor-neutral"


def test_summary_contains_energy_capability() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    energy = next(item for item in response.json()["capabilities"] if item["name"] == "energy")

    assert energy["available"] is True
    assert energy["data"]["annual_energy_kwh"] == "1000000"


def test_summary_contains_persistence_capability() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    persistence = next(
        item for item in response.json()["capabilities"] if item["name"] == "persistence"
    )

    assert persistence["available"] is True
    assert persistence["data"]["assessment_id"] == assessment["id"]
    assert persistence["data"]["status"] == "COMPLETED"


def test_summary_marks_integrated_report_available() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["integrated_report_available"] is True

    report = next(item for item in data["capabilities"] if item["name"] == "integrated_report")

    assert report["available"] is True


def test_summary_preserves_recommendations() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    assert "Monitor system specific power." in recommendations
    assert "Maintain the lowest practical operating pressure." in recommendations


def test_summary_does_not_infer_formal_compliance_claim() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False
    assert any(
        "no formal standards compliance claim" in warning.lower() for warning in data["warnings"]
    )


def test_greenfield_mode_is_mapped() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="GREENFIELD",
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200
    assert response.json()["assessment_mode"] == "GREENFIELD"


def test_brownfield_mode_is_mapped() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="BROWNFIELD",
    )

    response = get_summary(
        headers=headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 200
    assert response.json()["assessment_mode"] == "BROWNFIELD"


def test_unknown_assessment_returns_404() -> None:
    reset_data()
    _, headers, _ = prepare_context()

    response = get_summary(
        headers=headers,
        assessment_id=999999999,
    )

    assert response.status_code == 404


def test_system_summary_requires_authentication() -> None:
    reset_data()

    response = client.get("/api/v1/compressed-air/system-summary/assessment/999999999")

    assert response.status_code == 401


def test_cross_tenant_system_summary_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    assessment = create_assessment(
        headers=first_headers,
        project_id=first_project_id,
    )

    response = get_summary(
        headers=second_headers,
        assessment_id=assessment["id"],
    )

    assert response.status_code == 404
