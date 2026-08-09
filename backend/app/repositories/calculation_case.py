from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.calculation_case import CalculationCase
from app.schemas.calculation_case import (
    CalculationCaseCreate,
    CalculationCaseUpdate,
)


class CalculationCaseRepository:
    """Repository for compressor engineering calculation cases."""

    def create(
        self,
        db: Session,
        payload: CalculationCaseCreate,
    ) -> CalculationCase:
        calculation_case = CalculationCase(
            **payload.model_dump(mode="json"),
        )

        db.add(calculation_case)
        db.commit()
        db.refresh(calculation_case)

        return calculation_case

    def get_by_id(
        self,
        db: Session,
        calculation_case_id: int,
    ) -> CalculationCase | None:
        return db.get(CalculationCase, calculation_case_id)

    def get_by_code(
        self,
        db: Session,
        calculation_code: str,
    ) -> CalculationCase | None:
        statement = select(CalculationCase).where(
            CalculationCase.calculation_code == calculation_code
        )

        return db.scalar(statement)

    def list_all(
        self,
        db: Session,
    ) -> list[CalculationCase]:
        statement = select(CalculationCase).order_by(
            CalculationCase.id,
        )

        return list(db.scalars(statement).all())

    def list_by_project(
        self,
        db: Session,
        project_id: int,
    ) -> list[CalculationCase]:
        statement = (
            select(CalculationCase)
            .where(CalculationCase.project_id == project_id)
            .order_by(CalculationCase.id)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        calculation_case: CalculationCase,
        payload: CalculationCaseUpdate,
    ) -> CalculationCase:
        update_data = payload.model_dump(
            exclude_unset=True,
            mode="json",
        )

        for field, value in update_data.items():
            setattr(calculation_case, field, value)

        db.add(calculation_case)
        db.commit()
        db.refresh(calculation_case)

        return calculation_case

    def delete(
        self,
        db: Session,
        calculation_case: CalculationCase,
    ) -> None:
        db.delete(calculation_case)
        db.commit()


calculation_case_repository = CalculationCaseRepository()
