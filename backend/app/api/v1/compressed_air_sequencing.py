from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.schemas.compressed_air_sequencing import (
    SequencingAssessmentRequest,
    SequencingAssessmentResponse,
)
from app.services.compressed_air_sequencing import compressed_air_sequencing_service

router = APIRouter(
    prefix="/compressed-air/sequencing",
    tags=["Compressed Air - Sequencing"],
)

EngineeringCalculator = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]


@router.post(
    "/assess",
    response_model=SequencingAssessmentResponse,
    status_code=status.HTTP_200_OK,
)
def assess_sequencing(
    request: SequencingAssessmentRequest,
    current_user: EngineeringCalculator,
) -> SequencingAssessmentResponse:
    del current_user
    try:
        return compressed_air_sequencing_service.assess(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
