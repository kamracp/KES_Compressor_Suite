from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.compressed_air_leak import (
    CompressedAirLeakLifecycleStatus,
)


class CompressedAirLeakCreateRequest(BaseModel):
    """Request to tag one project-scoped compressed-air leak."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    leak_code: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=255)
    source_snapshot: dict[str, Any] = Field(min_length=1)


class CompressedAirLeakAssignRequest(BaseModel):
    """Request to assign a tagged compressed-air leak."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    assigned_to: str = Field(min_length=1, max_length=255)
    change_notes: str | None = None


class CompressedAirLeakCloseRequest(BaseModel):
    """Request to close an assigned compressed-air leak."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    closure_evidence: dict[str, Any] = Field(min_length=1)
    closure_notes: str | None = None
    change_notes: str | None = None


class CompressedAirLeakKpiSnapshotCreateRequest(BaseModel):
    """Request to capture one leakage KPI snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    snapshot_code: str = Field(min_length=1, max_length=100)
    metrics_payload: dict[str, Any] = Field(min_length=1)


class CompressedAirLeakStatusHistoryResponse(BaseModel):
    """Response for one immutable lifecycle transition."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    leak_id: int
    previous_status: CompressedAirLeakLifecycleStatus | None
    new_status: CompressedAirLeakLifecycleStatus
    changed_by: str | None
    change_notes: str | None
    changed_at: datetime


class CompressedAirLeakKpiSnapshotResponse(BaseModel):
    """Response for one historical leakage KPI snapshot."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    leak_id: int
    snapshot_code: str
    lifecycle_status: CompressedAirLeakLifecycleStatus
    metrics_payload: dict[str, Any]
    captured_by: str | None
    captured_at: datetime


class CompressedAirLeakResponse(BaseModel):
    """Response for one persistent compressed-air leak."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    leak_code: str
    location: str
    lifecycle_status: CompressedAirLeakLifecycleStatus
    assigned_to: str | None
    source_snapshot: dict[str, Any]
    closure_evidence: dict[str, Any] | None
    closure_notes: str | None
    created_by: str | None
    updated_by: str | None
    tagged_at: datetime
    assigned_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CompressedAirLeakListResponse(BaseModel):
    """Response for a project-scoped leakage lifecycle register."""

    project_id: int
    total_leaks: int
    tagged_leaks: int
    assigned_leaks: int
    closed_leaks: int
    items: tuple[CompressedAirLeakResponse, ...]
