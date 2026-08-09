from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCalculationHistoryItemResponse(BaseModel):
    """API response item for one project calculation history entry."""

    model_config = ConfigDict(from_attributes=True)

    calculation_case_id: int
    calculation_code: str
    calculation_type: str
    status: str
    revision: int
    title: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ProjectCalculationHistoryResponse(BaseModel):
    """API response for project-level compressor calculation history."""

    model_config = ConfigDict(from_attributes=True)

    project_id: int
    total_cases: int
    completed_cases: int
    draft_cases: int
    latest_case_id: int | None
    latest_completed_case_id: int | None
    items: tuple[ProjectCalculationHistoryItemResponse, ...]
