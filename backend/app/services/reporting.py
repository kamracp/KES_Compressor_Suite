from sqlalchemy.orm import Session

from app.domain.reporting.audit_summary import (
    CalculationAuditSummary,
    build_audit_summary,
)
from app.domain.reporting.calculation_report import (
    CalculationReport,
    build_calculation_report,
)
from app.repositories.calculation_case import calculation_case_repository


class ReportingCalculationCaseNotFoundError(LookupError):
    """Raised when a calculation case cannot be found for reporting."""


class ReportingService:
    """Service for compressor engineering reports and audit summaries."""

    def _get_case(
        self,
        db: Session,
        calculation_case_id: int,
    ):
        calculation_case = calculation_case_repository.get_by_id(
            db,
            calculation_case_id,
        )

        if calculation_case is None:
            raise ReportingCalculationCaseNotFoundError(
                f"Calculation case with id {calculation_case_id} was not found."
            )

        return calculation_case

    def get_calculation_report(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> CalculationReport:
        calculation_case = self._get_case(
            db,
            calculation_case_id,
        )

        return build_calculation_report(calculation_case)

    def get_audit_summary(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> CalculationAuditSummary:
        calculation_case = self._get_case(
            db,
            calculation_case_id,
        )

        return build_audit_summary(calculation_case)


reporting_service = ReportingService()
