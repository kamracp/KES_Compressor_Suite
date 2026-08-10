from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.consumers.consumer_demand import (
    InvalidAirConsumerInputError,
)
from app.domain.compressed_air.demand.plant_demand import (
    InvalidPlantDemandInputError,
)
from app.domain.compressed_air.energy.system_energy import (
    InvalidSystemEnergyInputError,
)
from app.domain.compressed_air.greenfield.system_design import (
    InvalidGreenfieldSystemDesignInputError,
)
from app.domain.compressed_air.pressure.pressure_budget import (
    InvalidPressureBudgetInputError,
)
from app.domain.compressed_air.profiles.demand_profile import (
    InvalidDemandProfileInputError,
)
from app.domain.compressed_air.station.capacity import (
    InvalidStationCapacityInputError,
)
from app.domain.compressed_air.storage.receiver_sizing import (
    InvalidReceiverSizingInputError,
)
from app.domain.compressed_air.treatment.air_treatment import (
    InvalidAirTreatmentInputError,
)
from app.schemas.compressed_air_greenfield import (
    GreenfieldSystemDesignRequest,
    GreenfieldSystemDesignResponse,
)
from app.services.compressed_air_greenfield import (
    compressed_air_greenfield_service,
)

router = APIRouter(
    prefix="/compressed-air/greenfield",
    tags=["Compressed Air - Greenfield Design"],
)


@router.post(
    "/design",
    response_model=GreenfieldSystemDesignResponse,
    status_code=status.HTTP_200_OK,
)
def design_greenfield_compressed_air_system(
    request: GreenfieldSystemDesignRequest,
) -> GreenfieldSystemDesignResponse:
    try:
        return compressed_air_greenfield_service.design(request)

    except (
        InvalidAirConsumerInputError,
        InvalidPlantDemandInputError,
        InvalidDemandProfileInputError,
        InvalidPressureBudgetInputError,
        InvalidAirTreatmentInputError,
        InvalidStationCapacityInputError,
        InvalidReceiverSizingInputError,
        InvalidSystemEnergyInputError,
        InvalidGreenfieldSystemDesignInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
