from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.calculation_case import (
    CalculationCase,
    CalculationStatus,
    CalculationType,
)
from app.models.project import Project
from app.repositories.project import project_repository
from app.schemas.calculation_case import CalculationCaseCreate
from app.schemas.project import ProjectCreate
from app.services.calculation_case import calculation_case_service
from app.services.project_history import (
    ProjectHistoryProjectNotFoundError,
    project_history_service,
)
from tests.helpers.tenant_context import ensure_test_organization_id


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def create_test_project() -> int:
    with SessionLocal() as db:
        project = project_repository.create(
            db,
            organization_id=ensure_test_organization_id(db),
            payload=ProjectCreate(
                project_code="KESC-HIST-001",
                project_name="Project History Test",
            ),
        )

        return project.id


def create_case(
    *,
    project_id: int,
    calculation_code: str,
    calculation_type: CalculationType,
    status: CalculationStatus,
    revision: int,
    title: str,
) -> int:
    with SessionLocal() as db:
        case = calculation_case_service.create_case(
            db,
            organization_id=ensure_test_organization_id(db),
            payload=CalculationCaseCreate(
                project_id=project_id,
                calculation_code=calculation_code,
                calculation_type=calculation_type,
                status=status,
                revision=revision,
                title=title,
                input_data={},
                result_data={"status": "PASS"} if status == CalculationStatus.COMPLETED else None,
            ),
        )

        return case.id


def test_get_project_history() -> None:
    reset_data()

    project_id = create_test_project()

    first_case_id = create_case(
        project_id=project_id,
        calculation_code="HIST-001",
        calculation_type=CalculationType.SELECTION,
        status=CalculationStatus.COMPLETED,
        revision=1,
        title="Selection Case",
    )

    second_case_id = create_case(
        project_id=project_id,
        calculation_code="HIST-002",
        calculation_type=CalculationType.CENTRIFUGAL,
        status=CalculationStatus.DRAFT,
        revision=1,
        title="Draft Centrifugal Case",
    )

    with SessionLocal() as db:
        history = project_history_service.get_project_history(
            db,
            organization_id=ensure_test_organization_id(db),
            project_id=project_id,
        )

    assert history.project_id == project_id
    assert history.total_cases == 2
    assert history.completed_cases == 1
    assert history.draft_cases == 1

    assert history.latest_case_id == second_case_id
    assert history.latest_completed_case_id == first_case_id

    assert len(history.items) == 2


def test_empty_project_history() -> None:
    reset_data()

    project_id = create_test_project()

    with SessionLocal() as db:
        history = project_history_service.get_project_history(
            db,
            organization_id=ensure_test_organization_id(db),
            project_id=project_id,
        )

    assert history.project_id == project_id
    assert history.total_cases == 0
    assert history.completed_cases == 0
    assert history.draft_cases == 0
    assert history.latest_case_id is None
    assert history.latest_completed_case_id is None
    assert history.items == ()


def test_missing_project_raises_error() -> None:
    reset_data()

    with SessionLocal() as db:
        try:
            project_history_service.get_project_history(
                db,
                organization_id=ensure_test_organization_id(db),
                project_id=999999,
            )
        except ProjectHistoryProjectNotFoundError as exc:
            assert "999999" in str(exc)
        else:
            raise AssertionError("Expected ProjectHistoryProjectNotFoundError.")
