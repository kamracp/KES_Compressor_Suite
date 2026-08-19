from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import (
    UserEmailConflictError,
    UserNotFoundError,
    UserOrganizationNotFoundError,
    user_service,
)

router = APIRouter(
    prefix="/users",
    tags=["SaaS - Users"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]

UserReader = Annotated[
    CurrentUser,
    Depends(require_permission("user.read")),
]

UserManager = Annotated[
    CurrentUser,
    Depends(require_permission("user.manage")),
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
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreate,
    db: DbSession,
    current_user: UserManager,
) -> UserResponse:
    _require_current_organization(
        requested_organization_id=request.organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return user_service.create(
            db,
            request,
        )
    except UserOrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/organization/{organization_id}",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def list_organization_users(
    organization_id: int,
    db: DbSession,
    current_user: UserReader,
    active_only: bool = Query(default=False),
) -> list[UserResponse]:
    _require_current_organization(
        requested_organization_id=organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return list(
            user_service.list_by_organization(
                db,
                organization_id=current_user.organization_id,
                active_only=active_only,
            )
        )
    except UserOrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/organization/{organization_id}/email/{email}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_by_email(
    organization_id: int,
    email: str,
    db: DbSession,
    current_user: UserReader,
) -> UserResponse:
    _require_current_organization(
        requested_organization_id=organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return user_service.get_by_email(
            db,
            organization_id=current_user.organization_id,
            email=email,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: int,
    db: DbSession,
    current_user: UserReader,
) -> UserResponse:
    return _get_current_tenant_user(
        db,
        user_id=user_id,
        organization_id=current_user.organization_id,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_id: int,
    request: UserUpdate,
    db: DbSession,
    current_user: UserManager,
) -> UserResponse:
    user = _get_current_tenant_user(
        db,
        user_id=user_id,
        organization_id=current_user.organization_id,
    )

    try:
        return user_service.update(
            db,
            user_id=user.id,
            user_in=request,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
