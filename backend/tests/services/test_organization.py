from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)
from app.services.organization import (
    OrganizationCodeConflictError,
    OrganizationNotFoundError,
    organization_service,
)


def cleanup_organizations() -> None:
    with SessionLocal() as db:
        db.execute(delete(Organization))
        db.commit()


def build_input(
    *,
    organization_code: str | None = None,
    active: bool = True,
) -> OrganizationCreate:
    code = organization_code or f"ORG-{uuid4().hex[:8]}"

    return OrganizationCreate(
        organization_code=code,
        organization_name="  Engineering Test Organization  ",
        legal_name="  Engineering Test Legal Entity  ",
        country_code="in",
        timezone="Asia/Kolkata",
        default_currency="inr",
        active=active,
        notes="Organization service test.",
    )


def test_create_normalizes_organization_fields() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        organization = organization_service.create(
            db,
            build_input(
                organization_code="  org-service-01  ",
            ),
        )

        assert organization.organization_code == "ORG-SERVICE-01"
        assert organization.organization_name == ("Engineering Test Organization")
        assert organization.legal_name == ("Engineering Test Legal Entity")
        assert organization.country_code == "IN"
        assert organization.default_currency == "INR"


def test_duplicate_code_is_rejected_case_insensitively() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        organization_service.create(
            db,
            build_input(
                organization_code="ORG-DUPLICATE",
            ),
        )

        with pytest.raises(
            OrganizationCodeConflictError,
            match="already exists",
        ):
            organization_service.create(
                db,
                build_input(
                    organization_code="org-duplicate",
                ),
            )


def test_get_returns_organization() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        created = organization_service.create(
            db,
            build_input(),
        )

        organization = organization_service.get(
            db,
            created.id,
        )

        assert organization.id == created.id


def test_get_unknown_organization_raises_not_found() -> None:
    cleanup_organizations()

    with (
        SessionLocal() as db,
        pytest.raises(
            OrganizationNotFoundError,
            match="Organization not found",
        ),
    ):
        organization_service.get(
            db,
            999999999,
        )


def test_get_by_code_normalizes_lookup() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        created = organization_service.create(
            db,
            build_input(
                organization_code="ORG-LOOKUP",
            ),
        )

        organization = organization_service.get_by_code(
            db,
            "  org-lookup  ",
        )

        assert organization.id == created.id


def test_get_by_unknown_code_raises_not_found() -> None:
    cleanup_organizations()

    with (
        SessionLocal() as db,
        pytest.raises(
            OrganizationNotFoundError,
            match="Organization not found",
        ),
    ):
        organization_service.get_by_code(
            db,
            "UNKNOWN-ORG",
        )


def test_list_active_only_filters_inactive_organizations() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        organization_service.create(
            db,
            build_input(
                active=True,
            ),
        )

        organization_service.create(
            db,
            build_input(
                active=False,
            ),
        )

        organizations = organization_service.list(
            db,
            active_only=True,
        )

        assert len(organizations) == 1
        assert organizations[0].active is True


def test_update_normalizes_fields() -> None:
    cleanup_organizations()

    with SessionLocal() as db:
        created = organization_service.create(
            db,
            build_input(),
        )

        updated = organization_service.update(
            db,
            organization_id=created.id,
            organization_in=OrganizationUpdate(
                organization_name="  Updated Organization  ",
                legal_name="  Updated Legal Entity  ",
                country_code="us",
                timezone="America/New_York",
                default_currency="usd",
                active=False,
            ),
        )

        assert updated.organization_name == "Updated Organization"
        assert updated.legal_name == "Updated Legal Entity"
        assert updated.country_code == "US"
        assert updated.default_currency == "USD"
        assert updated.timezone == "America/New_York"
        assert updated.active is False


def test_update_unknown_organization_raises_not_found() -> None:
    cleanup_organizations()

    with (
        SessionLocal() as db,
        pytest.raises(
            OrganizationNotFoundError,
            match="Organization not found",
        ),
    ):
        organization_service.update(
            db,
            organization_id=999999999,
            organization_in=OrganizationUpdate(
                organization_name="Updated Organization",
            ),
        )
