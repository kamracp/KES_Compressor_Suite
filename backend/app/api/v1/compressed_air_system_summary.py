from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.compressed_air.system.system_summary import (
    CompressedAirSystemSummary,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
)
from app.services.compressed_air_system_summary import (
    compressed_air_system_summary_service,
)

router = APIRouter(
    prefix="/compressed-air/system-summary",
    tags=["Compressed Air - System Summary"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/assessment/{assessment_id}",
    response_model=CompressedAirSystemSummary,
    status_code=status.HTTP_200_OK,
)
def build_compressed_air_system_summary(
    assessment_id: int,
    db: DbSession,
) -> CompressedAirSystemSummary:
    try:
        return compressed_air_system_summary_service.build_from_assessment(
            db,
            assessment_id=assessment_id,
        )
    except CompressedAirAssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
