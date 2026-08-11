from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    organization_code: str = Field(
        min_length=2,
        max_length=50,
    )

    organization_name: str = Field(
        min_length=2,
        max_length=200,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    country_code: str = Field(
        default="IN",
        min_length=2,
        max_length=2,
    )

    timezone: str = Field(
        default="Asia/Kolkata",
        min_length=1,
        max_length=100,
    )

    default_currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    active: bool = True

    notes: str | None = None


class OrganizationUpdate(BaseModel):
    organization_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    country_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    default_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    active: bool | None = None

    notes: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    organization_code: str
    organization_name: str

    legal_name: str | None

    country_code: str
    timezone: str
    default_currency: str

    active: bool

    notes: str | None

    created_at: datetime
    updated_at: datetime
