from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CalculationExportPayloadResponse(BaseModel):
    """API response schema for compressor engineering report export."""

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
