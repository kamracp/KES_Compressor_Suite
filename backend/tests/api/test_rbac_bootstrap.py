from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.services.permission_catalog import PERMISSION_CATALOG
from app.services.system_role_catalog import SYSTEM_ROLE_CATALOG

client = TestClient(app)


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(UserRole))
        db.execute(delete(RolePermission))
        db.execute(delete(Role))
        db.execute(delete(Permission))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> dict:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": f"ORG-{uuid4().hex[:8]}",
            "organization_name": "RBAC Bootstrap API Organization",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_bootstrap_endpoint_creates_system_roles() -> None:
    cleanup_data()
    organization = create_organization()

    response = client.post(f"/api/v1/rbac/bootstrap/organization/{organization['id']}")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == len(SYSTEM_ROLE_CATALOG)

    role_codes = {item["role_code"] for item in data}

    assert role_codes == {role.role_code for role in SYSTEM_ROLE_CATALOG}


def test_bootstrap_endpoint_is_idempotent() -> None:
    cleanup_data()
    organization = create_organization()

    first = client.post(f"/api/v1/rbac/bootstrap/organization/{organization['id']}")

    second = client.post(f"/api/v1/rbac/bootstrap/organization/{organization['id']}")

    assert first.status_code == 200
    assert second.status_code == 200

    with SessionLocal() as db:
        roles = (
            db.query(Role)
            .filter(
                Role.organization_id == organization["id"],
            )
            .all()
        )

        permissions = db.query(Permission).all()

        assert len(roles) == len(SYSTEM_ROLE_CATALOG)
        assert len(permissions) == len(PERMISSION_CATALOG)


def test_bootstrap_unknown_organization_returns_404() -> None:
    cleanup_data()

    response = client.post("/api/v1/rbac/bootstrap/organization/999999999")

    assert response.status_code == 404
