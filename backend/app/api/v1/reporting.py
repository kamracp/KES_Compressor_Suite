from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.reporting import (
    CalculationAuditSummaryResponse,
    CalculationReportResponse,
)
from app.services.reporting import (
    ReportingCalculationCaseNotFoundError,
    reporting_service,
)

router = APIRouter(
    prefix="/reporting",
    tags=["Reporting"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

ReportReader = Annotated[
    CurrentUser,
    Depends(require_permission("report.read")),
]


@router.get(
    "/calculation-cases/{calculation_case_id}/report",
    response_model=CalculationReportResponse,
)
def get_calculation_report(
    calculation_case_id: int,
    db: DatabaseSession,
    current_user: ReportReader,
) -> CalculationReportResponse:
    try:
        return reporting_service.get_calculation_report(
            db,
            organization_id=current_user.organization_id,
            calculation_case_id=calculation_case_id,
        )
    except ReportingCalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/calculation-cases/{calculation_case_id}/audit-summary",
    response_model=CalculationAuditSummaryResponse,
)
def get_calculation_audit_summary(
    calculation_case_id: int,
    db: DatabaseSession,
    current_user: ReportReader,
) -> CalculationAuditSummaryResponse:
    try:
        return reporting_service.get_audit_summary(
            db,
            organization_id=current_user.organization_id,
            calculation_case_id=calculation_case_id,
        )
    except ReportingCalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
