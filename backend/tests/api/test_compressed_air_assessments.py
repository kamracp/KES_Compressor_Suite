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
            "project_code": f"ASSESS-{uuid4().hex[:8]}",
            "project_name": "Compressed Air Assessment Test Project",
        },
    )

    assert response.status_code == 201

    return organization, headers, response.json()["id"]


def build_payload(
    *,
    project_id: int,
    assessment_code: str | None = None,
    assessment_type: str = "GREENFIELD",
) -> dict:
    return {
        "project_id": project_id,
        "assessment_code": assessment_code or f"CA-{uuid4().hex[:10]}",
        "assessment_type": assessment_type,
        "status": "DRAFT",
        "title": "Compressed Air Engineering Assessment",
        "engineering_basis": ("Vendor-neutral factory compressed-air engineering assessment."),
        "input_payload": {
            "required_flow_nm3_per_hr": "3000",
            "required_pressure_bar_g": "7.0",
        },
        "result_payload": {
            "recommended_flow_nm3_per_hr": "3300",
            "system_feasible": True,
        },
        "standards_snapshot": {
            "formal_compliance_claim_available": False,
        },
        "calculation_version": "S11-M37",
        "created_by": "test-suite",
    }


def create_assessment(
    *,
    headers: dict[str, str],
    project_id: int,
    assessment_type: str = "GREENFIELD",
    assessment_code: str | None = None,
) -> dict:
    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=build_payload(
            project_id=project_id,
            assessment_type=assessment_type,
            assessment_code=assessment_code,
        ),
    )

    assert response.status_code == 201
    return response.json()


def test_create_assessment() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    payload = build_payload(project_id=project_id)

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["project_id"] == project_id
    assert data["assessment_code"] == payload["assessment_code"]
    assert data["assessment_type"] == "GREENFIELD"
    assert data["status"] == "DRAFT"


def test_get_assessment_by_id() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = client.get(
        f"/api/v1/compressed-air/assessments/{assessment['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == assessment["id"]


def test_project_history_lists_assessments() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    first = create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="GREENFIELD",
    )

    second = create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="BROWNFIELD",
    )

    response = client.get(
        f"/api/v1/compressed-air/assessments/project/{project_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == project_id
    assert data["total"] == 2

    codes = {item["assessment_code"] for item in data["items"]}

    assert first["assessment_code"] in codes
    assert second["assessment_code"] in codes


def test_project_history_can_filter_by_type() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="GREENFIELD",
    )

    create_assessment(
        headers=headers,
        project_id=project_id,
        assessment_type="BROWNFIELD",
    )

    response = client.get(
        f"/api/v1/compressed-air/assessments/project/{project_id}",
        headers=headers,
        params={
            "assessment_type": "GREENFIELD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"]
    assert all(item["assessment_type"] == "GREENFIELD" for item in data["items"])


def test_status_update() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = client.patch(
        f"/api/v1/compressed-air/assessments/{assessment['id']}/status",
        headers=headers,
        json={
            "status": "COMPLETED",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_duplicate_assessment_code_returns_409() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    code = f"CA-DUP-{uuid4().hex[:8]}"

    payload = build_payload(
        project_id=project_id,
        assessment_code=code,
    )

    first = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    second = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_unknown_assessment_returns_404() -> None:
    reset_data()
    _, headers, _ = prepare_context()

    response = client.get(
        "/api/v1/compressed-air/assessments/999999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_invalid_project_id_returns_422() -> None:
    reset_data()
    _, headers, _ = prepare_context()

    payload = build_payload(project_id=1)
    payload["project_id"] = 0

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_assessment_type_returns_422() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    payload = build_payload(project_id=project_id)
    payload["assessment_type"] = "INVALID"

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_status_update_returns_422() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = client.patch(
        f"/api/v1/compressed-air/assessments/{assessment['id']}/status",
        headers=headers,
        json={
            "status": "INVALID",
        },
    )

    assert response.status_code == 422


def test_assessment_endpoint_requires_authentication() -> None:
    reset_data()

    response = client.get("/api/v1/compressed-air/assessments/999999999")

    assert response.status_code == 401


def test_cross_tenant_project_creation_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=second_headers,
        json=build_payload(
            project_id=first_project_id,
        ),
    )

    assert response.status_code == 404


def test_cross_tenant_assessment_read_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    assessment = create_assessment(
        headers=first_headers,
        project_id=first_project_id,
    )

    response = client.get(
        f"/api/v1/compressed-air/assessments/{assessment['id']}",
        headers=second_headers,
    )

    assert response.status_code == 404


def test_cross_tenant_status_update_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    assessment = create_assessment(
        headers=first_headers,
        project_id=first_project_id,
    )

    response = client.patch(
        f"/api/v1/compressed-air/assessments/{assessment['id']}/status",
        headers=second_headers,
        json={
            "status": "COMPLETED",
        },
    )

    assert response.status_code == 404
