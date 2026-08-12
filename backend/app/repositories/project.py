from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Repository for tenant-scoped compressor project persistence."""

    def create(
        self,
        db: Session,
        *,
        organization_id: int,
        payload: ProjectCreate,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            **payload.model_dump(),
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def get_by_id(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> Project | None:
        statement = select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )

        return db.scalar(statement)

    def get_by_code(
        self,
        db: Session,
        *,
        organization_id: int,
        project_code: str,
    ) -> Project | None:
        statement = select(Project).where(
            Project.organization_id == organization_id,
            Project.project_code == project_code,
        )

        return db.scalar(statement)

    def list_by_organization(
        self,
        db: Session,
        *,
        organization_id: int,
    ) -> list[Project]:
        statement = (
            select(Project)
            .where(
                Project.organization_id == organization_id,
            )
            .order_by(Project.id)
        )

        return list(
            db.scalars(statement).all()
        )

    def update(
        self,
        db: Session,
        project: Project,
        payload: ProjectUpdate,
    ) -> Project:
        update_data = payload.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(project, field, value)

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def delete(
        self,
        db: Session,
        project: Project,
    ) -> None:
        db.delete(project)
        db.commit()


project_repository = ProjectRepository()
