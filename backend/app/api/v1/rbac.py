from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.rbac import (
    PermissionResponse,
    RoleCreate,
    RolePermissionAssignment,
    RolePermissionResponse,
    RoleResponse,
    RoleUpdate,
    UserRoleAssignment,
    UserRoleResponse,
)
from app.services.organization import OrganizationNotFoundError
from app.services.rbac import (
    CrossTenantRoleAssignmentError,
    PermissionNotFoundError,
    RoleConflictError,
    RoleNotFoundError,
    RolePermissionConflictError,
    UserRoleConflictError,
    rbac_service,
)
from app.services.user import UserNotFoundError, user_service

router = APIRouter(
    prefix="/rbac",
    tags=["SaaS - RBAC"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]

RoleReader = Annotated[
    CurrentUser,
    Depends(require_permission("role.read")),
]

RoleManager = Annotated[
    CurrentUser,
    Depends(require_permission("role.manage")),
]


def _require_current_organization(
    *,
    requested_organization_id: int,
    current_organization_id: int,
) -> None:
    if requested_organization_id != current_organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )


def _get_current_tenant_role(
    db: Session,
    *,
    role_id: int,
    organization_id: int,
) -> Role:
    try:
        role = rbac_service.get_role(
            db,
            role_id,
        )
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if role.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


def _get_current_tenant_user(
    db: Session,
    *,
    user_id: int,
    organization_id: int,
) -> User:
    try:
        user = user_service.get(
            db,
            user_id,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    request: RoleCreate,
    db: DbSession,
    current_user: RoleManager,
) -> RoleResponse:
    _require_current_organization(
        requested_organization_id=request.organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return rbac_service.create_role(
            db,
            request,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RoleConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/roles/organization/{organization_id}",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
)
def list_roles(
    organization_id: int,
    db: DbSession,
    current_user: RoleReader,
    active_only: bool = Query(default=False),
) -> list[RoleResponse]:
    _require_current_organization(
        requested_organization_id=organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return list(
            rbac_service.list_roles(
                db,
                organization_id=current_user.organization_id,
                active_only=active_only,
            )
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def get_role(
    role_id: int,
    db: DbSession,
    current_user: RoleReader,
) -> RoleResponse:
    return _get_current_tenant_role(
        db,
        role_id=role_id,
        organization_id=current_user.organization_id,
    )


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def update_role(
    role_id: int,
    request: RoleUpdate,
    db: DbSession,
    current_user: RoleManager,
) -> RoleResponse:
    role = _get_current_tenant_role(
        db,
        role_id=role_id,
        organization_id=current_user.organization_id,
    )

    try:
        return rbac_service.update_role(
            db,
            role_id=role.id,
            role_in=request,
        )
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    status_code=status.HTTP_200_OK,
)
def list_permissions(
    db: DbSession,
    current_user: RoleReader,
    active_only: bool = Query(default=False),
) -> list[PermissionResponse]:
    del current_user

    return list(
        rbac_service.list_permissions(
            db,
            active_only=active_only,
        )
    )


@router.post(
    "/role-permissions",
    response_model=RolePermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_permission_to_role(
    request: RolePermissionAssignment,
    db: DbSession,
    current_user: RoleManager,
) -> RolePermissionResponse:
    role = _get_current_tenant_role(
        db,
        role_id=request.role_id,
        organization_id=current_user.organization_id,
    )

    try:
        return rbac_service.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=request.permission_id,
        )
    except (
        RoleNotFoundError,
        PermissionNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RolePermissionConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/user-roles",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_role_to_user(
    request: UserRoleAssignment,
    db: DbSession,
    current_user: RoleManager,
) -> UserRoleResponse:
    user = _get_current_tenant_user(
        db,
        user_id=request.user_id,
        organization_id=current_user.organization_id,
    )

    role = _get_current_tenant_role(
        db,
        role_id=request.role_id,
        organization_id=current_user.organization_id,
    )

    try:
        return rbac_service.assign_role_to_user(
            db,
            user_id=user.id,
            role_id=role.id,
        )
    except (
        RoleNotFoundError,
        LookupError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CrossTenantRoleAssignmentError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or user not found.",
        ) from exc
    except UserRoleConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/{user_id}/permissions",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
)
def get_effective_permissions(
    user_id: int,
    db: DbSession,
    current_user: RoleReader,
) -> list[str]:
    user = _get_current_tenant_user(
        db,
        user_id=user_id,
        organization_id=current_user.organization_id,
    )

    try:
        permissions = rbac_service.get_effective_permissions(
            db,
            user_id=user.id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return sorted(permissions)
