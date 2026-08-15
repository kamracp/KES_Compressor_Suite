from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.allied.allied_analysis import (
    InvalidAlliedEquipmentInputError,
)
from app.domain.compressed_air.storage.receiver_sizing import (
    InvalidReceiverSizingInputError,
)
from app.domain.compressed_air.treatment.air_treatment import (
    InvalidAirTreatmentInputError,
)
from app.schemas.compressed_air_allied import (
    AlliedEquipmentAnalysisRequest,
    AlliedEquipmentAnalysisResponse,
)
from app.services.compressed_air_allied import (
    compressed_air_allied_service,
)

router = APIRouter(
    prefix="/compressed-air/allied",
    tags=["Compressed Air - Allied Equipment"],
)


@router.post(
    "/analyze",
    response_model=AlliedEquipmentAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_compressed_air_allied_equipment(
    request: AlliedEquipmentAnalysisRequest,
) -> AlliedEquipmentAnalysisResponse:
    """Analyze compressed-air allied equipment and capacity adequacy."""

    try:
        return compressed_air_allied_service.analyze(request)
    except (
        InvalidAlliedEquipmentInputError,
        InvalidReceiverSizingInputError,
        InvalidAirTreatmentInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
