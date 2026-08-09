from datetime import datetime

from pydantic import BaseModel, Field

from app.models.compressed_air_assessment import (
    CompressedAirAssessmentStatus,
    CompressedAirAssessmentType,
)


class CompressedAirAssessmentCreateRequest(BaseModel):
    project_id: int = Field(gt=0)

    assessment_code: str = Field(
        min_length=1,
        max_length=100,
    )

    assessment_type: CompressedAirAssessmentType

    status: CompressedAirAssessmentStatus = CompressedAirAssessmentStatus.DRAFT

    title: str | None = Field(
        default=None,
        max_length=255,
    )

    engineering_basis: str | None = None

    input_payload: dict
    result_payload: dict

    standards_snapshot: dict | None = None

    calculation_version: str | None = Field(
        default=None,
        max_length=100,
    )

    created_by: str | None = Field(
        default=None,
        max_length=255,
    )


class CompressedAirAssessmentStatusUpdateRequest(BaseModel):
    status: CompressedAirAssessmentStatus


class CompressedAirAssessmentResponse(BaseModel):
    id: int

    project_id: int

    assessment_code: str
    assessment_type: str
    status: str

    title: str | None
    engineering_basis: str | None

    input_payload: dict
    result_payload: dict

    standards_snapshot: dict | None

    calculation_version: str | None

    created_by: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class CompressedAirAssessmentSummaryResponse(BaseModel):
    id: int

    project_id: int

    assessment_code: str
    assessment_type: str
    status: str

    title: str | None

    calculation_version: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class CompressedAirAssessmentListResponse(BaseModel):
    project_id: int

    total: int

    items: list[CompressedAirAssessmentSummaryResponse]
