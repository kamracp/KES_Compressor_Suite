from dataclasses import asdict

from sqlalchemy.orm import Session

from app.domain.compressed_air.system.system_summary import (
    CompressedAirSystemSummary,
    SystemAssessmentMode,
    build_compressed_air_system_summary,
)
from app.repositories.compressed_air_assessment import (
    compressed_air_assessment_repository,
)
from app.services.compressed_air_assessment import (
    CompressedAirAssessmentNotFoundError,
)
from app.services.compressed_air_report import (
    compressed_air_report_service,
)


class CompressedAirSystemSummaryService:
    """Application service for project-level compressed-air system summaries."""

    def build_from_assessment(
        self,
        db: Session,
        *,
        assessment_id: int,
    ) -> CompressedAirSystemSummary:
        assessment = compressed_air_assessment_repository.get_by_id(
            db,
            assessment_id,
        )

        if assessment is None:
            raise CompressedAirAssessmentNotFoundError("Compressed-air assessment not found.")

        assessment_mode = self._resolve_assessment_mode(assessment.assessment_type)

        input_payload = assessment.input_payload or {}
        result_payload = assessment.result_payload or {}
        standards_snapshot = assessment.standards_snapshot or {}

        greenfield = self._extract_mode_payload(
            assessment_type=assessment.assessment_type,
            expected_type="GREENFIELD",
            payload=result_payload,
        )

        brownfield = self._extract_mode_payload(
            assessment_type=assessment.assessment_type,
            expected_type="BROWNFIELD",
            payload=result_payload,
        )

        advanced_engineering = self._extract_mode_payload(
            assessment_type=assessment.assessment_type,
            expected_type="ADVANCED",
            payload=result_payload,
        )

        demand_and_capacity = self._extract_dict(
            result_payload,
            "demand_and_capacity",
        )

        pressure = self._extract_dict(
            result_payload,
            "pressure",
        )

        air_treatment = self._extract_dict(
            result_payload,
            "air_treatment",
        )

        storage = self._extract_dict(
            result_payload,
            "storage",
        )

        distribution = self._extract_dict(
            result_payload,
            "distribution",
        )

        energy = self._extract_dict(
            result_payload,
            "energy",
        )

        equipment = self._extract_dict(
            result_payload,
            "equipment_selection",
        )

        recommendations = self._extract_recommendations(result_payload)

        persistence = {
            "assessment_id": assessment.id,
            "assessment_code": assessment.assessment_code,
            "assessment_type": assessment.assessment_type,
            "status": assessment.status,
            "created_by": assessment.created_by,
            "created_at": assessment.created_at.isoformat(),
            "updated_at": assessment.updated_at.isoformat(),
        }

        integrated_report = compressed_air_report_service.build_from_assessment(
            db,
            assessment_id=assessment.id,
            report_code=f"{assessment.assessment_code}-SUMMARY",
            report_title="Compressed Air Integrated Engineering Summary",
        )

        standards = dict(standards_snapshot) if standards_snapshot else None

        if demand_and_capacity is None and input_payload:
            demand_and_capacity = self._extract_dict(
                input_payload,
                "demand_and_capacity",
            )

        return build_compressed_air_system_summary(
            project_id=assessment.project_id,
            assessment_mode=assessment_mode,
            greenfield=greenfield,
            brownfield=brownfield,
            advanced_engineering=advanced_engineering,
            demand_and_capacity=demand_and_capacity,
            pressure=pressure,
            air_treatment=air_treatment,
            storage=storage,
            distribution=distribution,
            energy=energy,
            equipment=equipment,
            standards=standards,
            persistence=persistence,
            integrated_report=asdict(integrated_report),
            recommendations=recommendations,
            assessment_code=assessment.assessment_code,
            calculation_version=assessment.calculation_version,
        )

    @staticmethod
    def _resolve_assessment_mode(
        assessment_type: str,
    ) -> SystemAssessmentMode:
        mapping = {
            "GREENFIELD": SystemAssessmentMode.GREENFIELD,
            "BROWNFIELD": SystemAssessmentMode.BROWNFIELD,
            "ADVANCED": SystemAssessmentMode.ADVANCED,
        }

        return mapping.get(
            assessment_type,
            SystemAssessmentMode.COMBINED,
        )

    @staticmethod
    def _extract_dict(
        payload: dict,
        key: str,
    ) -> dict | None:
        value = payload.get(key)

        if isinstance(value, dict):
            return dict(value)

        return None

    @staticmethod
    def _extract_mode_payload(
        *,
        assessment_type: str,
        expected_type: str,
        payload: dict,
    ) -> dict | None:
        if assessment_type != expected_type:
            return None

        return dict(payload) if payload else {}

    @staticmethod
    def _extract_recommendations(
        payload: dict,
    ) -> tuple[str, ...]:
        value = payload.get("recommendations")

        if isinstance(value, dict):
            items = value.get("items")

            if isinstance(items, list):
                return tuple(str(item) for item in items)

        if isinstance(value, list):
            return tuple(str(item) for item in value)

        return ()


compressed_air_system_summary_service = CompressedAirSystemSummaryService()
