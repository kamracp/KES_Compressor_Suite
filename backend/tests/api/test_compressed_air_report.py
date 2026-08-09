from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import engine
from app.main import app

client = TestClient(app)


def ensure_test_project_id() -> int:
    with engine.begin() as connection:
        project_id = connection.execute(
            text(
                """
                INSERT INTO projects (
                    project_code,
                    project_name,
                    client_name,
                    plant_name,
                    location,
                    service_description,
                    status
                )
                VALUES (
                    'TEST-REPORT-S11',
                    'Compressed Air Report Test Project',
                    'Engineering Test',
                    'Test Plant',
                    'Test Environment',
                    'Automated compressed-air report testing',
                    'ACTIVE'
                )
                ON CONFLICT (project_code)
                DO UPDATE SET
                    project_name = EXCLUDED.project_name,
                    status = EXCLUDED.status
                RETURNING id
                """
            )
        ).scalar_one()

    return int(project_id)


def create_assessment(
    *,
    assessment_type: str = "GREENFIELD",
    include_standards: bool = True,
) -> dict:
    project_id = ensure_test_project_id()

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
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


def test_generate_integrated_report_from_assessment() -> None:
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-001",
            "report_title": "Integrated Compressed Air Engineering Report",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == assessment["project_id"]
    assert data["report_code"] == "RPT-001"
    assert data["assessment_type"] == "GREENFIELD"

    assert data["generated_from_assessment_code"] == (assessment["assessment_code"])

    assert data["calculation_version"] == "S11-M38"
    assert data["section_count"] > 0


def test_report_maps_expected_sections() -> None:
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-SECTIONS",
            "report_title": "Section Mapping Report",
        },
    )

    assert response.status_code == 200

    data = response.json()

    sections = {item["section"]: item for item in data["sections"]}

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
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-AUDIT",
            "report_title": "Audit Trail Report",
        },
    )

    assert response.status_code == 200

    data = response.json()

    audit_section = next(item for item in data["sections"] if item["section"] == "AUDIT_TRAIL")

    assert audit_section["included"] is True

    audit_data = audit_section["data"]

    assert audit_data["assessment_id"] == assessment["id"]
    assert audit_data["assessment_code"] == assessment["assessment_code"]
    assert audit_data["assessment_status"] == "COMPLETED"
    assert audit_data["calculation_version"] == "S11-M38"


def test_report_preserves_vendor_neutral_equipment_section() -> None:
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-EQUIPMENT",
            "report_title": "Equipment Selection Report",
        },
    )

    assert response.status_code == 200

    data = response.json()

    equipment_section = next(
        item for item in data["sections"] if item["section"] == "EQUIPMENT_SELECTION"
    )

    assert equipment_section["included"] is True

    assert equipment_section["data"]["selection_basis"] == "vendor-neutral"


def test_report_does_not_infer_formal_compliance_claim() -> None:
    assessment = create_assessment(
        include_standards=True,
    )

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-STD",
            "report_title": "Standards Review Report",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False

    assert any("no formal compliance claim" in warning.lower() for warning in data["warnings"])


def test_report_warns_when_standards_snapshot_is_missing() -> None:
    assessment = create_assessment(
        include_standards=False,
    )

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-NO-STD",
            "report_title": "Report Without Standards Snapshot",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False

    assert any(
        "no standards applicability snapshot" in warning.lower() for warning in data["warnings"]
    )


def test_unknown_assessment_returns_404() -> None:
    response = client.get(
        "/api/v1/compressed-air/report/assessment/999999999",
        params={
            "report_code": "RPT-404",
            "report_title": "Missing Assessment Report",
        },
    )

    assert response.status_code == 404


def test_empty_report_code_returns_422() -> None:
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "",
            "report_title": "Invalid Report",
        },
    )

    assert response.status_code == 422


def test_missing_report_title_returns_422() -> None:
    assessment = create_assessment()

    response = client.get(
        f"/api/v1/compressed-air/report/assessment/{assessment['id']}",
        params={
            "report_code": "RPT-NO-TITLE",
        },
    )

    assert response.status_code == 422
