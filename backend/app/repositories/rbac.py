from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.schemas.rbac import RoleCreate, RoleUpdate


class RbacRepository:
    """Persistence operations for roles, permissions, and assignments."""

    def create_role(
        self,
        db: Session,
        role_in: RoleCreate,
    ) -> Role:
        role = Role(
            **role_in.model_dump(),
        )

        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    def get_role_by_id(
        self,
        db: Session,
        role_id: int,
    ) -> Role | None:
        return db.get(
            Role,
            role_id,
        )

    def get_role_by_code(
        self,
        db: Session,
        *,
        organization_id: int,
        role_code: str,
    ) -> Role | None:
        statement = select(Role).where(
            Role.organization_id == organization_id,
            Role.role_code == role_code,
        )

        return db.execute(statement).scalar_one_or_none()

    def list_roles(
        self,
        db: Session,
        *,
        organization_id: int,
        active_only: bool = False,
    ) -> tuple[Role, ...]:
        statement = select(Role).where(
            Role.organization_id == organization_id,
        )

        if active_only:
            statement = statement.where(
                Role.active.is_(True),
            )

        statement = statement.order_by(
            Role.role_name,
            Role.id,
        )

        return tuple(db.execute(statement).scalars().all())

    def update_role(
        self,
        db: Session,
        role: Role,
        role_in: RoleUpdate,
    ) -> Role:
        values = role_in.model_dump(
            exclude_unset=True,
        )

        for field_name, value in values.items():
            setattr(
                role,
                field_name,
                value,
            )

        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    def get_permission_by_id(
        self,
        db: Session,
        permission_id: int,
    ) -> Permission | None:
        return db.get(
            Permission,
            permission_id,
        )

    def get_permission_by_code(
        self,
        db: Session,
        permission_code: str,
    ) -> Permission | None:
        statement = select(Permission).where(
            Permission.permission_code == permission_code,
        )

        return db.execute(statement).scalar_one_or_none()

    def list_permissions(
        self,
        db: Session,
        *,
        active_only: bool = False,
    ) -> tuple[Permission, ...]:
        statement = select(Permission)

        if active_only:
            statement = statement.where(
                Permission.active.is_(True),
            )

        statement = statement.order_by(
            Permission.resource,
            Permission.action,
            Permission.id,
        )

        return tuple(db.execute(statement).scalars().all())

    def assign_permission_to_role(
        self,
        db: Session,
        *,
        role_id: int,
        permission_id: int,
    ) -> RolePermission:
        mapping = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )

        db.add(mapping)
        db.commit()
        db.refresh(mapping)

        return mapping

    def get_role_permission(
        self,
        db: Session,
        *,
        role_id: int,
        permission_id: int,
    ) -> RolePermission | None:
        return db.get(
            RolePermission,
            {
                "role_id": role_id,
                "permission_id": permission_id,
            },
        )

    def assign_role_to_user(
        self,
        db: Session,
        *,
        user_id: int,
        role_id: int,
    ) -> UserRole:
        mapping = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        db.add(mapping)
        db.commit()
        db.refresh(mapping)

        return mapping

    def get_user_role(
        self,
        db: Session,
        *,
        user_id: int,
        role_id: int,
    ) -> UserRole | None:
        return db.get(
            UserRole,
            {
                "user_id": user_id,
                "role_id": role_id,
            },
        )

    def list_user_roles(
        self,
        db: Session,
        *,
        user_id: int,
    ) -> tuple[UserRole, ...]:
        statement = (
            select(UserRole)
            .where(
                UserRole.user_id == user_id,
            )
            .order_by(
                UserRole.role_id,
            )
        )

        return tuple(db.execute(statement).scalars().all())


rbac_repository = RbacRepository()
