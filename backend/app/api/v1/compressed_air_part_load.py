from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.schemas.compressed_air_part_load import (
    PartLoadComparisonRequest,
    PartLoadComparisonResponse,
)
from app.services.compressed_air_part_load import compressed_air_part_load_service

router = APIRouter(
    prefix="/compressed-air/performance",
    tags=["Compressed Air - Performance"],
)

EngineeringCalculator = Annotated[
    CurrentUser,
    Depends(require_permission("engineering.calculate")),
]


@router.post(
    "/part-load",
    response_model=PartLoadComparisonResponse,
    status_code=status.HTTP_200_OK,
)
def compare_part_load_modes(
    request: PartLoadComparisonRequest,
    current_user: EngineeringCalculator,
) -> PartLoadComparisonResponse:
    """Compare control-mode part-load curves for one machine (C-8)."""
    del current_user
    try:
        return compressed_air_part_load_service.compare(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
