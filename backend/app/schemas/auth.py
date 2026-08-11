from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    organization_id: int = Field(gt=0)
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenClaims(BaseModel):
    subject: int
    organization_id: int
    email: EmailStr
    expires_at: datetime


class CurrentUserResponse(BaseModel):
    user_id: int
    organization_id: int
    email: EmailStr
    full_name: str
    active: bool
    verified: bool
