from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.domain.compressed_air.reporting.system_report import (
    IntegratedEngineeringReport,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
)
from app.services.compressed_air_report import compressed_air_report_service

router = APIRouter(
    prefix="/compressed-air/report",
    tags=["Compressed Air - Integrated Engineering Report"],
)

DbSession = Annotated[Session, Depends(get_db)]
ReportCodeQuery = Annotated[str, Query(min_length=1, max_length=100)]
ReportTitleQuery = Annotated[str, Query(min_length=1, max_length=255)]

ReportReader = Annotated[
    CurrentUser,
    Depends(require_permission("report.read")),
]


@router.get(
    "/assessment/{assessment_id}",
    response_model=IntegratedEngineeringReport,
    status_code=status.HTTP_200_OK,
)
def build_compressed_air_report(
    assessment_id: int,
    db: DbSession,
    current_user: ReportReader,
    report_code: ReportCodeQuery,
    report_title: ReportTitleQuery,
) -> IntegratedEngineeringReport:
    try:
        return compressed_air_report_service.build_from_assessment(
            db,
            organization_id=current_user.organization_id,
            assessment_id=assessment_id,
            report_code=report_code,
            report_title=report_title,
        )
    except CompressedAirAssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
