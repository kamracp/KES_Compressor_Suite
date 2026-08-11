from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
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

router = APIRouter(
    prefix="/rbac",
    tags=["SaaS - RBAC"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    request: RoleCreate,
    db: DbSession,
) -> RoleResponse:
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
    active_only: bool = Query(default=False),
) -> list[RoleResponse]:
    try:
        return list(
            rbac_service.list_roles(
                db,
                organization_id=organization_id,
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
) -> RoleResponse:
    try:
        return rbac_service.get_role(
            db,
            role_id,
        )
    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def update_role(
    role_id: int,
    request: RoleUpdate,
    db: DbSession,
) -> RoleResponse:
    try:
        return rbac_service.update_role(
            db,
            role_id=role_id,
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
    active_only: bool = Query(default=False),
) -> list[PermissionResponse]:
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
) -> RolePermissionResponse:
    try:
        return rbac_service.assign_permission_to_role(
            db,
            role_id=request.role_id,
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
) -> UserRoleResponse:
    try:
        return rbac_service.assign_role_to_user(
            db,
            user_id=request.user_id,
            role_id=request.role_id,
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
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
) -> list[str]:
    try:
        permissions = rbac_service.get_effective_permissions(
            db,
            user_id=user_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return sorted(permissions)
