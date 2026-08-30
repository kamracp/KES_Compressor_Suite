from dataclasses import asdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.domain.compressed_air.distribution.network_optimizer import (
    InvalidNetworkOptimizationInputError,
)
from app.domain.compressed_air.distribution.network_solver import (
    InvalidNetworkSolverInputError,
)
from app.domain.compressed_air.distribution.network_validation import (
    InvalidCompressedAirNetworkError,
)
from app.domain.compressed_air.distribution.path_solver import (
    InvalidNetworkPathError,
)
from app.domain.compressed_air.distribution.pipe_sizing import (
    InvalidPipeSizingInputError,
)
from app.domain.compressed_air.distribution.pressure_drop import (
    InvalidPressureDropInputError,
)
from app.schemas.compressed_air_distribution import (
    DistributionNetworkCalculationRequest,
    DistributionNetworkExecutionRequest,
)
from app.services.calculation_case import (
    CalculationCaseAlreadyExistsError,
    CalculationCaseProjectNotFoundError,
)
from app.services.compressed_air_distribution import (
    compressed_air_distribution_service,
)
from app.services.compressor_execution import (
    InvalidCalculationPersistenceMetadataError,
    compressor_execution_service,
)

router = APIRouter(
    prefix="/compressed-air/distribution",
    tags=["Compressed Air - Distribution Network"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

EngineeringCalculator = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]

DOMAIN_INPUT_ERRORS = (
    InvalidCompressedAirNetworkError,
    InvalidNetworkSolverInputError,
    InvalidNetworkPathError,
    InvalidPipeSizingInputError,
    InvalidPressureDropInputError,
    InvalidNetworkOptimizationInputError,
)


@router.post("/calculate")
def calculate_distribution_network(
    payload: DistributionNetworkCalculationRequest,
) -> dict[str, Any]:
    """Validate, hydraulically solve and optionally optimize a network."""

    try:
        return asdict(compressed_air_distribution_service.calculate(payload))
    except DOMAIN_INPUT_ERRORS as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.post("/execute")
def execute_distribution_network(
    payload: DistributionNetworkExecutionRequest,
    db: DatabaseSession,
    current_user: EngineeringCalculator,
) -> dict[str, Any]:
    """Run the distribution analysis and optionally persist the result."""

    try:
        return compressor_execution_service.execute_distribution(
            db,
            organization_id=current_user.organization_id,
            calculation=payload.calculation,
            execution=payload.execution,
        )
    except DOMAIN_INPUT_ERRORS as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
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
    except InvalidCalculationPersistenceMetadataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
