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
            "project_code": f"REPORT-{uuid4().hex[:8]}",
            "project_name": "Compressed Air Report Test Project",
        },
    )

    assert response.status_code == 201

    return organization, headers, response.json()["id"]


def create_assessment(
    *,
    headers: dict[str, str],
    project_id: int,
    assessment_type: str = "GREENFIELD",
    include_standards: bool = True,
) -> dict:
    payload = {
        "project_id": project_id,
        "assessment_code": f"CA-RPT-{uuid4().hex[:10]}",
        "assessment_type": assessment_type,
        "status": "COMPLETED",
        "title": "Compressed Air Engineering Assessment",
        "engineering_basis": "Vendor-neutral compressed-air engineering basis.",
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
            "equipment_selection": {
                "selection_basis": "vendor-neutral",
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
            "recommendations": {
                "items": [
                    "Maintain minimum operating pressure.",
                    "Monitor system specific power.",
                ]
            },
        },
        "standards_snapshot": (
            {
                "formal_compliance_claim_available": False,
                "applicable_standard_codes": [
                    "ASME_PTC_10",
                ],
            }
            if include_standards
            else None
        ),
        "calculation_version": "S11-M38",
        "created_by": "test-suite",
    }

    response = client.post(
        "/api/v1/compressed-air/assessments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


def get_report(
    *,
    headers: dict[str, str],
    assessment_id: int,
    report_code: str,
    report_title: str,
):
    return client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment_id}",
        headers=headers,
        params={
            "report_code": report_code,
            "report_title": report_title,
        },
    )


def test_generate_integrated_report_from_assessment() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-001",
        report_title="Integrated Compressed Air Engineering Report",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == assessment["project_id"]
    assert data["report_code"] == "RPT-001"
    assert data["assessment_type"] == "GREENFIELD"
    assert data["generated_from_assessment_code"] == assessment["assessment_code"]
    assert data["calculation_version"] == "S11-M38"
    assert data["section_count"] > 0


def test_report_maps_expected_sections() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-SECTIONS",
        report_title="Section Mapping Report",
    )

    assert response.status_code == 200

    sections = {item["section"]: item for item in response.json()["sections"]}

    assert sections["DESIGN_BASIS"]["included"] is True
    assert sections["DEMAND_AND_CAPACITY"]["included"] is True
    assert sections["EQUIPMENT_SELECTION"]["included"] is True
    assert sections["AIR_TREATMENT"]["included"] is True
    assert sections["STORAGE"]["included"] is True
    assert sections["DISTRIBUTION"]["included"] is True
    assert sections["ENERGY"]["included"] is True
    assert sections["RECOMMENDATIONS"]["included"] is True
    assert sections["AUDIT_TRAIL"]["included"] is True


def test_report_contains_audit_trail() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-AUDIT",
        report_title="Audit Trail Report",
    )

    assert response.status_code == 200

    audit_section = next(
        item for item in response.json()["sections"] if item["section"] == "AUDIT_TRAIL"
    )

    audit_data = audit_section["data"]

    assert audit_section["included"] is True
    assert audit_data["assessment_id"] == assessment["id"]
    assert audit_data["assessment_code"] == assessment["assessment_code"]
    assert audit_data["assessment_status"] == "COMPLETED"
    assert audit_data["calculation_version"] == "S11-M38"


def test_report_preserves_vendor_neutral_equipment_section() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-EQUIPMENT",
        report_title="Equipment Selection Report",
    )

    assert response.status_code == 200

    equipment_section = next(
        item for item in response.json()["sections"] if item["section"] == "EQUIPMENT_SELECTION"
    )

    assert equipment_section["included"] is True
    assert equipment_section["data"]["selection_basis"] == "vendor-neutral"


def test_report_does_not_infer_formal_compliance_claim() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
        include_standards=True,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-STD",
        report_title="Standards Review Report",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False
    assert any("no formal compliance claim" in warning.lower() for warning in data["warnings"])


def test_report_warns_when_standards_snapshot_is_missing() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    assessment = create_assessment(
        headers=headers,
        project_id=project_id,
        include_standards=False,
    )

    response = get_report(
        headers=headers,
        assessment_id=assessment["id"],
        report_code="RPT-NO-STD",
        report_title="Report Without Standards Snapshot",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False
    assert any(
        "no standards applicability snapshot" in warning.lower() for warning in data["warnings"]
    )


def test_report_requires_authentication() -> None:
    reset_data()

    response = client.get(
        "/api/v1/compressed-air/report/assessment/999999",
        params={
            "report_code": "RPT-AUTH",
            "report_title": "Authentication Test",
        },
    )

    assert response.status_code == 401


def test_cross_tenant_report_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    assessment = create_assessment(
        headers=first_headers,
        project_id=first_project_id,
    )

    response = get_report(
        headers=second_headers,
        assessment_id=assessment["id"],
        report_code="RPT-CROSS",
        report_title="Cross Tenant Report",
    )

    assert response.status_code == 404
