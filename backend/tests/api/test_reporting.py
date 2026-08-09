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
            "project_code": "KESC-RPT-API-001",
            "project_name": "Reporting API Test Project",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_completed_case(project_id: int) -> int:
    response = client.post(
        "/api/v1/calculation-cases",
        json={
            "project_id": project_id,
            "calculation_code": "RPT-API-CALC-001",
            "calculation_type": "CENTRIFUGAL",
            "status": "COMPLETED",
            "revision": 2,
            "title": "Centrifugal Reporting API Case",
            "description": "Reporting endpoint test.",
            "input_data": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
            },
            "result_data": {
                "required_driver_power_kw": "21011.32",
                "status": "PASS",
            },
            "engineering_notes": "Reviewed calculation.",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_get_calculation_report() -> None:
    reset_data()

    project_id = create_project()
    calculation_case_id = create_completed_case(project_id)

    response = client.get(f"/api/v1/reporting/calculation-cases/{calculation_case_id}/report")

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] == calculation_case_id
    assert data["project_id"] == project_id
    assert data["calculation_code"] == "RPT-API-CALC-001"
    assert data["calculation_type"] == "CENTRIFUGAL"
    assert data["status"] == "COMPLETED"
    assert data["revision"] == 2
    assert data["title"] == "Centrifugal Reporting API Case"

    assert data["input_data"]["suction_pressure_bar"] == "30"
    assert data["result_data"]["required_driver_power_kw"] == "21011.32"
    assert data["engineering_notes"] == "Reviewed calculation."
    assert data["completed_at"] is not None


def test_get_calculation_audit_summary() -> None:
    reset_data()

    project_id = create_project()
    calculation_case_id = create_completed_case(project_id)

    response = client.get(
        f"/api/v1/reporting/calculation-cases/{calculation_case_id}/audit-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] == calculation_case_id
    assert data["project_id"] == project_id
    assert data["status"] == "COMPLETED"
    assert data["revision"] == 2

    assert data["is_completed"] is True
    assert data["has_result_data"] is True
    assert data["has_engineering_notes"] is True
    assert data["completed_at"] is not None


def test_missing_calculation_report_returns_404() -> None:
    reset_data()

    response = client.get("/api/v1/reporting/calculation-cases/999999/report")

    assert response.status_code == 404


def test_missing_audit_summary_returns_404() -> None:
    reset_data()

    response = client.get("/api/v1/reporting/calculation-cases/999999/audit-summary")

    assert response.status_code == 404
