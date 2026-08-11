from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.repositories.rbac import rbac_repository
from app.services.permission_catalog import PERMISSION_CATALOG


class PermissionSeedService:
    """Idempotently synchronize canonical permissions into the database."""

    def sync(
        self,
        db: Session,
    ) -> tuple[Permission, ...]:
        synced_permissions: list[Permission] = []

        for definition in PERMISSION_CATALOG:
            permission = rbac_repository.get_permission_by_code(
                db,
                definition.permission_code,
            )

            if permission is None:
                permission = Permission(
                    permission_code=definition.permission_code,
                    permission_name=definition.permission_name,
                    resource=definition.resource,
                    action=definition.action,
                    description=definition.description,
                    active=True,
                )

                db.add(permission)
                db.flush()

            else:
                permission.permission_name = definition.permission_name
                permission.resource = definition.resource
                permission.action = definition.action
                permission.description = definition.description
                permission.active = True

                db.add(permission)

            synced_permissions.append(permission)

        db.commit()

        for permission in synced_permissions:
            db.refresh(permission)

        return tuple(synced_permissions)


permission_seed_service = PermissionSeedService()
