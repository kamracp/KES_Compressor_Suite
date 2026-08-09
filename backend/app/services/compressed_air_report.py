from sqlalchemy.orm import Session

from app.domain.compressed_air.reporting.system_report import (
    IntegratedEngineeringReport,
    build_integrated_engineering_report,
)
from app.repositories.compressed_air_assessment import (
    compressed_air_assessment_repository,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
)


class CompressedAirReportService:
    """Application service for integrated compressed-air engineering reports."""

    def build_from_assessment(
        self,
        db: Session,
        *,
        assessment_id: int,
        report_code: str,
        report_title: str,
    ) -> IntegratedEngineeringReport:
        assessment = compressed_air_assessment_repository.get_by_id(
            db,
            assessment_id,
        )

        if assessment is None:
            raise CompressedAirAssessmentNotFoundError("Compressed-air assessment not found.")

        input_payload = assessment.input_payload or {}
        result_payload = assessment.result_payload or {}
        standards_snapshot = assessment.standards_snapshot or {}

        design_basis = self._extract_section(
            input_payload,
            "design_basis",
        )

        demand_and_capacity = self._extract_section(
            result_payload,
            "demand_and_capacity",
        )

        equipment_selection = self._extract_section(
            result_payload,
            "equipment_selection",
        )

        air_treatment = self._extract_section(
            result_payload,
            "air_treatment",
        )

        storage = self._extract_section(
            result_payload,
            "storage",
        )

        distribution = self._extract_section(
            result_payload,
            "distribution",
        )

        energy = self._extract_section(
            result_payload,
            "energy",
        )

        brownfield_audit = self._extract_section(
            result_payload,
            "brownfield_audit",
        )

        advanced_engineering = self._extract_section(
            result_payload,
            "advanced_engineering",
        )

        recommendations = self._extract_section(
            result_payload,
            "recommendations",
        )

        if design_basis is None and input_payload:
            design_basis = dict(input_payload)

        if (
            demand_and_capacity is None
            and result_payload
            and assessment.assessment_type == "GREENFIELD"
        ):
            demand_and_capacity = dict(result_payload)

        if (
            brownfield_audit is None
            and result_payload
            and assessment.assessment_type == "BROWNFIELD"
        ):
            brownfield_audit = dict(result_payload)

        if (
            advanced_engineering is None
            and result_payload
            and assessment.assessment_type == "ADVANCED"
        ):
            advanced_engineering = dict(result_payload)

        standards_and_compliance = dict(standards_snapshot) if standards_snapshot else None

        audit_trail = {
            "assessment_id": assessment.id,
            "assessment_code": assessment.assessment_code,
            "assessment_type": assessment.assessment_type,
            "assessment_status": assessment.status,
            "calculation_version": assessment.calculation_version,
            "created_by": assessment.created_by,
            "created_at": assessment.created_at.isoformat(),
            "updated_at": assessment.updated_at.isoformat(),
        }

        return build_integrated_engineering_report(
            project_id=assessment.project_id,
            report_code=report_code,
            title=report_title,
            assessment_type=assessment.assessment_type,
            design_basis=design_basis,
            demand_and_capacity=demand_and_capacity,
            equipment_selection=equipment_selection,
            air_treatment=air_treatment,
            storage=storage,
            distribution=distribution,
            energy=energy,
            brownfield_audit=brownfield_audit,
            advanced_engineering=advanced_engineering,
            standards_and_compliance=standards_and_compliance,
            recommendations=recommendations,
            audit_trail=audit_trail,
            generated_from_assessment_code=assessment.assessment_code,
            calculation_version=assessment.calculation_version,
        )

    @staticmethod
    def _extract_section(
        payload: dict,
        key: str,
    ) -> dict | None:
        value = payload.get(key)

        if isinstance(value, dict):
            return dict(value)

        return None


compressed_air_report_service = CompressedAirReportService()
