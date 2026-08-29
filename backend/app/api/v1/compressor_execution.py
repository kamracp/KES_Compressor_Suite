from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.compressor_execution import (
    CentrifugalExecutionRequest,
    CompressionExecutionRequest,
    ReciprocatingExecutionRequest,
    RotaryScrewExecutionRequest,
    SelectionExecutionRequest,
)
from app.services.calculation_case import (
    CalculationCaseAlreadyExistsError,
    CalculationCaseProjectNotFoundError,
)
from app.services.compressor_execution import (
    InvalidCalculationPersistenceMetadataError,
    compressor_execution_service,
)

router = APIRouter(
    prefix="/compressor-execution",
    tags=["Compressor Execution"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

EngineeringCalculator = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]


def _raise_execution_error(exc: Exception) -> None:
    if isinstance(exc, CalculationCaseAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if isinstance(exc, CalculationCaseProjectNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(exc, InvalidCalculationPersistenceMetadataError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    raise exc


@router.post("/compression")
def execute_compression(
    payload: CompressionExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_compression(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except (
        CalculationCaseAlreadyExistsError,
        CalculationCaseProjectNotFoundError,
        InvalidCalculationPersistenceMetadataError,
    ) as exc:
        _raise_execution_error(exc)

    raise RuntimeError("Unreachable execution path.")


@router.post("/reciprocating")
def execute_reciprocating(
    payload: ReciprocatingExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_reciprocating(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except (
        CalculationCaseAlreadyExistsError,
        CalculationCaseProjectNotFoundError,
        InvalidCalculationPersistenceMetadataError,
    ) as exc:
        _raise_execution_error(exc)

    raise RuntimeError("Unreachable execution path.")


@router.post("/centrifugal")
def execute_centrifugal(
    payload: CentrifugalExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_centrifugal(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except (
        CalculationCaseAlreadyExistsError,
        CalculationCaseProjectNotFoundError,
        InvalidCalculationPersistenceMetadataError,
    ) as exc:
        _raise_execution_error(exc)

    raise RuntimeError("Unreachable execution path.")


@router.post("/selection")
def execute_selection(
    payload: SelectionExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_selection(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except (
        CalculationCaseAlreadyExistsError,
        CalculationCaseProjectNotFoundError,
        InvalidCalculationPersistenceMetadataError,
    ) as exc:
        _raise_execution_error(exc)

    raise RuntimeError("Unreachable execution path.")


@router.post("/rotary-screw")
def execute_rotary_screw(
    payload: RotaryScrewExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_rotary_screw(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except (
        CalculationCaseAlreadyExistsError,
        CalculationCaseProjectNotFoundError,
        InvalidCalculationPersistenceMetadataError,
    ) as exc:
        _raise_execution_error(exc)

    raise RuntimeError("Unreachable execution path.")
