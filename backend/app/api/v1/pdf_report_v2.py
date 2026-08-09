from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pdf_report_v2 import (
    PdfReportV2GenerationError,
    pdf_report_v2_service,
)
from app.services.report_export import report_export_service
from app.services.reporting import ReportingCalculationCaseNotFoundError

router = APIRouter(
    prefix="/pdf-report-v2",
    tags=["PDF Report V2"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/calculation-cases/{calculation_case_id}",
    response_class=StreamingResponse,
)
def download_structured_calculation_pdf(
    calculation_case_id: int,
    db: DatabaseSession,
) -> StreamingResponse:
    try:
        payload = report_export_service.get_export_payload(
            db,
            calculation_case_id,
        )

        pdf_bytes = pdf_report_v2_service.generate_calculation_report(
            payload,
        )

    except ReportingCalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except PdfReportV2GenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    filename = f"{payload.calculation_code}_rev{payload.revision}_engineering_report.pdf"

    headers = {"Content-Disposition": (f'attachment; filename="{filename}"')}

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )
