from sqlalchemy.orm import Session

from app.domain.reporting.audit_summary import (
    CalculationAuditSummary,
    build_audit_summary,
)
from app.domain.reporting.calculation_report import (
    CalculationReport,
    build_calculation_report,
)
from app.services.calculation_case import (
    CalculationCaseNotFoundError,
    calculation_case_service,
)


class ReportingCalculationCaseNotFoundError(LookupError):
    """Raised when a tenant-scoped calculation case cannot be found for reporting."""


class ReportingService:
    """Service for tenant-scoped compressor engineering reporting."""

    def _get_case(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation_case_id: int,
    ):
        try:
            return calculation_case_service.get_case(
                db,
                organization_id=organization_id,
                calculation_case_id=calculation_case_id,
            )
        except CalculationCaseNotFoundError as exc:
            raise ReportingCalculationCaseNotFoundError(
                f"Calculation case with id {calculation_case_id} was not found."
            ) from exc

    def get_calculation_report(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation_case_id: int,
    ) -> CalculationReport:
        calculation_case = self._get_case(
            db,
            organization_id=organization_id,
            calculation_case_id=calculation_case_id,
        )

        return build_calculation_report(calculation_case)

    def get_audit_summary(
        self,
        db: Session,
        *,
        organization_id: int,
        calculation_case_id: int,
    ) -> CalculationAuditSummary:
        calculation_case = self._get_case(
            db,
            organization_id=organization_id,
            calculation_case_id=calculation_case_id,
        )

        return build_audit_summary(calculation_case)


reporting_service = ReportingService()
