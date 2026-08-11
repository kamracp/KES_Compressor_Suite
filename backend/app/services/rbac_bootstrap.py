from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.role_permission import RolePermission
from app.repositories.rbac import rbac_repository
from app.schemas.rbac import RoleCreate
from app.services.organization import organization_service
from app.services.permission_seed import permission_seed_service
from app.services.system_role_catalog import SYSTEM_ROLE_CATALOG


class RbacBootstrapService:
    """Bootstrap canonical RBAC roles and permissions for a tenant."""

    def bootstrap_organization(
        self,
        db: Session,
        *,
        organization_id: int,
    ) -> tuple[Role, ...]:
        organization_service.get(
            db,
            organization_id,
        )

        permission_seed_service.sync(db)

        roles: list[Role] = []

        for definition in SYSTEM_ROLE_CATALOG:
            role = rbac_repository.get_role_by_code(
                db,
                organization_id=organization_id,
                role_code=definition.role_code,
            )

            if role is None:
                role = rbac_repository.create_role(
                    db,
                    RoleCreate(
                        organization_id=organization_id,
                        role_code=definition.role_code,
                        role_name=definition.role_name,
                        description=definition.description,
                        system_role=True,
                        active=True,
                    ),
                )
            else:
                role.role_name = definition.role_name
                role.description = definition.description
                role.system_role = True
                role.active = True

                db.add(role)
                db.commit()
                db.refresh(role)

            self._sync_role_permissions(
                db,
                role=role,
                permission_codes=definition.permission_codes,
            )

            roles.append(role)

        return tuple(roles)

    @staticmethod
    def _sync_role_permissions(
        db: Session,
        *,
        role: Role,
        permission_codes: tuple[str, ...],
    ) -> None:
        for permission_code in permission_codes:
            permission = rbac_repository.get_permission_by_code(
                db,
                permission_code,
            )

            if permission is None:
                raise RuntimeError(f"Canonical permission '{permission_code}' is missing.")

            existing = rbac_repository.get_role_permission(
                db,
                role_id=role.id,
                permission_id=permission.id,
            )

            if existing is not None:
                continue

            db.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission.id,
                )
            )

        db.commit()


rbac_bootstrap_service = RbacBootstrapService()
