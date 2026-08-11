from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.core.token_security import decode_access_token
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
from app.services.auth import (
    AuthenticationFailedError,
    InactiveUserError,
    auth_service,
)
from app.services.organization import organization_service
from app.services.user import user_service


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(User))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> Organization:
    with SessionLocal() as db:
        return organization_service.create(
            db,
            OrganizationCreate(
                organization_code=f"ORG-{uuid4().hex[:8]}",
                organization_name="Authentication Service Organization",
            ),
        )


def create_user(
    *,
    organization_id: int,
    email: str = "auth-service@example.com",
    password: str = "Strong-Test-Password-123!",
    active: bool = True,
) -> User:
    with SessionLocal() as db:
        return user_service.create(
            db,
            UserCreate(
                organization_id=organization_id,
                email=email,
                full_name="Authentication Service User",
                password=password,
                active=active,
                verified=True,
            ),
        )


def test_authenticate_returns_user_and_access_token() -> None:
    cleanup_data()

    organization = create_organization()

    user = create_user(
        organization_id=organization.id,
    )

    with SessionLocal() as db:
        authenticated_user, token = auth_service.authenticate(
            db,
            LoginRequest(
                organization_id=organization.id,
                email="AUTH-SERVICE@example.com",
                password="Strong-Test-Password-123!",
            ),
        )

        assert authenticated_user.id == user.id
        assert token.access_token
        assert token.token_type == "bearer"

        claims = decode_access_token(
            token.access_token,
        )

        assert claims.subject == user.id
        assert claims.organization_id == organization.id
        assert claims.email == "auth-service@example.com"


def test_authenticate_rejects_wrong_password() -> None:
    cleanup_data()

    organization = create_organization()

    create_user(
        organization_id=organization.id,
    )

    with (
        SessionLocal() as db,
        pytest.raises(
            AuthenticationFailedError,
            match="Invalid organization, email, or password",
        ),
    ):
        auth_service.authenticate(
            db,
            LoginRequest(
                organization_id=organization.id,
                email="auth-service@example.com",
                password="Wrong-Password",
            ),
        )


def test_authenticate_rejects_unknown_user() -> None:
    cleanup_data()

    organization = create_organization()

    with (
        SessionLocal() as db,
        pytest.raises(
            AuthenticationFailedError,
            match="Invalid organization, email, or password",
        ),
    ):
        auth_service.authenticate(
            db,
            LoginRequest(
                organization_id=organization.id,
                email="unknown@example.com",
                password="Strong-Test-Password-123!",
            ),
        )


def test_authenticate_rejects_inactive_user() -> None:
    cleanup_data()

    organization = create_organization()

    create_user(
        organization_id=organization.id,
        active=False,
    )

    with (
        SessionLocal() as db,
        pytest.raises(
            InactiveUserError,
            match="User account is inactive",
        ),
    ):
        auth_service.authenticate(
            db,
            LoginRequest(
                organization_id=organization.id,
                email="auth-service@example.com",
                password="Strong-Test-Password-123!",
            ),
        )


def test_authenticate_is_tenant_scoped() -> None:
    cleanup_data()

    first_organization = create_organization()
    second_organization = create_organization()

    create_user(
        organization_id=first_organization.id,
        email="shared-auth@example.com",
    )

    with (
        SessionLocal() as db,
        pytest.raises(
            AuthenticationFailedError,
            match="Invalid organization, email, or password",
        ),
    ):
        auth_service.authenticate(
            db,
            LoginRequest(
                organization_id=second_organization.id,
                email="shared-auth@example.com",
                password="Strong-Test-Password-123!",
            ),
        )
