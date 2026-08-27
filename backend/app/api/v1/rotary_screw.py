from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.rotary_screw import RotaryScrewInput, RotaryScrewOutput, rotary_screw_engine

router = APIRouter(prefix="/rotary-screw", tags=["Rotary Screw Engineering"])

@router.post("/calculate", response_model=RotaryScrewOutput)
def calculate_rotary_screw(
    payload: RotaryScrewInput,
    _user = Depends(require_permission("project.read")),
):
    return rotary_screw_engine.calculate(payload)
