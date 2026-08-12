from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
from app.services.organization import organization_service


def ensure_test_organization_id(
    db: Session,
) -> int:
    """Return an existing test tenant or create one."""

    organization = db.query(Organization).order_by(Organization.id).first()

    if organization is not None:
        return organization.id

    organization = organization_service.create(
        db,
        OrganizationCreate(
            organization_code=f"TEST-{uuid4().hex[:8]}",
            organization_name="Legacy Regression Test Organization",
        ),
    )

    return organization.id
