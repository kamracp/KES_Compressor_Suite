from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.air_dryer import (
    AirDryerInput,
    AirDryerOutput,
    air_dryer_engine,
)

router = APIRouter(prefix="/air-dryer", tags=["Air Dryer & Filtration"])

@router.post("/size", response_model=AirDryerOutput)
def size_air_dryer(
    payload: AirDryerInput,
    _user = Depends(require_permission("project.read")),
):
    return air_dryer_engine.calculate(payload)
