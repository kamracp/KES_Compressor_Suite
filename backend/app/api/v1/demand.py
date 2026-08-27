from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.demand import (
    DemandCalculationInput,
    DemandCalculationOutput,
    demand_engine,
)

router = APIRouter(prefix="/demand", tags=["Factory Air Demand"])

@router.post("/calculate", response_model=DemandCalculationOutput)
def calculate_factory_demand(
    payload: DemandCalculationInput,
    _user = Depends(require_permission("project.read")),
):
    return demand_engine.calculate(payload)
