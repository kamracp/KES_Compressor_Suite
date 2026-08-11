from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.organization import OrganizationCreate
from app.schemas.rbac import RoleCreate
from app.schemas.user import UserCreate
from app.services.organization import organization_service
from app.services.rbac import (
    CrossTenantRoleAssignmentError,
    RoleConflictError,
    RolePermissionConflictError,
    UserRoleConflictError,
    rbac_service,
)
from app.services.user import user_service


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(UserRole))
        db.execute(delete(RolePermission))
        db.execute(delete(Permission))
        db.execute(delete(Role))
        db.execute(delete(User))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> Organization:
    with SessionLocal() as db:
        return organization_service.create(
            db,
            OrganizationCreate(
                organization_code=f"ORG-{uuid4().hex[:8]}",
                organization_name="RBAC Test Organization",
            ),
        )


def create_user(
    organization_id: int,
) -> User:
    with SessionLocal() as db:
        return user_service.create(
            db,
            UserCreate(
                organization_id=organization_id,
                email=f"user-{uuid4().hex[:8]}@example.com",
                full_name="RBAC Test User",
                password="Strong-Test-Password-123!",
            ),
        )


def create_permission(
    *,
    permission_code: str,
) -> Permission:
    with SessionLocal() as db:
        permission = Permission(
            permission_code=permission_code,
            permission_name=permission_code,
            resource="project",
            action="read",
            active=True,
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        return permission


def test_create_role_normalizes_code() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code=" engineer ",
                role_name=" Engineering Role ",
            ),
        )

        assert role.role_code == "ENGINEER"
        assert role.role_name == "Engineering Role"


def test_duplicate_role_code_is_rejected() -> None:
    cleanup_data()
    organization = create_organization()

    with SessionLocal() as db:
        rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="ENGINEER",
                role_name="Engineer",
            ),
        )

        with pytest.raises(
            RoleConflictError,
            match="Role code already exists",
        ):
            rbac_service.create_role(
                db,
                RoleCreate(
                    organization_id=organization.id,
                    role_code="engineer",
                    role_name="Engineer 2",
                ),
            )


def test_assign_permission_to_role() -> None:
    cleanup_data()
    organization = create_organization()
    permission = create_permission(
        permission_code="project.read",
    )

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="VIEWER",
                role_name="Viewer",
            ),
        )

        mapping = rbac_service.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=permission.id,
        )

        assert mapping.role_id == role.id
        assert mapping.permission_id == permission.id


def test_duplicate_role_permission_is_rejected() -> None:
    cleanup_data()
    organization = create_organization()
    permission = create_permission(
        permission_code="project.write",
    )

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="EDITOR",
                role_name="Editor",
            ),
        )

        rbac_service.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=permission.id,
        )

        with pytest.raises(
            RolePermissionConflictError,
            match="already assigned",
        ):
            rbac_service.assign_permission_to_role(
                db,
                role_id=role.id,
                permission_id=permission.id,
            )


def test_assign_role_to_user() -> None:
    cleanup_data()
    organization = create_organization()
    user = create_user(organization.id)

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="ENGINEER",
                role_name="Engineer",
            ),
        )

        mapping = rbac_service.assign_role_to_user(
            db,
            user_id=user.id,
            role_id=role.id,
        )

        assert mapping.user_id == user.id
        assert mapping.role_id == role.id


def test_cross_tenant_role_assignment_is_rejected() -> None:
    cleanup_data()

    first_organization = create_organization()
    second_organization = create_organization()

    user = create_user(first_organization.id)

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=second_organization.id,
                role_code="ADMIN",
                role_name="Admin",
            ),
        )

        with pytest.raises(
            CrossTenantRoleAssignmentError,
            match="different organizations",
        ):
            rbac_service.assign_role_to_user(
                db,
                user_id=user.id,
                role_id=role.id,
            )


def test_duplicate_user_role_is_rejected() -> None:
    cleanup_data()
    organization = create_organization()
    user = create_user(organization.id)

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="OWNER",
                role_name="Owner",
            ),
        )

        rbac_service.assign_role_to_user(
            db,
            user_id=user.id,
            role_id=role.id,
        )

        with pytest.raises(
            UserRoleConflictError,
            match="already assigned",
        ):
            rbac_service.assign_role_to_user(
                db,
                user_id=user.id,
                role_id=role.id,
            )


def test_effective_permissions_are_resolved() -> None:
    cleanup_data()
    organization = create_organization()
    user = create_user(organization.id)

    first_permission = create_permission(
        permission_code="project.read",
    )

    second_permission = create_permission(
        permission_code="report.export",
    )

    with SessionLocal() as db:
        role = rbac_service.create_role(
            db,
            RoleCreate(
                organization_id=organization.id,
                role_code="ENGINEER",
                role_name="Engineer",
            ),
        )

        rbac_service.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=first_permission.id,
        )

        rbac_service.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=second_permission.id,
        )

        rbac_service.assign_role_to_user(
            db,
            user_id=user.id,
            role_id=role.id,
        )

        permissions = rbac_service.get_effective_permissions(
            db,
            user_id=user.id,
        )

        assert permissions == frozenset(
            {
                "project.read",
                "report.export",
            }
        )
