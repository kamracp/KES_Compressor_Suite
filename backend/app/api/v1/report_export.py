from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report_export import CalculationExportPayloadResponse
from app.services.report_export import report_export_service
from app.services.reporting import ReportingCalculationCaseNotFoundError

router = APIRouter(
    prefix="/report-export",
    tags=["Report Export"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/calculation-cases/{calculation_case_id}/json",
    response_model=CalculationExportPayloadResponse,
)
def export_calculation_case_json(
    calculation_case_id: int,
    db: DatabaseSession,
) -> CalculationExportPayloadResponse:
    try:
        return report_export_service.get_export_payload(
            db,
            calculation_case_id,
        )
    except ReportingCalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
