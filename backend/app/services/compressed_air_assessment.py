from sqlalchemy.orm import Session

from app.models.compressed_air_assessment import CompressedAirAssessment
from app.repositories.compressed_air_assessment import (
    compressed_air_assessment_repository,
)
from app.repositories.project import project_repository
from app.schemas.compressed_air_assessment import (
    CompressedAirAssessmentCreateRequest,
    CompressedAirAssessmentListResponse,
    CompressedAirAssessmentResponse,
    CompressedAirAssessmentStatusUpdateRequest,
    CompressedAirAssessmentSummaryResponse,
)


class CompressedAirAssessmentNotFoundError(LookupError):
    """Raised when a tenant-scoped compressed-air assessment cannot be found."""


class CompressedAirAssessmentProjectNotFoundError(LookupError):
    """Raised when the tenant-scoped parent project cannot be found."""


class DuplicateCompressedAirAssessmentCodeError(ValueError):
    """Raised when an assessment code already exists within a tenant."""


class CompressedAirAssessmentService:
    """Application service for tenant-scoped compressed-air assessments."""

    def _validate_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> None:
        project = project_repository.get_by_id(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        if project is None:
            raise CompressedAirAssessmentProjectNotFoundError(
                f"Project with id {project_id} was not found."
            )

    def create(
        self,
        db: Session,
        *,
        organization_id: int,
        request: CompressedAirAssessmentCreateRequest,
    ) -> CompressedAirAssessmentResponse:
        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=request.project_id,
        )

        existing = compressed_air_assessment_repository.get_by_code(
            db,
            project_id=request.project_id,
            assessment_code=request.assessment_code,
        )

        if existing is not None:
            raise DuplicateCompressedAirAssessmentCodeError(
                "Compressed-air assessment code already exists."
            )

        assessment = CompressedAirAssessment(
            project_id=request.project_id,
            assessment_code=request.assessment_code,
            assessment_type=request.assessment_type.value,
            status=request.status.value,
            title=request.title,
            engineering_basis=request.engineering_basis,
            input_payload=request.input_payload,
            result_payload=request.result_payload,
            standards_snapshot=request.standards_snapshot,
            calculation_version=request.calculation_version,
            created_by=request.created_by,
        )

        created = compressed_air_assessment_repository.create(
            db,
            assessment,
        )

        return CompressedAirAssessmentResponse.model_validate(created)

    def get_by_id(
        self,
        db: Session,
        *,
        organization_id: int,
        assessment_id: int,
    ) -> CompressedAirAssessmentResponse:
        assessment = compressed_air_assessment_repository.get_by_id(
            db,
            organization_id=organization_id,
            assessment_id=assessment_id,
        )

        if assessment is None:
            raise CompressedAirAssessmentNotFoundError("Compressed-air assessment not found.")

        return CompressedAirAssessmentResponse.model_validate(assessment)

    def list_by_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> CompressedAirAssessmentListResponse:
        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        assessments = compressed_air_assessment_repository.list_by_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        items = [
            CompressedAirAssessmentSummaryResponse.model_validate(item) for item in assessments
        ]

        return CompressedAirAssessmentListResponse(
            project_id=project_id,
            total=len(items),
            items=items,
        )

    def list_by_project_and_type(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
        assessment_type: str,
    ) -> CompressedAirAssessmentListResponse:
        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        assessments = compressed_air_assessment_repository.list_by_project_and_type(
            db,
            organization_id=organization_id,
            project_id=project_id,
            assessment_type=assessment_type,
        )

        items = [
            CompressedAirAssessmentSummaryResponse.model_validate(item) for item in assessments
        ]

        return CompressedAirAssessmentListResponse(
            project_id=project_id,
            total=len(items),
            items=items,
        )

    def update_status(
        self,
        db: Session,
        *,
        organization_id: int,
        assessment_id: int,
        request: CompressedAirAssessmentStatusUpdateRequest,
    ) -> CompressedAirAssessmentResponse:
        assessment = compressed_air_assessment_repository.get_by_id(
            db,
            organization_id=organization_id,
            assessment_id=assessment_id,
        )

        if assessment is None:
            raise CompressedAirAssessmentNotFoundError("Compressed-air assessment not found.")

        updated = compressed_air_assessment_repository.update_status(
            db,
            assessment=assessment,
            status=request.status.value,
        )

        return CompressedAirAssessmentResponse.model_validate(updated)


compressed_air_assessment_service = CompressedAirAssessmentService()
