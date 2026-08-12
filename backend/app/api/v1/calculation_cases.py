from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
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

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

CalculationReader = Annotated[
    CurrentUser,
    Depends(require_permission("project.read")),
]

CalculationWriter = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]


@router.post(
    "",
    response_model=CalculationCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_calculation_case(
    payload: CalculationCaseCreate,
    db: DatabaseSession,
    current_user: CalculationWriter,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.create_case(
            db,
            organization_id=current_user.organization_id,
            payload=payload,
        )
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
    current_user: CalculationReader,
) -> list[CalculationCaseRead]:
    return calculation_case_service.list_cases(
        db,
        organization_id=current_user.organization_id,
    )


@router.get(
    "/project/{project_id}",
    response_model=list[CalculationCaseRead],
)
def list_project_calculation_cases(
    project_id: int,
    db: DatabaseSession,
    current_user: CalculationReader,
) -> list[CalculationCaseRead]:
    try:
        return calculation_case_service.list_project_cases(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
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
    current_user: CalculationReader,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.get_case(
            db,
            organization_id=current_user.organization_id,
            calculation_case_id=calculation_case_id,
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
    current_user: CalculationWriter,
) -> CalculationCaseRead:
    try:
        return calculation_case_service.update_case(
            db,
            organization_id=current_user.organization_id,
            calculation_case_id=calculation_case_id,
            payload=payload,
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
    current_user: CalculationWriter,
) -> Response:
    try:
        calculation_case_service.delete_case(
            db,
            organization_id=current_user.organization_id,
            calculation_case_id=calculation_case_id,
        )
    except CalculationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
