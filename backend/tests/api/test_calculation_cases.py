from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.calculation_case import CalculationCase
from app.models.project import Project

client = TestClient(app)


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def create_project() -> int:
    response = client.post(
        "/api/v1/projects",
        json={
            "project_code": "KESC-CALC-PROJECT",
            "project_name": "Calculation Case Test Project",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_calculation_case() -> None:
    reset_data()
    project_id = create_project()

    response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-001",
            "calculation_type": "CENTRIFUGAL",
            "title": "Centrifugal Design Case",
            "input_data": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
            },
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["calculation_code"] == "CALC-001"
    assert data["calculation_type"] == "CENTRIFUGAL"
    assert data["status"] == "DRAFT"
    assert data["revision"] == 1
    assert data["project_id"] == project_id


def test_list_calculation_cases() -> None:
    reset_data()
    project_id = create_project()

    client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-002",
            "calculation_type": "COMPRESSION",
            "title": "Compression Case",
            "input_data": {},
        },
    )

    response = client.get("/api/v1/calculation-cases")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["calculation_code"] == "CALC-002"


def test_get_calculation_case() -> None:
    reset_data()
    project_id = create_project()

    create_response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-003",
            "calculation_type": "RECIPROCATING",
            "title": "Reciprocating Case",
            "input_data": {},
        },
    )

    calculation_case_id = create_response.json()["id"]

    response = client.get(f"/api/v1/calculation-cases/{calculation_case_id}")

    assert response.status_code == 200
    assert response.json()["calculation_code"] == "CALC-003"


def test_update_calculation_case() -> None:
    reset_data()
    project_id = create_project()

    create_response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-004",
            "calculation_type": "COMPRESSION",
            "title": "Original Case",
            "input_data": {},
        },
    )

    calculation_case_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/calculation-cases/{calculation_case_id}",
        json={
            "title": "Updated Case",
            "revision": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Case"
    assert data["revision"] == 2


def test_complete_calculation_case_sets_completed_at() -> None:
    reset_data()
    project_id = create_project()

    create_response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-005",
            "calculation_type": "CENTRIFUGAL",
            "title": "Completion Case",
            "input_data": {},
        },
    )

    calculation_case_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/calculation-cases/{calculation_case_id}",
        json={
            "status": "COMPLETED",
            "result_data": {
                "driver_power_kw": "21000",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["completed_at"] is not None


def test_duplicate_calculation_code_returns_conflict() -> None:
    reset_data()
    project_id = create_project()

    payload = {
        "project_id": project_id,
        "calculation_code": "CALC-006",
        "calculation_type": "COMPRESSION",
        "title": "Duplicate Case",
        "input_data": {},
    }

    first_response = client.post(
        "/api/v1/calculation-cases",
        json=payload,
    )
    second_response = client.post(
        "/api/v1/calculation-cases",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_missing_project_returns_not_found() -> None:
    reset_data()

    response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": 999999,
            "calculation_code": "CALC-007",
            "calculation_type": "COMPRESSION",
            "title": "Missing Project Case",
            "input_data": {},
        },
    )

    assert response.status_code == 404


def test_delete_calculation_case() -> None:
    reset_data()
    project_id = create_project()

    create_response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "CALC-008",
            "calculation_type": "COMPRESSION",
            "title": "Delete Case",
            "input_data": {},
        },
    )

    calculation_case_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/calculation-cases/{calculation_case_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/calculation-cases/{calculation_case_id}")

    assert get_response.status_code == 404
