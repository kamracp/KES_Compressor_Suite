from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.calculation_case import CalculationStatus, CalculationType
from app.schemas._bounds import MAX_CASE_REVISION, MAX_DB_INTEGER_ID


class CalculationCaseBase(BaseModel):
    """Shared fields for compressor engineering calculation cases."""

    project_id: int = Field(gt=0, le=MAX_DB_INTEGER_ID)
    calculation_code: str = Field(min_length=1, max_length=50)
    calculation_type: CalculationType
    status: CalculationStatus = CalculationStatus.DRAFT
    revision: int = Field(default=1, ge=1, le=MAX_CASE_REVISION)

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    input_data: dict[str, Any]
    result_data: dict[str, Any] | None = None

    engineering_notes: str | None = Field(default=None, max_length=2000)


class CalculationCaseCreate(CalculationCaseBase):
    """Payload for creating a compressor engineering calculation case."""


class CalculationCaseUpdate(BaseModel):
    """Payload for partially updating a calculation case."""

    calculation_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    calculation_type: CalculationType | None = None
    status: CalculationStatus | None = None
    revision: int | None = Field(default=None, ge=1, le=MAX_CASE_REVISION)

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(default=None, max_length=1000)

    input_data: dict[str, Any] | None = None
    result_data: dict[str, Any] | None = None

    engineering_notes: str | None = Field(default=None, max_length=2000)


class CalculationCaseRead(CalculationCaseBase):
    """API representation of a stored engineering calculation case."""

    id: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
