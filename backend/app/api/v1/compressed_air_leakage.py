from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.energy.leakage_energy import (
    InvalidLeakageEnergyInputError,
)
from app.domain.compressed_air.leakage.leakage_analysis import (
    InvalidLeakageManagementInputError,
)
from app.schemas.compressed_air_leakage import (
    CompressedAirLeakageManagementRequest,
    CompressedAirLeakageManagementResponse,
)
from app.services.compressed_air_leakage import (
    compressed_air_leakage_service,
)

router = APIRouter(
    prefix="/compressed-air/leakage",
    tags=["Compressed Air - Leakage Management"],
)


@router.post(
    "/analyze",
    response_model=CompressedAirLeakageManagementResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_compressed_air_leakage(
    request: CompressedAirLeakageManagementRequest,
) -> CompressedAirLeakageManagementResponse:
    """Analyze a compressed-air leakage register and repair opportunity."""

    try:
        return compressed_air_leakage_service.analyze(request)

    except (
        InvalidLeakageManagementInputError,
        InvalidLeakageEnergyInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
