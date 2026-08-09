from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models.calculation_case import CalculationCase


@dataclass(frozen=True, slots=True)
class CalculationReport:
    """Structured engineering report for a persisted calculation case."""

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


def build_calculation_report(
    calculation_case: CalculationCase,
) -> CalculationReport:
    """Build a structured report from a persisted calculation case."""

    return CalculationReport(
        calculation_case_id=calculation_case.id,
        project_id=calculation_case.project_id,
        calculation_code=calculation_case.calculation_code,
        calculation_type=calculation_case.calculation_type,
        status=calculation_case.status,
        revision=calculation_case.revision,
        title=calculation_case.title,
        description=calculation_case.description,
        input_data=calculation_case.input_data,
        result_data=calculation_case.result_data,
        engineering_notes=calculation_case.engineering_notes,
        created_at=calculation_case.created_at,
        updated_at=calculation_case.updated_at,
        completed_at=calculation_case.completed_at,
    )
