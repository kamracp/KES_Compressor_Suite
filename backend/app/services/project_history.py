from sqlalchemy.orm import Session

from app.domain.reporting.project_history import (
    ProjectCalculationHistory,
    build_project_calculation_history,
)
from app.repositories.calculation_case import calculation_case_repository
from app.repositories.project import project_repository


class ProjectHistoryProjectNotFoundError(LookupError):
    """Raised when a project cannot be found for history reporting."""


class ProjectHistoryService:
    """Service for project-level compressor calculation history."""

    def get_project_history(
        self,
        db: Session,
        project_id: int,
    ) -> ProjectCalculationHistory:
        project = project_repository.get_by_id(
            db,
            project_id,
        )

        if project is None:
            raise ProjectHistoryProjectNotFoundError(f"Project with id {project_id} was not found.")

        calculation_cases = calculation_case_repository.list_by_project(
            db,
            project_id,
        )

        return build_project_calculation_history(
            project_id=project_id,
            calculation_cases=calculation_cases,
        )


project_history_service = ProjectHistoryService()
