from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.compressed_air_assessment import (
    CompressedAirAssessmentCreateRequest,
    CompressedAirAssessmentListResponse,
    CompressedAirAssessmentResponse,
    CompressedAirAssessmentStatusUpdateRequest,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
    CompressedAirAssessmentProjectNotFoundError,
    DuplicateCompressedAirAssessmentCodeError,
    compressed_air_assessment_service,
)

router = APIRouter(
    prefix="/compressed-air/assessments",
    tags=["Compressed Air - Assessment History"],
)

DbSession = Annotated[Session, Depends(get_db)]
AssessmentTypeQuery = Annotated[str | None, Query()]

AssessmentReader = Annotated[
    CurrentUser,
    Depends(require_permission("assessment.read")),
]

AssessmentWriter = Annotated[
    CurrentUser,
    Depends(require_permission("assessment.write")),
]


@router.post(
    "",
    response_model=CompressedAirAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_compressed_air_assessment(
    request: CompressedAirAssessmentCreateRequest,
    db: DbSession,
    current_user: AssessmentWriter,
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.create(
            db,
            organization_id=current_user.organization_id,
            request=request,
        )
    except CompressedAirAssessmentProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateCompressedAirAssessmentCodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{assessment_id}",
    response_model=CompressedAirAssessmentResponse,
)
def get_compressed_air_assessment(
    assessment_id: int,
    db: DbSession,
    current_user: AssessmentReader,
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.get_by_id(
            db,
            organization_id=current_user.organization_id,
            assessment_id=assessment_id,
        )
    except CompressedAirAssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/project/{project_id}",
    response_model=CompressedAirAssessmentListResponse,
)
def list_compressed_air_assessments(
    project_id: int,
    db: DbSession,
    current_user: AssessmentReader,
    assessment_type: AssessmentTypeQuery = None,
) -> CompressedAirAssessmentListResponse:
    try:
        if assessment_type is None:
            return compressed_air_assessment_service.list_by_project(
                db,
                organization_id=current_user.organization_id,
                project_id=project_id,
            )

        return compressed_air_assessment_service.list_by_project_and_type(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
            assessment_type=assessment_type,
        )
    except CompressedAirAssessmentProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{assessment_id}/status",
    response_model=CompressedAirAssessmentResponse,
)
def update_compressed_air_assessment_status(
    assessment_id: int,
    request: CompressedAirAssessmentStatusUpdateRequest,
    db: DbSession,
    current_user: AssessmentWriter,
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.update_status(
            db,
            organization_id=current_user.organization_id,
            assessment_id=assessment_id,
            request=request,
        )
    except CompressedAirAssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
