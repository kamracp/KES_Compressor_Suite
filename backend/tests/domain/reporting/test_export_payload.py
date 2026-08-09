from datetime import UTC, datetime

from app.domain.reporting.calculation_report import CalculationReport
from app.domain.reporting.export_payload import (
    build_export_payload,
    export_payload_to_dict,
)


def build_report() -> CalculationReport:
    timestamp = datetime(2026, 8, 9, 7, 0, tzinfo=UTC)

    return CalculationReport(
        calculation_case_id=301,
        project_id=31,
        calculation_code="EXPORT-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=2,
        title="Centrifugal Compressor Export Case",
        description="Export payload test.",
        input_data={
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
        },
        result_data={
            "required_driver_power_kw": "21011.32",
            "status": "PASS",
        },
        engineering_notes="Reviewed for export.",
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=timestamp,
    )


def test_build_export_payload() -> None:
    report = build_report()

    payload = build_export_payload(report)

    assert payload.calculation_case_id == 301
    assert payload.project_id == 31
    assert payload.calculation_code == "EXPORT-001"
    assert payload.calculation_type == "CENTRIFUGAL"
    assert payload.status == "COMPLETED"
    assert payload.revision == 2

    assert payload.title == "Centrifugal Compressor Export Case"
    assert payload.description == "Export payload test."

    assert payload.input_data["suction_pressure_bar"] == "30"

    assert payload.result_data is not None
    assert payload.result_data["required_driver_power_kw"] == "21011.32"

    assert payload.engineering_notes == "Reviewed for export."


def test_export_payload_to_dict() -> None:
    report = build_report()

    payload = build_export_payload(report)
    data = export_payload_to_dict(payload)

    assert isinstance(data, dict)

    assert data["calculation_case_id"] == 301
    assert data["project_id"] == 31
    assert data["calculation_code"] == "EXPORT-001"
    assert data["calculation_type"] == "CENTRIFUGAL"

    assert data["input_data"]["discharge_pressure_bar"] == "90"

    assert data["result_data"] is not None
    assert data["result_data"]["status"] == "PASS"

    assert data["created_at"] == report.created_at
    assert data["updated_at"] == report.updated_at
    assert data["completed_at"] == report.completed_at


def test_export_payload_supports_missing_optional_values() -> None:
    timestamp = datetime(2026, 8, 9, 7, 0, tzinfo=UTC)

    report = CalculationReport(
        calculation_case_id=302,
        project_id=31,
        calculation_code="EXPORT-002",
        calculation_type="SELECTION",
        status="DRAFT",
        revision=1,
        title="Draft Export Case",
        description=None,
        input_data={},
        result_data=None,
        engineering_notes=None,
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=None,
    )

    payload = build_export_payload(report)
    data = export_payload_to_dict(payload)

    assert data["description"] is None
    assert data["result_data"] is None
    assert data["engineering_notes"] is None
    assert data["completed_at"] is None
