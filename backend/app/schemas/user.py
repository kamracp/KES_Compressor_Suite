from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    organization_id: int = Field(gt=0)

    email: EmailStr

    full_name: str = Field(
        min_length=2,
        max_length=200,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    active: bool = True
    verified: bool = False


class UserUpdate(BaseModel):
    email: EmailStr | None = None

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    active: bool | None = None
    verified: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    organization_id: int

    email: EmailStr
    full_name: str

    active: bool
    verified: bool

    created_at: datetime
    updated_at: datetime
