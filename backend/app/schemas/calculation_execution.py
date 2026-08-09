from pydantic import BaseModel, Field


class CalculationExecutionMetadata(BaseModel):
    """Persistence metadata for a compressor engineering calculation."""

    persist_result: bool = False

    project_id: int | None = Field(default=None, gt=0)
    calculation_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    engineering_notes: str | None = Field(
        default=None,
        max_length=2000,
    )
