from datetime import UTC, datetime

from app.domain.reporting.calculation_report import build_calculation_report
from app.models.calculation_case import CalculationCase


def test_build_calculation_report() -> None:
    created_at = datetime(2026, 8, 9, 5, 0, tzinfo=UTC)
    updated_at = datetime(2026, 8, 9, 5, 30, tzinfo=UTC)
    completed_at = datetime(2026, 8, 9, 5, 20, tzinfo=UTC)

    calculation_case = CalculationCase(
        id=101,
        project_id=11,
        calculation_code="CALC-RPT-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=2,
        title="Centrifugal Compressor Design Case",
        description="Design-point centrifugal compressor calculation.",
        input_data={
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
        },
        result_data={
            "polytropic_head_kj_per_kg": "155.667",
            "required_driver_power_kw": "21011.32",
        },
        engineering_notes="Reviewed engineering calculation.",
        created_at=created_at,
        updated_at=updated_at,
        completed_at=completed_at,
    )

    report = build_calculation_report(calculation_case)

    assert report.calculation_case_id == 101
    assert report.project_id == 11

    assert report.calculation_code == "CALC-RPT-001"
    assert report.calculation_type == "CENTRIFUGAL"
    assert report.status == "COMPLETED"
    assert report.revision == 2

    assert report.title == "Centrifugal Compressor Design Case"
    assert report.description == ("Design-point centrifugal compressor calculation.")

    assert report.input_data["suction_pressure_bar"] == "30"
    assert report.input_data["discharge_pressure_bar"] == "90"

    assert report.result_data is not None
    assert report.result_data["polytropic_head_kj_per_kg"] == "155.667"
    assert report.result_data["required_driver_power_kw"] == "21011.32"

    assert report.engineering_notes == "Reviewed engineering calculation."

    assert report.created_at == created_at
    assert report.updated_at == updated_at
    assert report.completed_at == completed_at


def test_build_draft_report_without_results() -> None:
    timestamp = datetime(2026, 8, 9, 5, 0, tzinfo=UTC)

    calculation_case = CalculationCase(
        id=102,
        project_id=11,
        calculation_code="CALC-RPT-002",
        calculation_type="SELECTION",
        status="DRAFT",
        revision=1,
        title="Compressor Selection Case",
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

    report = build_calculation_report(calculation_case)

    assert report.status == "DRAFT"
    assert report.result_data is None
    assert report.description is None
    assert report.engineering_notes is None
    assert report.completed_at is None
