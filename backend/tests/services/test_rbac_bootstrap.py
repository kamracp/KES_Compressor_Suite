from uuid import uuid4

from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.schemas.organization import OrganizationCreate
from app.services.organization import organization_service
from app.services.permission_catalog import PERMISSION_CATALOG
from app.services.rbac_bootstrap import rbac_bootstrap_service
from app.services.system_role_catalog import SYSTEM_ROLE_CATALOG


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(RolePermission))
        db.execute(delete(Role))
        db.execute(delete(Permission))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> Organization:
    with SessionLocal() as db:
        return organization_service.create(
            db,
            OrganizationCreate(
                organization_code=f"ORG-{uuid4().hex[:8]}",
                organization_name="RBAC Bootstrap Test Organization",
            ),
        )


def test_bootstrap_creates_all_system_roles() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        roles = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        assert len(roles) == len(SYSTEM_ROLE_CATALOG)

        role_codes = {role.role_code for role in roles}

        assert role_codes == {definition.role_code for definition in SYSTEM_ROLE_CATALOG}


def test_bootstrap_creates_permission_catalog() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        permissions = db.query(Permission).all()

        assert len(permissions) == len(PERMISSION_CATALOG)


def test_bootstrap_is_idempotent() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        first = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        second = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        assert len(first) == len(SYSTEM_ROLE_CATALOG)
        assert len(second) == len(SYSTEM_ROLE_CATALOG)

        roles = (
            db.query(Role)
            .filter(
                Role.organization_id == organization.id,
            )
            .all()
        )

        assert len(roles) == len(SYSTEM_ROLE_CATALOG)


def test_tenant_admin_receives_full_permission_catalog() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        roles = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        tenant_admin = next(role for role in roles if role.role_code == "TENANT_ADMIN")

        mappings = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == tenant_admin.id,
            )
            .all()
        )

        assert len(mappings) == len(PERMISSION_CATALOG)


def test_bootstrap_keeps_roles_active_and_system_managed() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        roles = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization.id,
        )

        assert all(role.active for role in roles)
        assert all(role.system_role for role in roles)
