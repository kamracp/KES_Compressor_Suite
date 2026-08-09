from dataclasses import dataclass
from datetime import datetime

from app.models.calculation_case import CalculationCase, CalculationStatus


@dataclass(frozen=True, slots=True)
class CalculationAuditSummary:
    """Audit summary for a persisted compressor calculation case."""

    calculation_case_id: int
    project_id: int

    calculation_code: str
    calculation_type: str
    status: str
    revision: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    is_completed: bool
    has_result_data: bool
    has_engineering_notes: bool


def build_audit_summary(
    calculation_case: CalculationCase,
) -> CalculationAuditSummary:
    """Build a concise audit summary from a calculation case."""

    return CalculationAuditSummary(
        calculation_case_id=calculation_case.id,
        project_id=calculation_case.project_id,
        calculation_code=calculation_case.calculation_code,
        calculation_type=calculation_case.calculation_type,
        status=calculation_case.status,
        revision=calculation_case.revision,
        created_at=calculation_case.created_at,
        updated_at=calculation_case.updated_at,
        completed_at=calculation_case.completed_at,
        is_completed=(calculation_case.status == CalculationStatus.COMPLETED.value),
        has_result_data=calculation_case.result_data is not None,
        has_engineering_notes=bool(calculation_case.engineering_notes),
    )
