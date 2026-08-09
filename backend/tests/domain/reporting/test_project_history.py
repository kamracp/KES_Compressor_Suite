from datetime import UTC, datetime, timedelta

from app.domain.reporting.project_history import (
    build_project_calculation_history,
)
from app.models.calculation_case import CalculationCase


def build_case(
    *,
    case_id: int,
    project_id: int,
    calculation_code: str,
    calculation_type: str,
    status: str,
    revision: int,
    title: str,
    created_at: datetime,
    completed_at: datetime | None = None,
) -> CalculationCase:
    return CalculationCase(
        id=case_id,
        project_id=project_id,
        calculation_code=calculation_code,
        calculation_type=calculation_type,
        status=status,
        revision=revision,
        title=title,
        description=None,
        input_data={},
        result_data={} if status == "COMPLETED" else None,
        engineering_notes=None,
        created_at=created_at,
        updated_at=created_at,
        completed_at=completed_at,
    )


def test_build_project_calculation_history() -> None:
    base_time = datetime(2026, 8, 9, 6, 0, tzinfo=UTC)

    cases = [
        build_case(
            case_id=3,
            project_id=10,
            calculation_code="CALC-003",
            calculation_type="CENTRIFUGAL",
            status="DRAFT",
            revision=1,
            title="Draft Centrifugal Case",
            created_at=base_time + timedelta(hours=2),
        ),
        build_case(
            case_id=1,
            project_id=10,
            calculation_code="CALC-001",
            calculation_type="SELECTION",
            status="COMPLETED",
            revision=1,
            title="Selection Case",
            created_at=base_time,
            completed_at=base_time + timedelta(minutes=10),
        ),
        build_case(
            case_id=2,
            project_id=10,
            calculation_code="CALC-002",
            calculation_type="COMPRESSION",
            status="COMPLETED",
            revision=2,
            title="Compression Case",
            created_at=base_time + timedelta(hours=1),
            completed_at=base_time + timedelta(hours=1, minutes=20),
        ),
    ]

    history = build_project_calculation_history(
        project_id=10,
        calculation_cases=cases,
    )

    assert history.project_id == 10
    assert history.total_cases == 3
    assert history.completed_cases == 2
    assert history.draft_cases == 1

    assert history.latest_case_id == 3
    assert history.latest_completed_case_id == 2

    assert [item.calculation_case_id for item in history.items] == [
        1,
        2,
        3,
    ]


def test_cases_from_other_projects_are_ignored() -> None:
    base_time = datetime(2026, 8, 9, 6, 0, tzinfo=UTC)

    cases = [
        build_case(
            case_id=1,
            project_id=10,
            calculation_code="P10-CALC",
            calculation_type="COMPRESSION",
            status="COMPLETED",
            revision=1,
            title="Project 10 Case",
            created_at=base_time,
            completed_at=base_time,
        ),
        build_case(
            case_id=2,
            project_id=20,
            calculation_code="P20-CALC",
            calculation_type="CENTRIFUGAL",
            status="COMPLETED",
            revision=1,
            title="Project 20 Case",
            created_at=base_time + timedelta(hours=1),
            completed_at=base_time + timedelta(hours=1),
        ),
    ]

    history = build_project_calculation_history(
        project_id=10,
        calculation_cases=cases,
    )

    assert history.total_cases == 1
    assert history.items[0].calculation_case_id == 1


def test_empty_project_history() -> None:
    history = build_project_calculation_history(
        project_id=999,
        calculation_cases=[],
    )

    assert history.project_id == 999
    assert history.total_cases == 0
    assert history.completed_cases == 0
    assert history.draft_cases == 0
    assert history.latest_case_id is None
    assert history.latest_completed_case_id is None
    assert history.items == ()
