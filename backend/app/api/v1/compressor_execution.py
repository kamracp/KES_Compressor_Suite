from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.compressor_execution import (
    CentrifugalExecutionRequest,
    CompressionExecutionRequest,
    ReciprocatingExecutionRequest,
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
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_compression(
            db,
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
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_reciprocating(
            db,
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
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_centrifugal(
            db,
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
) -> dict[str, Any]:
    try:
        return compressor_execution_service.execute_selection(
            db,
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
