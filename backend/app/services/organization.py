from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.organization import organization_repository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)


class OrganizationNotFoundError(LookupError):
    """Raised when a tenant organization cannot be found."""


class OrganizationCodeConflictError(ValueError):
    """Raised when an organization code already exists."""


class OrganizationService:
    """Business service for SaaS tenant organizations."""

    def create(
        self,
        db: Session,
        organization_in: OrganizationCreate,
    ) -> Organization:
        normalized_code = organization_in.organization_code.strip().upper()

        existing = organization_repository.get_by_code(
            db,
            normalized_code,
        )

        if existing is not None:
            raise OrganizationCodeConflictError(
                f"Organization code '{normalized_code}' already exists."
            )

        normalized_input = organization_in.model_copy(
            update={
                "organization_code": normalized_code,
                "organization_name": (organization_in.organization_name.strip()),
                "country_code": (organization_in.country_code.strip().upper()),
                "timezone": organization_in.timezone.strip(),
                "default_currency": (organization_in.default_currency.strip().upper()),
                "legal_name": (
                    organization_in.legal_name.strip()
                    if organization_in.legal_name is not None
                    else None
                ),
            }
        )

        return organization_repository.create(
            db,
            normalized_input,
        )

    def get(
        self,
        db: Session,
        organization_id: int,
    ) -> Organization:
        organization = organization_repository.get_by_id(
            db,
            organization_id,
        )

        if organization is None:
            raise OrganizationNotFoundError("Organization not found.")

        return organization

    def get_by_code(
        self,
        db: Session,
        organization_code: str,
    ) -> Organization:
        normalized_code = organization_code.strip().upper()

        organization = organization_repository.get_by_code(
            db,
            normalized_code,
        )

        if organization is None:
            raise OrganizationNotFoundError("Organization not found.")

        return organization

    def list(
        self,
        db: Session,
        *,
        active_only: bool = False,
    ) -> tuple[Organization, ...]:
        return organization_repository.list(
            db,
            active_only=active_only,
        )

    def update(
        self,
        db: Session,
        *,
        organization_id: int,
        organization_in: OrganizationUpdate,
    ) -> Organization:
        organization = self.get(
            db,
            organization_id,
        )

        updates = organization_in.model_dump(
            exclude_unset=True,
        )

        normalized_updates = self._normalize_updates(updates)

        normalized_input = OrganizationUpdate(**normalized_updates)

        return organization_repository.update(
            db,
            organization,
            normalized_input,
        )

    @staticmethod
    def _normalize_updates(
        updates: dict,
    ) -> dict:
        normalized = dict(updates)

        if "organization_name" in normalized:
            normalized["organization_name"] = normalized["organization_name"].strip()

        if "legal_name" in normalized and normalized["legal_name"] is not None:
            normalized["legal_name"] = normalized["legal_name"].strip()

        if "country_code" in normalized and normalized["country_code"] is not None:
            normalized["country_code"] = normalized["country_code"].strip().upper()

        if "timezone" in normalized and normalized["timezone"] is not None:
            normalized["timezone"] = normalized["timezone"].strip()

        if "default_currency" in normalized and normalized["default_currency"] is not None:
            normalized["default_currency"] = normalized["default_currency"].strip().upper()

        return normalized


organization_service = OrganizationService()
