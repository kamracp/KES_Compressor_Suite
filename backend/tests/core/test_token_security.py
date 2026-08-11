from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.token_security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
)


def test_create_and_decode_access_token() -> None:
    token, expires_at = create_access_token(
        user_id=101,
        organization_id=202,
        email="engineer@example.com",
    )

    claims = decode_access_token(token)

    assert claims.subject == 101
    assert claims.organization_id == 202
    assert claims.email == "engineer@example.com"
    assert claims.expires_at == expires_at.replace(
        microsecond=0,
    )


def test_malformed_token_is_rejected() -> None:
    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token("not-a-valid-jwt")


def test_tampered_token_is_rejected() -> None:
    token, _ = create_access_token(
        user_id=1,
        organization_id=1,
        email="engineer@example.com",
    )

    tampered = token + "tampered"

    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token(tampered)


def test_wrong_issuer_is_rejected() -> None:
    settings = get_settings()

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "1",
            "organization_id": 1,
            "email": "engineer@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "iss": "wrong-issuer",
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token(token)


def test_expired_token_is_rejected() -> None:
    settings = get_settings()

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "1",
            "organization_id": 1,
            "email": "engineer@example.com",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
            "iss": settings.jwt_issuer,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token(token)


def test_missing_subject_is_rejected() -> None:
    settings = get_settings()

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "organization_id": 1,
            "email": "engineer@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "iss": settings.jwt_issuer,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token(token)


def test_invalid_subject_type_is_rejected() -> None:
    settings = get_settings()

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "not-an-integer",
            "organization_id": 1,
            "email": "engineer@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "iss": settings.jwt_issuer,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        InvalidAccessTokenError,
        match="Access token is invalid",
    ):
        decode_access_token(token)
