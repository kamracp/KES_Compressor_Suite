from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectAlreadyExistsError(ValueError):
    """Raised when a project code already exists."""


class ProjectNotFoundError(LookupError):
    """Raised when a project cannot be found."""


class ProjectService:
    """Business service for compressor engineering projects."""

    def create_project(self, db: Session, payload: ProjectCreate) -> Project:
        existing = project_repository.get_by_code(db, payload.project_code)

        if existing is not None:
            raise ProjectAlreadyExistsError(
                f"Project code '{payload.project_code}' already exists."
            )

        return project_repository.create(db, payload)

    def get_project(self, db: Session, project_id: int) -> Project:
        project = project_repository.get_by_id(db, project_id)

        if project is None:
            raise ProjectNotFoundError(f"Project with id {project_id} was not found.")

        return project

    def list_projects(self, db: Session) -> list[Project]:
        return project_repository.list_all(db)

    def update_project(
        self,
        db: Session,
        project_id: int,
        payload: ProjectUpdate,
    ) -> Project:
        project = self.get_project(db, project_id)

        if payload.project_code is not None:
            existing = project_repository.get_by_code(db, payload.project_code)

            if existing is not None and existing.id != project.id:
                raise ProjectAlreadyExistsError(
                    f"Project code '{payload.project_code}' already exists."
                )

        return project_repository.update(db, project, payload)

    def delete_project(self, db: Session, project_id: int) -> None:
        project = self.get_project(db, project_id)
        project_repository.delete(db, project)


project_service = ProjectService()
