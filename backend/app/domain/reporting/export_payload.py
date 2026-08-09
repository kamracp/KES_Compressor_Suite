from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from app.domain.reporting.calculation_report import CalculationReport


@dataclass(frozen=True, slots=True)
class CalculationExportPayload:
    """Serializable export payload for a compressor engineering report."""

    calculation_case_id: int
    project_id: int

    calculation_code: str
    calculation_type: str
    status: str
    revision: int

    title: str
    description: str | None

    input_data: dict[str, Any]
    result_data: dict[str, Any] | None

    engineering_notes: str | None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


def build_export_payload(
    report: CalculationReport,
) -> CalculationExportPayload:
    """Build a serializable export payload from a calculation report."""

    return CalculationExportPayload(
        calculation_case_id=report.calculation_case_id,
        project_id=report.project_id,
        calculation_code=report.calculation_code,
        calculation_type=report.calculation_type,
        status=report.status,
        revision=report.revision,
        title=report.title,
        description=report.description,
        input_data=report.input_data,
        result_data=report.result_data,
        engineering_notes=report.engineering_notes,
        created_at=report.created_at,
        updated_at=report.updated_at,
        completed_at=report.completed_at,
    )


def export_payload_to_dict(
    payload: CalculationExportPayload,
) -> dict[str, Any]:
    """Convert export payload to a dictionary."""

    return asdict(payload)
