from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.multi_compressor import (
    StationInput,
    StationOutput,
    multi_compressor_engine,
)

router = APIRouter(prefix="/multi-compressor", tags=["Multi-Compressor Station"])

@router.post("/evaluate", response_model=StationOutput)
def evaluate_multi_compressor_station(
    payload: StationInput,
    _user = Depends(require_permission("project.read")),
):
    return multi_compressor_engine.calculate(payload)
