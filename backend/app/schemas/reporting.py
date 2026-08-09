from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CalculationReportResponse(BaseModel):
    """API response schema for a compressor calculation report."""

    model_config = ConfigDict(from_attributes=True)

    calculation_case_id: int
    project_id: int

    calculation_code: str
    calculation_type: str
    status: str
    revision: int

    title: str
    description: str | None

    input_data: dict[str, Any]
    result_data: dict[str, Any] | None

    engineering_notes: str | None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class CalculationAuditSummaryResponse(BaseModel):
    """API response schema for calculation audit information."""

    model_config = ConfigDict(from_attributes=True)

    calculation_case_id: int
    project_id: int

    calculation_code: str
    calculation_type: str
    status: str
    revision: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    is_completed: bool
    has_result_data: bool
    has_engineering_notes: bool
