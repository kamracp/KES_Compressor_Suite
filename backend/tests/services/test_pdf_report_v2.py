from datetime import UTC, datetime

from app.domain.reporting.export_payload import CalculationExportPayload
from app.services.pdf_report_v2 import pdf_report_v2_service


def build_payload() -> CalculationExportPayload:
    timestamp = datetime(2026, 8, 9, 11, 30, tzinfo=UTC)

    return CalculationExportPayload(
        calculation_case_id=601,
        project_id=61,
        calculation_code="PDFV2-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=4,
        title="Centrifugal Compressor Engineering Report",
        description="Structured engineering PDF report test.",
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
                },
                {
                    "code": "SURGE_MARGIN_OK",
                    "status": "PASS",
                },
            ],
        },
        engineering_notes="Reviewed structured engineering report.",
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=timestamp,
    )


def test_generate_structured_pdf_report() -> None:
    payload = build_payload()

    pdf_bytes = pdf_report_v2_service.generate_calculation_report(payload)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1500


def test_generate_structured_pdf_with_nested_validation_data() -> None:
    payload = build_payload()

    pdf_bytes = pdf_report_v2_service.generate_calculation_report(payload)

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1500


def test_generate_draft_structured_pdf() -> None:
    timestamp = datetime(2026, 8, 9, 11, 30, tzinfo=UTC)

    payload = CalculationExportPayload(
        calculation_case_id=602,
        project_id=61,
        calculation_code="PDFV2-002",
        calculation_type="SELECTION",
        status="DRAFT",
        revision=1,
        title="Draft Compressor Selection Report",
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

    pdf_bytes = pdf_report_v2_service.generate_calculation_report(payload)

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_structured_pdf_is_repeatable() -> None:
    payload = build_payload()

    first_pdf = pdf_report_v2_service.generate_calculation_report(payload)
    second_pdf = pdf_report_v2_service.generate_calculation_report(payload)

    assert first_pdf.startswith(b"%PDF-")
    assert second_pdf.startswith(b"%PDF-")
    assert len(first_pdf) > 1500
    assert len(second_pdf) > 1500
