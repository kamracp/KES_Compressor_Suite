from fastapi import APIRouter, status

from app.schemas.compressed_air_advanced import (
    AdvancedEngineeringRequest,
    AdvancedEngineeringResponse,
)
from app.services.compressed_air_advanced import (
    compressed_air_advanced_service,
)

router = APIRouter(
    prefix="/compressed-air/advanced",
    tags=["Compressed Air - Advanced Engineering"],
)


@router.post(
    "/assess",
    response_model=AdvancedEngineeringResponse,
    status_code=status.HTTP_200_OK,
)
def assess_advanced_compressed_air_engineering(
    request: AdvancedEngineeringRequest,
) -> AdvancedEngineeringResponse:
    return compressed_air_advanced_service.assess(request)
