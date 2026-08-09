from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.calculation_case import (
    CalculationCaseCreate,
    CalculationCaseRead,
    CalculationCaseUpdate,
)
from app.services.calculation_case import (
    CalculationCaseAlreadyExistsError,
    CalculationCaseNotFoundError,
    CalculationCaseProjectNotFoundError,
    calculation_case_service,
)

router = APIRouter(
    prefix="/calculation-cases",
    tags=["Calculation Cases"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=CalculationCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_calculation_case(
    payload: CalculationCaseCreate,
    db: DatabaseSession,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.create_case(db, payload)
    except CalculationCaseAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except CalculationCaseProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[CalculationCaseRead],
)
def list_calculation_cases(
    db: DatabaseSession,
) -> list[CalculationCaseRead]:
    return calculation_case_service.list_cases(db)


@router.get(
    "/project/{project_id}",
    response_model=list[CalculationCaseRead],
)
def list_project_calculation_cases(
    project_id: int,
    db: DatabaseSession,
) -> list[CalculationCaseRead]:
    try:
        return calculation_case_service.list_project_cases(
            db,
            project_id,
        )
    except CalculationCaseProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{calculation_case_id}",
    response_model=CalculationCaseRead,
)
def get_calculation_case(
    calculation_case_id: int,
    db: DatabaseSession,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.get_case(
            db,
            calculation_case_id,
        )
    except CalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{calculation_case_id}",
    response_model=CalculationCaseRead,
)
def update_calculation_case(
    calculation_case_id: int,
    payload: CalculationCaseUpdate,
    db: DatabaseSession,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.update_case(
            db,
            calculation_case_id,
            payload,
        )
    except CalculationCaseAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except CalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{calculation_case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calculation_case(
    calculation_case_id: int,
    db: DatabaseSession,
) -> Response:
    try:
        calculation_case_service.delete_case(
            db,
            calculation_case_id,
        )
    except CalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
