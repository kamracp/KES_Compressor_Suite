from datetime import UTC, datetime

from app.domain.reporting.export_payload import CalculationExportPayload
from app.services.pdf_report import pdf_report_service


def build_export_payload() -> CalculationExportPayload:
    timestamp = datetime(2026, 8, 9, 11, 0, tzinfo=UTC)

    return CalculationExportPayload(
        calculation_case_id=401,
        project_id=41,
        calculation_code="PDF-001",
        calculation_type="CENTRIFUGAL",
        status="COMPLETED",
        revision=1,
        title="Centrifugal Compressor Engineering Report",
        description="PDF generation service test.",
        input_data={
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
            "mass_flow_kg_per_s": "93.376",
        },
        result_data={
            "polytropic_head_kj_per_kg": "155.667",
            "required_driver_power_kw": "21011.32",
            "status": "PASS",
        },
        engineering_notes="Engineering calculation reviewed.",
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=timestamp,
    )


def test_generate_calculation_report_pdf() -> None:
    payload = build_export_payload()

    pdf_bytes = pdf_report_service.generate_calculation_report(
        payload,
    )

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_generate_pdf_without_optional_sections() -> None:
    timestamp = datetime(2026, 8, 9, 11, 0, tzinfo=UTC)

    payload = CalculationExportPayload(
        calculation_case_id=402,
        project_id=41,
        calculation_code="PDF-002",
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

    pdf_bytes = pdf_report_service.generate_calculation_report(
        payload,
    )

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_pdf_service_formats_nested_result_data() -> None:
    timestamp = datetime(2026, 8, 9, 11, 0, tzinfo=UTC)

    payload = CalculationExportPayload(
        calculation_case_id=403,
        project_id=41,
        calculation_code="PDF-003",
        calculation_type="COMPRESSION",
        status="COMPLETED",
        revision=1,
        title="Nested Result PDF Test",
        description=None,
        input_data={
            "number_of_stages": 3,
        },
        result_data={
            "driver": {
                "required_driver_power_kw": "21011.32",
                "driver_is_adequate": True,
            },
            "validation_checks": [
                "STAGE_RATIO_OK",
                "DRIVER_OK",
            ],
        },
        engineering_notes=None,
        created_at=timestamp,
        updated_at=timestamp,
        completed_at=timestamp,
    )

    pdf_bytes = pdf_report_service.generate_calculation_report(
        payload,
    )

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000
