from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.core.database import get_db
from app.schemas.auth import (
    AccessTokenResponse,
    CurrentUserResponse,
    LoginRequest,
)
from app.services.auth import (
    AuthenticationFailedError,
    InactiveUserError,
    auth_service,
)

router = APIRouter(
    prefix="/auth",
    tags=["SaaS - Authentication"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    db: DbSession,
) -> AccessTokenResponse:
    try:
        _, token = auth_service.authenticate(
            db,
            request,
        )
        return token

    except AuthenticationFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: CurrentUser,
) -> CurrentUserResponse:
    return CurrentUserResponse(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        email=current_user.email,
        full_name=current_user.full_name,
        active=current_user.active,
        verified=current_user.verified,
    )
