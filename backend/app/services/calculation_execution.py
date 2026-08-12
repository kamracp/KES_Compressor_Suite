from dataclasses import asdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.calculation_case import (
    CalculationCase,
    CalculationStatus,
    CalculationType,
)
from app.repositories.calculation_case import calculation_case_repository
from app.repositories.project import project_repository
from app.schemas.calculation_case import CalculationCaseCreate
from app.services.calculation_case import (
    CalculationCaseAlreadyExistsError,
    CalculationCaseProjectNotFoundError,
)


class UnsupportedCalculationExecutionError(ValueError):
    """Raised when a calculation execution type is unsupported."""


class CalculationExecutionService:
    """Persist tenant-scoped completed compressor engineering calculations."""

    def _validate_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> None:
        project = project_repository.get_by_id(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        if project is None:
            raise CalculationCaseProjectNotFoundError(
                f"Project with id {project_id} was not found."
            )

    def _validate_calculation_code(
        self,
        db: Session,
        calculation_code: str,
    ) -> None:
        statement = select(CalculationCase).where(
            CalculationCase.calculation_code == calculation_code
        )

        existing = db.scalar(statement)

        if existing is not None:
            raise CalculationCaseAlreadyExistsError(
                f"Calculation case '{calculation_code}' already exists."
            )

    def persist_execution(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
        calculation_code: str,
        calculation_type: CalculationType,
        title: str,
        input_data: dict[str, Any],
        result: Any,
        engineering_notes: str | None = None,
    ) -> CalculationCase:
        """Persist a completed calculation within a tenant-owned project."""

        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        self._validate_calculation_code(
            db,
            calculation_code,
        )

        result_data = asdict(result)

        payload = CalculationCaseCreate(
            project_id=project_id,
            calculation_code=calculation_code,
            calculation_type=calculation_type,
            status=CalculationStatus.COMPLETED,
            revision=1,
            title=title,
            input_data=input_data,
            result_data=result_data,
            engineering_notes=engineering_notes,
        )

        try:
            calculation_case = calculation_case_repository.create(
                db,
                payload,
            )
        except IntegrityError as exc:
            db.rollback()

            raise CalculationCaseAlreadyExistsError(
                f"Calculation case '{calculation_code}' already exists."
            ) from exc

        return calculation_case


calculation_execution_service = CalculationExecutionService()
