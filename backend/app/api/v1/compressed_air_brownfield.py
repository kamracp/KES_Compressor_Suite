from fastapi import APIRouter, HTTPException, status

from app.domain.compressed_air.brownfield.audit_analysis import (
    InvalidBrownfieldAuditInputError,
)
from app.domain.compressed_air.brownfield.sequencing_bridge import (
    InvalidBrownfieldSequencingInputError,
)
from app.domain.compressed_air.brownfield.system_engine import (
    InvalidBrownfieldSystemEngineInputError,
)
from app.domain.compressed_air.energy.leakage_energy import (
    InvalidLeakageEnergyInputError,
)
from app.domain.compressed_air.energy.pressure_energy import (
    InvalidPressureEnergyInputError,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    InvalidSequencingInputError,
)
from app.schemas.compressed_air_brownfield import (
    BrownfieldSystemAuditRequest,
    BrownfieldSystemAuditResponse,
)
from app.services.compressed_air_brownfield import (
    compressed_air_brownfield_service,
)

router = APIRouter(
    prefix="/compressed-air/brownfield",
    tags=["Compressed Air - Brownfield Audit"],
)


@router.post(
    "/audit",
    response_model=BrownfieldSystemAuditResponse,
    status_code=status.HTTP_200_OK,
)
def audit_existing_compressed_air_system(
    request: BrownfieldSystemAuditRequest,
) -> BrownfieldSystemAuditResponse:
    try:
        return compressed_air_brownfield_service.analyze(request)

    except (
        InvalidBrownfieldAuditInputError,
        InvalidBrownfieldSystemEngineInputError,
        InvalidBrownfieldSequencingInputError,
        InvalidSequencingInputError,
        InvalidLeakageEnergyInputError,
        InvalidPressureEnergyInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
