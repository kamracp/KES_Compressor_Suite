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
            "project_code": "KESC-EXPORT-API-001",
            "project_name": "Report Export API Test Project",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_completed_case(project_id: int) -> int:
    response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "EXPORT-API-CALC-001",
            "calculation_type": "CENTRIFUGAL",
            "status": "COMPLETED",
            "revision": 2,
            "title": "Centrifugal Export API Case",
            "description": "JSON export endpoint test.",
            "input_data": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
            },
            "result_data": {
                "required_driver_power_kw": "21011.32",
                "status": "PASS",
            },
            "engineering_notes": "Reviewed before JSON export.",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_export_calculation_case_json() -> None:
    reset_data()

    project_id = create_project()
    calculation_case_id = create_completed_case(project_id)

    response = client.get(f"/api/v1/report-export/calculation-cases/{calculation_case_id}/json")

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] == calculation_case_id
    assert data["project_id"] == project_id
    assert data["calculation_code"] == "EXPORT-API-CALC-001"
    assert data["calculation_type"] == "CENTRIFUGAL"
    assert data["status"] == "COMPLETED"
    assert data["revision"] == 2

    assert data["title"] == "Centrifugal Export API Case"
    assert data["description"] == "JSON export endpoint test."

    assert data["input_data"]["suction_pressure_bar"] == "30"
    assert data["input_data"]["discharge_pressure_bar"] == "90"

    assert data["result_data"]["required_driver_power_kw"] == "21011.32"
    assert data["result_data"]["status"] == "PASS"

    assert data["engineering_notes"] == "Reviewed before JSON export."
    assert data["completed_at"] is not None


def test_missing_export_case_returns_404() -> None:
    reset_data()

    response = client.get("/api/v1/report-export/calculation-cases/999999/json")

    assert response.status_code == 404
