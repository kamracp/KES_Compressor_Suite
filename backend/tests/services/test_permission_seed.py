from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.permission import Permission
from app.services.permission_catalog import PERMISSION_CATALOG
from app.services.permission_seed import permission_seed_service


def cleanup_permissions() -> None:
    with SessionLocal() as db:
        db.execute(delete(Permission))
        db.commit()


def test_permission_seed_inserts_catalog() -> None:
    cleanup_permissions()

    with SessionLocal() as db:
        permissions = permission_seed_service.sync(db)

        assert len(permissions) == len(PERMISSION_CATALOG)

        stored = db.query(Permission).all()

        assert len(stored) == len(PERMISSION_CATALOG)


def test_permission_seed_is_idempotent() -> None:
    cleanup_permissions()

    with SessionLocal() as db:
        first = permission_seed_service.sync(db)
        second = permission_seed_service.sync(db)

        assert len(first) == len(PERMISSION_CATALOG)
        assert len(second) == len(PERMISSION_CATALOG)

        stored = db.query(Permission).all()

        assert len(stored) == len(PERMISSION_CATALOG)


def test_permission_seed_updates_existing_definition() -> None:
    cleanup_permissions()

    with SessionLocal() as db:
        permission = Permission(
            permission_code="project.read",
            permission_name="Old Name",
            resource="old-resource",
            action="old-action",
            description="Old description",
            active=False,
        )

        db.add(permission)
        db.commit()

        permission_seed_service.sync(db)

        updated = (
            db.query(Permission)
            .filter(
                Permission.permission_code == "project.read",
            )
            .one()
        )

        definition = next(
            item for item in PERMISSION_CATALOG if item.permission_code == "project.read"
        )

        assert updated.permission_name == definition.permission_name
        assert updated.resource == definition.resource
        assert updated.action == definition.action
        assert updated.description == definition.description
        assert updated.active is True
