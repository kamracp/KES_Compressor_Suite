from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Repository for compressor project persistence operations."""

    def create(self, db: Session, payload: ProjectCreate) -> Project:
        project = Project(**payload.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def get_by_id(self, db: Session, project_id: int) -> Project | None:
        return db.get(Project, project_id)

    def get_by_code(self, db: Session, project_code: str) -> Project | None:
        statement = select(Project).where(Project.project_code == project_code)
        return db.scalar(statement)

    def list_all(self, db: Session) -> list[Project]:
        statement = select(Project).order_by(Project.id)
        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        project: Project,
        payload: ProjectUpdate,
    ) -> Project:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def delete(self, db: Session, project: Project) -> None:
        db.delete(project)
        db.commit()


project_repository = ProjectRepository()
