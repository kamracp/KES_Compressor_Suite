from typing import List
from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.technology_selection import (
    TechSelectionInput,
    TechComparisonResult,
    technology_selection_engine,
)

router = APIRouter(prefix="/technology-selection", tags=["Technology Selection"])

@router.post("/evaluate", response_model=List[TechComparisonResult])
def evaluate_compressor_technologies(
    payload: TechSelectionInput,
    _user = Depends(require_permission("project.read")),
):
    return technology_selection_engine.evaluate(payload)
