from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.calculation_case import CalculationCase
from app.models.project import Project
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def prepare_context() -> dict[str, str]:
    _, _, headers = prepare_authenticated_tenant(client)
    return headers


def create_project(
    *,
    headers: dict[str, str],
) -> int:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": "KESC-HIST-API-001",
            "project_name": "Project History API Test",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_case(
    *,
    headers: dict[str, str],
    project_id: int,
    calculation_code: str,
    calculation_type: str,
    status: str,
    revision: int,
    title: str,
) -> int:
    response = client.post(
        "/api/v1/calculation-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "calculation_code": calculation_code,
            "calculation_type": calculation_type,
            "status": status,
            "revision": revision,
            "title": title,
            "input_data": {},
            "result_data": ({"status": "PASS"} if status == "COMPLETED" else None),
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_get_project_calculation_history() -> None:
    reset_data()
    headers = prepare_context()

    project_id = create_project(
        headers=headers,
    )

    first_case_id = create_case(
        headers=headers,
        project_id=project_id,
        calculation_code="HIST-API-001",
        calculation_type="SELECTION",
        status="COMPLETED",
        revision=1,
        title="Selection Case",
    )

    second_case_id = create_case(
        headers=headers,
        project_id=project_id,
        calculation_code="HIST-API-002",
        calculation_type="CENTRIFUGAL",
        status="DRAFT",
        revision=1,
        title="Draft Centrifugal Case",
    )

    response = client.get(
        f"/api/v1/projects/{project_id}/calculation-history",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == project_id
    assert data["total_cases"] == 2
    assert data["completed_cases"] == 1
    assert data["draft_cases"] == 1
    assert data["latest_case_id"] == second_case_id
    assert data["latest_completed_case_id"] == first_case_id
    assert len(data["items"]) == 2


def test_empty_project_history() -> None:
    reset_data()
    headers = prepare_context()

    project_id = create_project(
        headers=headers,
    )

    response = client.get(
        f"/api/v1/projects/{project_id}/calculation-history",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == project_id
    assert data["total_cases"] == 0
    assert data["completed_cases"] == 0
    assert data["draft_cases"] == 0
    assert data["latest_case_id"] is None
    assert data["latest_completed_case_id"] is None
    assert data["items"] == []


def test_missing_project_returns_404() -> None:
    reset_data()
    headers = prepare_context()

    response = client.get(
        "/api/v1/projects/999999/calculation-history",
        headers=headers,
    )

    assert response.status_code == 404
