from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compressed_air_assessment import CompressedAirAssessment
from app.models.project import Project


class CompressedAirAssessmentRepository:
    """Persistence operations for tenant-scoped compressed-air assessments."""

    def create(
        self,
        db: Session,
        assessment: CompressedAirAssessment,
    ) -> CompressedAirAssessment:
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    def get_by_id(
        self,
        db: Session,
        *,
        organization_id: int,
        assessment_id: int,
    ) -> CompressedAirAssessment | None:
        statement = (
            select(CompressedAirAssessment)
            .join(
                Project,
                Project.id == CompressedAirAssessment.project_id,
            )
            .where(
                CompressedAirAssessment.id == assessment_id,
                Project.organization_id == organization_id,
            )
        )

        return db.scalar(statement)

    def get_by_code(
        self,
        db: Session,
        *,
        project_id: int,
        assessment_code: str,
    ) -> CompressedAirAssessment | None:
        statement = select(CompressedAirAssessment).where(
            CompressedAirAssessment.project_id == project_id,
            CompressedAirAssessment.assessment_code == assessment_code,
        )

        return db.scalar(statement)

    def list_by_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> list[CompressedAirAssessment]:
        statement = (
            select(CompressedAirAssessment)
            .join(
                Project,
                Project.id == CompressedAirAssessment.project_id,
            )
            .where(
                CompressedAirAssessment.project_id == project_id,
                Project.organization_id == organization_id,
            )
            .order_by(
                CompressedAirAssessment.created_at.desc(),
                CompressedAirAssessment.id.desc(),
            )
        )

        return list(db.scalars(statement).all())

    def list_by_project_and_type(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
        assessment_type: str,
    ) -> list[CompressedAirAssessment]:
        statement = (
            select(CompressedAirAssessment)
            .join(
                Project,
                Project.id == CompressedAirAssessment.project_id,
            )
            .where(
                CompressedAirAssessment.project_id == project_id,
                CompressedAirAssessment.assessment_type == assessment_type,
                Project.organization_id == organization_id,
            )
            .order_by(
                CompressedAirAssessment.created_at.desc(),
                CompressedAirAssessment.id.desc(),
            )
        )

        return list(db.scalars(statement).all())

    def update_status(
        self,
        db: Session,
        *,
        assessment: CompressedAirAssessment,
        status: str,
    ) -> CompressedAirAssessment:
        assessment.status = status

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return assessment


compressed_air_assessment_repository = CompressedAirAssessmentRepository()
