from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.energy.pressure_energy import (
    InvalidPressureEnergyInputError,
)
from app.domain.compressed_air.performance.performance_analysis import (
    InvalidPerformanceAnalysisInputError,
)
from app.schemas.compressed_air_performance import (
    CompressedAirPerformanceAnalysisRequest,
    CompressedAirPerformanceAnalysisResponse,
)
from app.services.compressed_air_performance import (
    compressed_air_performance_service,
)

router = APIRouter(
    prefix="/compressed-air/performance",
    tags=["Compressed Air - Performance & Energy"],
)


@router.post(
    "/analyze",
    response_model=CompressedAirPerformanceAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_compressed_air_performance(
    request: CompressedAirPerformanceAnalysisRequest,
) -> CompressedAirPerformanceAnalysisResponse:
    """Analyze measured compressed-air performance and energy."""

    try:
        return compressed_air_performance_service.analyze(request)
    except (
        InvalidPerformanceAnalysisInputError,
        InvalidPressureEnergyInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
