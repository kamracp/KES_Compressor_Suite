from datetime import UTC, datetime

from app.domain.reporting.audit_summary import build_audit_summary
from app.models.calculation_case import CalculationCase


def test_completed_case_audit_summary() -> None:
    created_at = datetime(2026, 8, 9, 5, 0, tzinfo=UTC)
    updated_at = datetime(2026, 8, 9, 5, 30, tzinfo=UTC)
    completed_at = datetime(2026, 8, 9, 5, 20, tzinfo=UTC)

    calculation_case = CalculationCase(
        id=201,
        project_id=21,
        calculation_code="AUDIT-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=3,
        title="Completed Centrifugal Case",
        description=None,
        input_data={
            "suction_pressure_bar": "30",
        },
        result_data={
            "driver_power_kw": "21000",
        },
        engineering_notes="Reviewed and approved.",
        created_at=created_at,
        updated_at=updated_at,
        completed_at=completed_at,
    )

    summary = build_audit_summary(calculation_case)

    assert summary.calculation_case_id == 201
    assert summary.project_id == 21
    assert summary.calculation_code == "AUDIT-001"
    assert summary.calculation_type == "CENTRIFUGAL"
    assert summary.status == "COMPLETED"
    assert summary.revision == 3

    assert summary.created_at == created_at
    assert summary.updated_at == updated_at
    assert summary.completed_at == completed_at

    assert summary.is_completed is True
    assert summary.has_result_data is True
    assert summary.has_engineering_notes is True


def test_draft_case_audit_summary() -> None:
    timestamp = datetime(2026, 8, 9, 5, 0, tzinfo=UTC)

    calculation_case = CalculationCase(
        id=202,
        project_id=21,
        calculation_code="AUDIT-002",
        calculation_type="SELECTION",
        status="DRAFT",
        revision=1,
        title="Draft Selection Case",
        description=None,
        input_data={
            "required_flow_m3_per_hr": "14143.4",
        },
        result_data=None,
        engineering_notes=None,
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=None,
    )

    summary = build_audit_summary(calculation_case)

    assert summary.status == "DRAFT"
    assert summary.is_completed is False
    assert summary.has_result_data is False
    assert summary.has_engineering_notes is False
    assert summary.completed_at is None


def test_empty_engineering_notes_are_not_counted() -> None:
    timestamp = datetime(2026, 8, 9, 5, 0, tzinfo=UTC)

    calculation_case = CalculationCase(
        id=203,
        project_id=21,
        calculation_code="AUDIT-003",
        calculation_type="COMPRESSION",
        status="COMPLETED",
        revision=1,
        title="Compression Case",
        description=None,
        input_data={},
        result_data={
            "status": "PASS",
        },
        engineering_notes="",
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=timestamp,
    )

    summary = build_audit_summary(calculation_case)

    assert summary.is_completed is True
    assert summary.has_result_data is True
    assert summary.has_engineering_notes is False
