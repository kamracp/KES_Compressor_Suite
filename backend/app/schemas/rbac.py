from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    organization_id: int = Field(gt=0)

    role_code: str = Field(
        min_length=2,
        max_length=50,
    )

    role_name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    system_role: bool = False
    active: bool = True


class RoleUpdate(BaseModel):
    role_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    active: bool | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    organization_id: int

    role_code: str
    role_name: str

    description: str | None

    system_role: bool
    active: bool

    created_at: datetime
    updated_at: datetime


class PermissionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    permission_code: str
    permission_name: str

    description: str | None

    resource: str
    action: str

    active: bool

    created_at: datetime
    updated_at: datetime


class RolePermissionAssignment(BaseModel):
    role_id: int = Field(gt=0)
    permission_id: int = Field(gt=0)


class UserRoleAssignment(BaseModel):
    user_id: int = Field(gt=0)
    role_id: int = Field(gt=0)


class UserRoleResponse(BaseModel):
    user_id: int
    role_id: int
    assigned_at: datetime


class RolePermissionResponse(BaseModel):
    role_id: int
    permission_id: int
    granted_at: datetime
