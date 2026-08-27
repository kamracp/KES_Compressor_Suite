from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.system_orchestrator import (
    SystemDesignInput,
    SystemDesignOutput,
    system_orchestrator_engine,
)

router = APIRouter(prefix="/system-orchestration", tags=["System Master Orchestration"])

@router.post("/design-plant", response_model=SystemDesignOutput)
def calculate_full_plant_system(
    payload: SystemDesignInput,
    _user = Depends(require_permission("project.read")),
):
    return system_orchestrator_engine.calculate_full_system(payload)
