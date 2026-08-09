from sqlalchemy.orm import Session

from app.domain.reporting.export_payload import (
    CalculationExportPayload,
    build_export_payload,
)
from app.services.reporting import (
    ReportingCalculationCaseNotFoundError,
    reporting_service,
)


class ReportExportService:
    """Service for compressor engineering report exports."""

    def get_export_payload(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> CalculationExportPayload:
        """Build an export-ready payload for a calculation case."""

        try:
            report = reporting_service.get_calculation_report(
                db,
                calculation_case_id,
            )
        except ReportingCalculationCaseNotFoundError:
            raise

        return build_export_payload(report)


report_export_service = ReportExportService()
