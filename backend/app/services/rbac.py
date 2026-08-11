from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.repositories.rbac import rbac_repository
from app.repositories.user import user_repository
from app.schemas.rbac import RoleCreate, RoleUpdate
from app.services.organization import (
    OrganizationNotFoundError,
    organization_service,
)


class RoleNotFoundError(LookupError):
    """Raised when an RBAC role does not exist."""


class PermissionNotFoundError(LookupError):
    """Raised when an RBAC permission does not exist."""


class RoleConflictError(ValueError):
    """Raised when a tenant role code already exists."""


class RolePermissionConflictError(ValueError):
    """Raised when a permission is already assigned to a role."""


class UserRoleConflictError(ValueError):
    """Raised when a role is already assigned to a user."""


class CrossTenantRoleAssignmentError(PermissionError):
    """Raised when a role belongs to a different tenant."""


class RbacService:
    """Business rules for tenant-scoped RBAC."""

    def create_role(
        self,
        db: Session,
        role_in: RoleCreate,
    ) -> Role:
        try:
            organization_service.get(
                db,
                role_in.organization_id,
            )
        except OrganizationNotFoundError:
            raise

        normalized_code = role_in.role_code.strip().upper()
        normalized_name = role_in.role_name.strip()

        existing = rbac_repository.get_role_by_code(
            db,
            organization_id=role_in.organization_id,
            role_code=normalized_code,
        )

        if existing is not None:
            raise RoleConflictError("Role code already exists for this organization.")

        normalized_input = role_in.model_copy(
            update={
                "role_code": normalized_code,
                "role_name": normalized_name,
            },
        )

        return rbac_repository.create_role(
            db,
            normalized_input,
        )

    def get_role(
        self,
        db: Session,
        role_id: int,
    ) -> Role:
        role = rbac_repository.get_role_by_id(
            db,
            role_id,
        )

        if role is None:
            raise RoleNotFoundError("Role not found.")

        return role

    def list_roles(
        self,
        db: Session,
        *,
        organization_id: int,
        active_only: bool = False,
    ) -> tuple[Role, ...]:
        organization_service.get(
            db,
            organization_id,
        )

        return rbac_repository.list_roles(
            db,
            organization_id=organization_id,
            active_only=active_only,
        )

    def update_role(
        self,
        db: Session,
        *,
        role_id: int,
        role_in: RoleUpdate,
    ) -> Role:
        role = self.get_role(
            db,
            role_id,
        )

        values = role_in.model_dump(
            exclude_unset=True,
        )

        if "role_name" in values and values["role_name"] is not None:
            values["role_name"] = values["role_name"].strip()

        normalized_input = RoleUpdate(
            **values,
        )

        return rbac_repository.update_role(
            db,
            role,
            normalized_input,
        )

    def list_permissions(
        self,
        db: Session,
        *,
        active_only: bool = False,
    ) -> tuple[Permission, ...]:
        return rbac_repository.list_permissions(
            db,
            active_only=active_only,
        )

    def get_permission(
        self,
        db: Session,
        permission_id: int,
    ) -> Permission:
        permission = rbac_repository.get_permission_by_id(
            db,
            permission_id,
        )

        if permission is None:
            raise PermissionNotFoundError("Permission not found.")

        return permission

    def assign_permission_to_role(
        self,
        db: Session,
        *,
        role_id: int,
        permission_id: int,
    ):
        role = self.get_role(
            db,
            role_id,
        )

        permission = self.get_permission(
            db,
            permission_id,
        )

        existing = rbac_repository.get_role_permission(
            db,
            role_id=role.id,
            permission_id=permission.id,
        )

        if existing is not None:
            raise RolePermissionConflictError("Permission is already assigned to this role.")

        return rbac_repository.assign_permission_to_role(
            db,
            role_id=role.id,
            permission_id=permission.id,
        )

    def assign_role_to_user(
        self,
        db: Session,
        *,
        user_id: int,
        role_id: int,
    ):
        user = user_repository.get_by_id(
            db,
            user_id,
        )

        if user is None:
            raise LookupError("User not found.")

        role = self.get_role(
            db,
            role_id,
        )

        self._validate_same_tenant(
            user=user,
            role=role,
        )

        existing = rbac_repository.get_user_role(
            db,
            user_id=user.id,
            role_id=role.id,
        )

        if existing is not None:
            raise UserRoleConflictError("Role is already assigned to this user.")

        return rbac_repository.assign_role_to_user(
            db,
            user_id=user.id,
            role_id=role.id,
        )

    def get_effective_permissions(
        self,
        db: Session,
        *,
        user_id: int,
    ) -> frozenset[str]:
        user = user_repository.get_by_id(
            db,
            user_id,
        )

        if user is None:
            raise LookupError("User not found.")

        user_roles = rbac_repository.list_user_roles(
            db,
            user_id=user.id,
        )

        permission_codes: set[str] = set()

        for user_role in user_roles:
            role = self.get_role(
                db,
                user_role.role_id,
            )

            if not role.active:
                continue

            permission_codes.update(
                self._permission_codes_for_role(
                    db,
                    role_id=role.id,
                )
            )

        return frozenset(permission_codes)

    def _permission_codes_for_role(
        self,
        db: Session,
        *,
        role_id: int,
    ) -> set[str]:
        from app.models.role_permission import RolePermission

        mappings = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
            )
            .all()
        )

        codes: set[str] = set()

        for mapping in mappings:
            permission = rbac_repository.get_permission_by_id(
                db,
                mapping.permission_id,
            )

            if permission is not None and permission.active:
                codes.add(permission.permission_code)

        return codes

    @staticmethod
    def _validate_same_tenant(
        *,
        user: User,
        role: Role,
    ) -> None:
        if user.organization_id != role.organization_id:
            raise CrossTenantRoleAssignmentError("User and role belong to different organizations.")


rbac_service = RbacService()
