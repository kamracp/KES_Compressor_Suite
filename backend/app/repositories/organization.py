from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)


class OrganizationRepository:
    """Persistence operations for SaaS tenant organizations."""

    def create(
        self,
        db: Session,
        organization_in: OrganizationCreate,
    ) -> Organization:
        organization = Organization(
            **organization_in.model_dump(),
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        return organization

    def get_by_id(
        self,
        db: Session,
        organization_id: int,
    ) -> Organization | None:
        return db.get(
            Organization,
            organization_id,
        )

    def get_by_code(
        self,
        db: Session,
        organization_code: str,
    ) -> Organization | None:
        statement = select(Organization).where(
            Organization.organization_code == organization_code.strip()
        )

        return db.execute(statement).scalar_one_or_none()

    def list(
        self,
        db: Session,
        *,
        active_only: bool = False,
    ) -> tuple[Organization, ...]:
        statement = select(Organization)

        if active_only:
            statement = statement.where(Organization.active.is_(True))

        statement = statement.order_by(
            Organization.organization_name,
            Organization.id,
        )

        return tuple(db.execute(statement).scalars().all())

    def update(
        self,
        db: Session,
        organization: Organization,
        organization_in: OrganizationUpdate,
    ) -> Organization:
        values = organization_in.model_dump(
            exclude_unset=True,
        )

        for field_name, value in values.items():
            setattr(
                organization,
                field_name,
                value,
            )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        return organization


organization_repository = OrganizationRepository()
