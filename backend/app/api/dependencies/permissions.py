from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.core.database import get_db
from app.models.user import User
from app.services.rbac import rbac_service

DbSession = Annotated[
    Session,
    Depends(get_db),
]


def require_permission(
    permission_code: str,
) -> Callable:
    """Build a dependency that requires one effective permission."""

    normalized_permission = permission_code.strip().lower()

    if not normalized_permission:
        raise ValueError("Permission code cannot be empty.")

    def dependency(
        current_user: CurrentUser,
        db: DbSession,
    ) -> User:
        permissions = rbac_service.get_effective_permissions(
            db,
            user_id=current_user.id,
        )

        normalized_permissions = {item.strip().lower() for item in permissions}

        if normalized_permission not in normalized_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(f"Permission '{normalized_permission}' is required."),
            )

        return current_user

    return dependency
