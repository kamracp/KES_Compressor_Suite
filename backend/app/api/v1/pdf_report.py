from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pdf_report import PdfReportGenerationError, pdf_report_service
from app.services.report_export import report_export_service
from app.services.reporting import ReportingCalculationCaseNotFoundError

router = APIRouter(
    prefix="/pdf-report",
    tags=["PDF Report"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/calculation-cases/{calculation_case_id}",
    response_class=StreamingResponse,
)
def download_calculation_pdf(
    calculation_case_id: int,
    db: DatabaseSession,
) -> StreamingResponse:
    try:
        payload = report_export_service.get_export_payload(
            db,
            calculation_case_id,
        )

        pdf_bytes = pdf_report_service.generate_calculation_report(
            payload,
        )

    except ReportingCalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except PdfReportGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    filename = f"{payload.calculation_code}_rev{payload.revision}.pdf"

    headers = {"Content-Disposition": (f'attachment; filename="{filename}"')}

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )
