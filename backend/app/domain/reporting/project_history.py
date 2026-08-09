from dataclasses import dataclass
from datetime import datetime

from app.models.calculation_case import CalculationCase, CalculationStatus


@dataclass(frozen=True, slots=True)
class ProjectCalculationHistoryItem:
    """One persisted calculation entry in project history."""

    calculation_case_id: int
    calculation_code: str
    calculation_type: str
    status: str
    revision: int
    title: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


@dataclass(frozen=True, slots=True)
class ProjectCalculationHistory:
    """Chronological compressor calculation history for a project."""

    project_id: int
    total_cases: int
    completed_cases: int
    draft_cases: int
    latest_case_id: int | None
    latest_completed_case_id: int | None
    items: tuple[ProjectCalculationHistoryItem, ...]


def build_project_calculation_history(
    project_id: int,
    calculation_cases: list[CalculationCase],
) -> ProjectCalculationHistory:
    """Build chronological calculation history for a project."""

    matching_cases = [case for case in calculation_cases if case.project_id == project_id]

    ordered_cases = sorted(
        matching_cases,
        key=lambda case: (
            case.created_at,
            case.id,
        ),
    )

    items = tuple(
        ProjectCalculationHistoryItem(
            calculation_case_id=case.id,
            calculation_code=case.calculation_code,
            calculation_type=case.calculation_type,
            status=case.status,
            revision=case.revision,
            title=case.title,
            created_at=case.created_at,
            updated_at=case.updated_at,
            completed_at=case.completed_at,
        )
        for case in ordered_cases
    )

    completed_cases = [
        case for case in ordered_cases if case.status == CalculationStatus.COMPLETED.value
    ]

    draft_cases = [case for case in ordered_cases if case.status == CalculationStatus.DRAFT.value]

    latest_case_id = ordered_cases[-1].id if ordered_cases else None

    latest_completed_case_id = completed_cases[-1].id if completed_cases else None

    return ProjectCalculationHistory(
        project_id=project_id,
        total_cases=len(ordered_cases),
        completed_cases=len(completed_cases),
        draft_cases=len(draft_cases),
        latest_case_id=latest_case_id,
        latest_completed_case_id=latest_completed_case_id,
        items=items,
    )
