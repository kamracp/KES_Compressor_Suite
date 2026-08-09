from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.compressed_air_assessment import (
    CompressedAirAssessmentCreateRequest,
    CompressedAirAssessmentListResponse,
    CompressedAirAssessmentResponse,
    CompressedAirAssessmentStatusUpdateRequest,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
    DuplicateCompressedAirAssessmentCodeError,
    compressed_air_assessment_service,
)

router = APIRouter(
    prefix="/compressed-air/assessments",
    tags=["Compressed Air - Assessment History"],
)

DbSession = Annotated[Session, Depends(get_db)]
AssessmentTypeQuery = Annotated[str | None, Query()]


@router.post(
    "",
    response_model=CompressedAirAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_compressed_air_assessment(
    request: CompressedAirAssessmentCreateRequest,
    db: DbSession,
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.create(
            db,
            request,
        )
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
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.get_by_id(
            db,
            assessment_id,
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
    assessment_type: AssessmentTypeQuery = None,
) -> CompressedAirAssessmentListResponse:
    if assessment_type is None:
        return compressed_air_assessment_service.list_by_project(
            db,
            project_id,
        )

    return compressed_air_assessment_service.list_by_project_and_type(
        db,
        project_id=project_id,
        assessment_type=assessment_type,
    )


@router.patch(
    "/{assessment_id}/status",
    response_model=CompressedAirAssessmentResponse,
)
def update_compressed_air_assessment_status(
    assessment_id: int,
    request: CompressedAirAssessmentStatusUpdateRequest,
    db: DbSession,
) -> CompressedAirAssessmentResponse:
    try:
        return compressed_air_assessment_service.update_status(
            db,
            assessment_id=assessment_id,
            request=request,
        )
    except CompressedAirAssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
