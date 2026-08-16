from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.skid.skid_assessment import (
    InvalidAirSkidInputError,
)
from app.schemas.compressed_air_skid import (
    AirSkidAssessmentRequest,
    AirSkidAssessmentResponse,
)
from app.services.compressed_air_skid import compressed_air_skid_service

router = APIRouter(
    prefix="/compressed-air/skid",
    tags=["Compressed Air - Skid Engineering"],
)


@router.post(
    "/assess",
    response_model=AirSkidAssessmentResponse,
    status_code=status.HTTP_200_OK,
)
def assess_compressed_air_skid(
    request: AirSkidAssessmentRequest,
) -> AirSkidAssessmentResponse:
    """Assess compressed-air skid capacity and configuration adequacy."""

    try:
        return compressed_air_skid_service.assess(request)
    except InvalidAirSkidInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
