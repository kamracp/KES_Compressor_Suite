from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.schemas.gas_properties import (
    GasPropertiesRequest,
    GasPropertiesResponse,
)
from app.services.gas_properties import gas_properties_service

router = APIRouter(
    prefix="/compressor/gas-properties",
    tags=["Compressor Engineering - Gas Properties"],
)

EngineeringCalculator = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]


@router.post(
    "/calculate",
    response_model=GasPropertiesResponse,
    status_code=status.HTTP_200_OK,
)
def calculate_gas_properties(
    request: GasPropertiesRequest,
    current_user: EngineeringCalculator,
) -> GasPropertiesResponse:
    del current_user

    try:
        return gas_properties_service.calculate(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
