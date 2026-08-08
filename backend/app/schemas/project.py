from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Shared compressor project fields."""

    project_code: str = Field(min_length=1, max_length=50)
    project_name: str = Field(min_length=1, max_length=200)

    client_name: str | None = Field(default=None, max_length=200)
    plant_name: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    service_description: str | None = None

    status: str = Field(default="DRAFT", min_length=1, max_length=30)


class ProjectCreate(ProjectBase):
    """Payload for creating a compressor engineering project."""


class ProjectUpdate(BaseModel):
    """Payload for partially updating a compressor engineering project."""

    project_code: str | None = Field(default=None, min_length=1, max_length=50)
    project_name: str | None = Field(default=None, min_length=1, max_length=200)

    client_name: str | None = Field(default=None, max_length=200)
    plant_name: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    service_description: str | None = None

    status: str | None = Field(default=None, min_length=1, max_length=30)


class ProjectRead(ProjectBase):
    """API representation of a stored compressor engineering project."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
