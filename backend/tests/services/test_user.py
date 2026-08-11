from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate, UserUpdate
from app.services.organization import organization_service
from app.services.user import (
    UserEmailConflictError,
    UserNotFoundError,
    UserOrganizationNotFoundError,
    user_service,
)


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
                organization_name="User Service Test Organization",
            ),
        )


def build_user_input(
    *,
    organization_id: int,
    email: str | None = None,
    active: bool = True,
) -> UserCreate:
    return UserCreate(
        organization_id=organization_id,
        email=email or f"user-{uuid4().hex[:8]}@example.com",
        full_name="  Engineering Test User  ",
        password="Strong-Test-Password-123!",
        active=active,
        verified=False,
    )


def test_create_user_normalizes_fields_and_hashes_password() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        user = user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                email="ENGINEER@example.com",
            ),
        )

        assert user.email == "engineer@example.com"
        assert user.full_name == "Engineering Test User"
        assert user.password_hash != "Strong-Test-Password-123!"

        assert verify_password(
            password="Strong-Test-Password-123!",
            hashed_password=user.password_hash,
        )


def test_create_user_requires_existing_organization() -> None:
    cleanup_data()

    with (
        SessionLocal() as db,
        pytest.raises(
            UserOrganizationNotFoundError,
            match="Organization not found",
        ),
    ):
        user_service.create(
            db,
            build_user_input(
                organization_id=999999999,
            ),
        )


def test_duplicate_email_is_rejected_within_organization() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                email="duplicate@example.com",
            ),
        )

        with pytest.raises(
            UserEmailConflictError,
            match="already exists",
        ):
            user_service.create(
                db,
                build_user_input(
                    organization_id=organization.id,
                    email="DUPLICATE@example.com",
                ),
            )


def test_same_email_is_allowed_across_organizations() -> None:
    cleanup_data()

    first_organization = create_organization()
    second_organization = create_organization()

    with SessionLocal() as db:
        first = user_service.create(
            db,
            build_user_input(
                organization_id=first_organization.id,
                email="shared@example.com",
            ),
        )

        second = user_service.create(
            db,
            build_user_input(
                organization_id=second_organization.id,
                email="shared@example.com",
            ),
        )

        assert first.organization_id != second.organization_id


def test_get_unknown_user_raises_not_found() -> None:
    cleanup_data()

    with (
        SessionLocal() as db,
        pytest.raises(
            UserNotFoundError,
            match="User not found",
        ),
    ):
        user_service.get(
            db,
            999999999,
        )


def test_get_by_email_normalizes_lookup() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        created = user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                email="lookup@example.com",
            ),
        )

        found = user_service.get_by_email(
            db,
            organization_id=organization.id,
            email="  LOOKUP@example.com  ",
        )

        assert found.id == created.id


def test_list_active_users_only() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                active=True,
            ),
        )

        user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                active=False,
            ),
        )

        users = user_service.list_by_organization(
            db,
            organization_id=organization.id,
            active_only=True,
        )

        assert len(users) == 1
        assert users[0].active is True


def test_update_user_normalizes_fields() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        created = user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
            ),
        )

        updated = user_service.update(
            db,
            user_id=created.id,
            user_in=UserUpdate(
                email="UPDATED@example.com",
                full_name="  Updated Engineering User  ",
                active=False,
                verified=True,
            ),
        )

        assert updated.email == "updated@example.com"
        assert updated.full_name == "Updated Engineering User"
        assert updated.active is False
        assert updated.verified is True


def test_update_to_existing_email_is_rejected() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        first = user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                email="first@example.com",
            ),
        )

        user_service.create(
            db,
            build_user_input(
                organization_id=organization.id,
                email="second@example.com",
            ),
        )

        with pytest.raises(
            UserEmailConflictError,
            match="already exists",
        ):
            user_service.update(
                db,
                user_id=first.id,
                user_in=UserUpdate(
                    email="second@example.com",
                ),
            )
