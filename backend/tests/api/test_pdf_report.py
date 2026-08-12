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


def create_project(headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": "KESC-PDF-API-001",
            "project_name": "PDF Report API Test Project",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_completed_case(
    project_id: int,
    headers: dict[str, str],
) -> int:
    response = client.post(
        "/api/v1/calculation-cases",
        headers=headers,
        json={
            "project_id": project_id,
            "calculation_code": "PDF-API-CALC-001",
            "calculation_type": "CENTRIFUGAL",
            "status": "COMPLETED",
            "revision": 3,
            "title": "Centrifugal Compressor PDF Report",
            "description": "PDF report endpoint test.",
            "input_data": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
                "mass_flow_kg_per_s": "93.376",
            },
            "result_data": {
                "polytropic_head_kj_per_kg": "155.667",
                "required_driver_power_kw": "21011.32",
                "status": "PASS",
            },
            "engineering_notes": "Reviewed before PDF export.",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_download_calculation_pdf() -> None:
    reset_data()

    _, _, headers = prepare_authenticated_tenant(client)
    project_id = create_project(headers)
    calculation_case_id = create_completed_case(
        project_id,
        headers,
    )

    response = client.get(f"/api/v1/pdf-report/calculation-cases/{calculation_case_id}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    content_disposition = response.headers["content-disposition"]

    assert "attachment" in content_disposition
    assert "PDF-API-CALC-001_rev3.pdf" in content_disposition

    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 1000


def test_missing_pdf_report_case_returns_404() -> None:
    reset_data()

    response = client.get("/api/v1/pdf-report/calculation-cases/999999")

    assert response.status_code == 404


def test_pdf_endpoint_returns_non_empty_document() -> None:
    reset_data()

    _, _, headers = prepare_authenticated_tenant(client)
    project_id = create_project(headers)
    calculation_case_id = create_completed_case(
        project_id,
        headers,
    )

    response = client.get(f"/api/v1/pdf-report/calculation-cases/{calculation_case_id}")

    assert response.status_code == 200
    assert len(response.content) > 1000
    assert response.content[:5] == b"%PDF-"
