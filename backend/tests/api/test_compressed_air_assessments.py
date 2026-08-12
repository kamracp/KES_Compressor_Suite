from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.main import app
from tests.helpers.tenant_context import ensure_test_organization_id

client = TestClient(app)


def ensure_test_project_id() -> int:
    """Ensure that the tests have a tenant-owned parent project."""

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        project_id = db.execute(
            text(
                """
                INSERT INTO projects (
                    organization_id,
                    project_code,
                    project_name,
                    client_name,
                    plant_name,
                    location,
                    service_description,
                    status
                )
                VALUES (
                    :organization_id,
                    :project_code,
                    :project_name,
                    'Engineering Test',
                    'Test Plant',
                    'Test Environment',
                    'Automated compressed-air regression testing',
                    'ACTIVE'
                )
                ON CONFLICT (organization_id, project_code)
                DO UPDATE SET
                    project_name = EXCLUDED.project_name,
                    status = EXCLUDED.status
                RETURNING id
                """
            ),
            {
                "organization_id": organization_id,
                "project_code": "TEST-CAS-S11",
                "project_name": "Compressed Air S11 Test Project",
            },
        ).scalar_one()

        db.commit()

    return int(project_id)


def build_payload(
    *,
    assessment_code: str | None = None,
    assessment_type: str = "GREENFIELD",
) -> dict:
    code = assessment_code or f"CA-{uuid4().hex[:10]}"

    return {
        "project_id": ensure_test_project_id(),
        "assessment_code": code,
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


def test_create_assessment() -> None:
    payload = build_payload()

    response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["project_id"] == payload["project_id"]
    assert data["assessment_code"] == payload["assessment_code"]
    assert data["assessment_type"] == "GREENFIELD"
    assert data["status"] == "DRAFT"

    assert data["input_payload"] == payload["input_payload"]
    assert data["result_payload"] == payload["result_payload"]

    assert data["standards_snapshot"] == payload["standards_snapshot"]
    assert data["calculation_version"] == "S11-M37"


def test_get_assessment_by_id() -> None:
    payload = build_payload()

    create_response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert create_response.status_code == 201

    assessment_id = create_response.json()["id"]

    response = client.get(f"/api/v1/compressed-air/assessments/{assessment_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == assessment_id
    assert data["assessment_code"] == payload["assessment_code"]


def test_project_history_lists_assessments() -> None:
    first = build_payload(
        assessment_type="GREENFIELD",
    )

    second = build_payload(
        assessment_type="BROWNFIELD",
    )

    assert first["project_id"] == second["project_id"]

    assert (
        client.post(
            "/api/v1/compressed-air/assessments",
            json=first,
        ).status_code
        == 201
    )

    assert (
        client.post(
            "/api/v1/compressed-air/assessments",
            json=second,
        ).status_code
        == 201
    )

    project_id = first["project_id"]

    response = client.get(f"/api/v1/compressed-air/assessments/project/{project_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == project_id
    assert data["total"] >= 2

    codes = {item["assessment_code"] for item in data["items"]}

    assert first["assessment_code"] in codes
    assert second["assessment_code"] in codes


def test_project_history_can_filter_by_type() -> None:
    greenfield = build_payload(
        assessment_type="GREENFIELD",
    )

    brownfield = build_payload(
        assessment_type="BROWNFIELD",
    )

    assert greenfield["project_id"] == brownfield["project_id"]

    assert (
        client.post(
            "/api/v1/compressed-air/assessments",
            json=greenfield,
        ).status_code
        == 201
    )

    assert (
        client.post(
            "/api/v1/compressed-air/assessments",
            json=brownfield,
        ).status_code
        == 201
    )

    project_id = greenfield["project_id"]

    response = client.get(
        f"/api/v1/compressed-air/assessments/project/{project_id}",
        params={
            "assessment_type": "GREENFIELD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"]

    assert all(item["assessment_type"] == "GREENFIELD" for item in data["items"])


def test_status_update() -> None:
    payload = build_payload()

    create_response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert create_response.status_code == 201

    assessment_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/compressed-air/assessments/{assessment_id}/status",
        json={
            "status": "COMPLETED",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_duplicate_assessment_code_returns_409() -> None:
    code = f"CA-DUP-{uuid4().hex[:8]}"

    payload = build_payload(
        assessment_code=code,
    )

    first = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert second.status_code == 409
    assert "already exists" in second.json()["detail"]


def test_unknown_assessment_returns_404() -> None:
    response = client.get("/api/v1/compressed-air/assessments/999999999")

    assert response.status_code == 404


def test_invalid_project_id_returns_422() -> None:
    payload = build_payload()
    payload["project_id"] = 0

    response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_assessment_type_returns_422() -> None:
    payload = build_payload()
    payload["assessment_type"] = "INVALID"

    response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_status_update_returns_422() -> None:
    payload = build_payload()

    create_response = client.post(
        "/api/v1/compressed-air/assessments",
        json=payload,
    )

    assert create_response.status_code == 201

    assessment_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/compressed-air/assessments/{assessment_id}/status",
        json={
            "status": "INVALID",
        },
    )

    assert response.status_code == 422
