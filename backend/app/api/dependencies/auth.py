from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.token_security import (
    InvalidAccessTokenError,
    decode_access_token,
)
from app.models.user import User
from app.repositories.user import user_repository

bearer_scheme = HTTPBearer(
    auto_error=False,
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: DbSession,
) -> User:
    """Resolve and validate the current authenticated user."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        claims = decode_access_token(
            credentials.credentials,
        )
    except InvalidAccessTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    user = user_repository.get_by_id(
        db,
        claims.subject,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    if user.organization_id != claims.organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token tenant context is invalid.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if user.email.lower() != str(claims.email).lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token user context is invalid.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
