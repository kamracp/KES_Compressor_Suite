from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.calculation_case import CalculationCase, CalculationStatus
from app.repositories.calculation_case import calculation_case_repository
from app.repositories.project import project_repository
from app.schemas.calculation_case import (
    CalculationCaseCreate,
    CalculationCaseUpdate,
)


class CalculationCaseAlreadyExistsError(ValueError):
    """Raised when a calculation code already exists."""


class CalculationCaseNotFoundError(LookupError):
    """Raised when a calculation case cannot be found."""


class CalculationCaseProjectNotFoundError(LookupError):
    """Raised when the parent project cannot be found."""


class CalculationCaseService:
    """Business service for compressor engineering calculation cases."""

    def create_case(
        self,
        db: Session,
        payload: CalculationCaseCreate,
    ) -> CalculationCase:
        project = project_repository.get_by_id(
            db,
            payload.project_id,
        )

        if project is None:
            raise CalculationCaseProjectNotFoundError(
                f"Project with id {payload.project_id} was not found."
            )

        existing = calculation_case_repository.get_by_code(
            db,
            payload.calculation_code,
        )

        if existing is not None:
            raise CalculationCaseAlreadyExistsError(
                f"Calculation code '{payload.calculation_code}' already exists."
            )

        calculation_case = calculation_case_repository.create(
            db,
            payload,
        )

        if calculation_case.status == CalculationStatus.COMPLETED.value:
            calculation_case.completed_at = datetime.now(UTC)
            db.commit()
            db.refresh(calculation_case)

        return calculation_case

    def get_case(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> CalculationCase:
        calculation_case = calculation_case_repository.get_by_id(
            db,
            calculation_case_id,
        )

        if calculation_case is None:
            raise CalculationCaseNotFoundError(
                f"Calculation case with id {calculation_case_id} was not found."
            )

        return calculation_case

    def list_cases(
        self,
        db: Session,
    ) -> list[CalculationCase]:
        return calculation_case_repository.list_all(db)

    def list_project_cases(
        self,
        db: Session,
        project_id: int,
    ) -> list[CalculationCase]:
        project = project_repository.get_by_id(
            db,
            project_id,
        )

        if project is None:
            raise CalculationCaseProjectNotFoundError(
                f"Project with id {project_id} was not found."
            )

        return calculation_case_repository.list_by_project(
            db,
            project_id,
        )

    def update_case(
        self,
        db: Session,
        calculation_case_id: int,
        payload: CalculationCaseUpdate,
    ) -> CalculationCase:
        calculation_case = self.get_case(
            db,
            calculation_case_id,
        )

        if payload.calculation_code is not None:
            existing = calculation_case_repository.get_by_code(
                db,
                payload.calculation_code,
            )

            if existing is not None and existing.id != calculation_case.id:
                raise CalculationCaseAlreadyExistsError(
                    f"Calculation code '{payload.calculation_code}' already exists."
                )

        previous_status = calculation_case.status

        calculation_case = calculation_case_repository.update(
            db,
            calculation_case,
            payload,
        )

        if (
            previous_status != CalculationStatus.COMPLETED.value
            and calculation_case.status == CalculationStatus.COMPLETED.value
        ):
            calculation_case.completed_at = datetime.now(UTC)
            db.commit()
            db.refresh(calculation_case)

        if calculation_case.status != CalculationStatus.COMPLETED.value:
            calculation_case.completed_at = None
            db.commit()
            db.refresh(calculation_case)

        return calculation_case

    def delete_case(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> None:
        calculation_case = self.get_case(
            db,
            calculation_case_id,
        )

        calculation_case_repository.delete(
            db,
            calculation_case,
        )


calculation_case_service = CalculationCaseService()
