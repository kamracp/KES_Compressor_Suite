from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings
from app.schemas.auth import TokenClaims


class InvalidAccessTokenError(ValueError):
    """Raised when an access token is invalid or cannot be verified."""


def create_access_token(
    *,
    user_id: int,
    organization_id: int,
    email: str,
) -> tuple[str, datetime]:
    """Create a signed JWT access token."""

    settings = get_settings()

    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(
        minutes=settings.jwt_access_token_expire_minutes,
    )

    payload = {
        "sub": str(user_id),
        "organization_id": organization_id,
        "email": email,
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_at


def decode_access_token(
    token: str,
) -> TokenClaims:
    """Decode and validate a signed JWT access token."""

    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )

        user_id = int(payload["sub"])
        organization_id = int(payload["organization_id"])
        email = str(payload["email"])
        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=UTC,
        )

    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise InvalidAccessTokenError("Access token is invalid.") from exc

    return TokenClaims(
        subject=user_id,
        organization_id=organization_id,
        email=email,
        expires_at=expires_at,
    )
