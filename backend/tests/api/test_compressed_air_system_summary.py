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
                "project_code": "TEST-SYSTEM-S11",
                "project_name": "Compressed Air System Summary Test Project",
            },
        ).scalar_one()

        db.commit()

    return int(project_id)


def create_assessment(
    *,
    assessment_type: str = "GREENFIELD",
) -> dict:
    project_id = ensure_test_project_id()

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
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


def test_build_system_summary_from_assessment() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == assessment["project_id"]
    assert data["assessment_mode"] == "GREENFIELD"
    assert data["assessment_code"] == assessment["assessment_code"]
    assert data["calculation_version"] == "S11-M39"

    assert data["available_capability_count"] > 0
    assert data["total_capability_count"] == 13


def test_summary_preserves_vendor_neutral_equipment_information() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    equipment = next(item for item in data["capabilities"] if item["name"] == "equipment")

    assert equipment["available"] is True
    assert equipment["data"]["selection_basis"] == "vendor-neutral"


def test_summary_contains_energy_capability() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    energy = next(item for item in data["capabilities"] if item["name"] == "energy")

    assert energy["available"] is True
    assert energy["data"]["annual_energy_kwh"] == "1000000"


def test_summary_contains_persistence_capability() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    persistence = next(item for item in data["capabilities"] if item["name"] == "persistence")

    assert persistence["available"] is True
    assert persistence["data"]["assessment_id"] == assessment["id"]
    assert persistence["data"]["status"] == "COMPLETED"


def test_summary_marks_integrated_report_available() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["integrated_report_available"] is True

    report = next(item for item in data["capabilities"] if item["name"] == "integrated_report")

    assert report["available"] is True


def test_summary_preserves_recommendations() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert "Monitor system specific power." in data["recommendations"]

    assert "Maintain the lowest practical operating pressure." in data["recommendations"]


def test_summary_does_not_infer_formal_compliance_claim() -> None:
    assessment = create_assessment()

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False

    assert any(
        "no formal standards compliance claim" in warning.lower() for warning in data["warnings"]
    )


def test_greenfield_mode_is_mapped() -> None:
    assessment = create_assessment(
        assessment_type="GREENFIELD",
    )

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["assessment_mode"] == "GREENFIELD"

    greenfield = next(item for item in data["capabilities"] if item["name"] == "greenfield")

    assert greenfield["available"] is True


def test_brownfield_mode_is_mapped() -> None:
    assessment = create_assessment(
        assessment_type="BROWNFIELD",
    )

    response = client.get(f"/api/v1/compressed-air/system-summary/assessment/{assessment['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["assessment_mode"] == "BROWNFIELD"

    brownfield = next(item for item in data["capabilities"] if item["name"] == "brownfield")

    assert brownfield["available"] is True


def test_unknown_assessment_returns_404() -> None:
    response = client.get("/api/v1/compressed-air/system-summary/assessment/999999999")

    assert response.status_code == 404
