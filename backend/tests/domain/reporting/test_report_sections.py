from datetime import UTC, datetime

from app.domain.reporting.export_payload import CalculationExportPayload
from app.domain.reporting.report_sections import build_report_sections


def build_payload() -> CalculationExportPayload:
    created_at = datetime(2026, 8, 9, 10, 0, tzinfo=UTC)
    updated_at = datetime(2026, 8, 9, 10, 30, tzinfo=UTC)
    completed_at = datetime(2026, 8, 9, 10, 20, tzinfo=UTC)

    return CalculationExportPayload(
        calculation_case_id=501,
        project_id=51,
        calculation_code="SECTION-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=3,
        title="Centrifugal Engineering Report",
        description="Design basis for centrifugal compressor sizing.",
        input_data={
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
            "mass_flow_kg_per_s": "93.376",
        },
        result_data={
            "polytropic_head_kj_per_kg": "155.667",
            "required_driver_power_kw": "21011.32",
            "overall_status": "PASS",
            "driver_is_adequate": True,
            "design_point_is_within_envelope": True,
            "validation_checks": [
                {
                    "code": "DRIVER_OK",
                    "status": "PASS",
                }
            ],
        },
        engineering_notes="Reviewed engineering calculation.",
        created_at=created_at,
        updated_at=updated_at,
        completed_at=completed_at,
    )


def test_build_report_sections() -> None:
    payload = build_payload()

    sections = build_report_sections(payload)

    assert sections.metadata.title == "Document Information"
    assert sections.metadata.data["calculation_code"] == "SECTION-001"
    assert sections.metadata.data["calculation_type"] == "CENTRIFUGAL"
    assert sections.metadata.data["revision"] == 3

    assert sections.design_basis.title == "Design Basis"
    assert (
        sections.design_basis.data["description"]
        == "Design basis for centrifugal compressor sizing."
    )

    assert sections.inputs.title == "Calculation Inputs"
    assert sections.inputs.data["suction_pressure_bar"] == "30"

    assert sections.results.title == "Calculation Results"
    assert sections.results.data["required_driver_power_kw"] == "21011.32"

    assert sections.engineering_notes.title == "Engineering Notes"
    assert sections.engineering_notes.data["notes"] == "Reviewed engineering calculation."


def test_validation_section_extracts_available_checks() -> None:
    payload = build_payload()

    sections = build_report_sections(payload)

    validation = sections.validation.data

    assert validation["overall_status"] == "PASS"
    assert validation["driver_is_adequate"] is True
    assert validation["design_point_is_within_envelope"] is True

    assert validation["validation_checks"] == [
        {
            "code": "DRIVER_OK",
            "status": "PASS",
        }
    ]


def test_revision_audit_section() -> None:
    payload = build_payload()

    sections = build_report_sections(payload)

    audit = sections.revision_audit.data

    assert audit["revision"] == 3
    assert audit["status"] == "COMPLETED"
    assert audit["created_at"] == payload.created_at.isoformat()
    assert audit["updated_at"] == payload.updated_at.isoformat()
    assert audit["completed_at"] == payload.completed_at.isoformat()


def test_missing_optional_values_are_handled() -> None:
    timestamp = datetime(2026, 8, 9, 10, 0, tzinfo=UTC)

    payload = CalculationExportPayload(
        calculation_case_id=502,
        project_id=51,
        calculation_code="SECTION-002",
        calculation_type="SELECTION",
        status="DRAFT",
        revision=1,
        title="Draft Selection Report",
        description=None,
        input_data={},
        result_data=None,
        engineering_notes=None,
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=None,
    )

    sections = build_report_sections(payload)

    assert "description" not in sections.design_basis.data
    assert sections.results.data == {}
    assert sections.validation.data == {}
    assert sections.engineering_notes.data["notes"] == "No engineering notes recorded."
    assert sections.revision_audit.data["completed_at"] is None
