from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.permission import Permission
from app.models.role import Role
from app.services.permission_catalog import PERMISSION_CATALOG
from app.services.system_role_catalog import SYSTEM_ROLE_CATALOG
from tests.helpers.api_tenant_auth import (
    create_test_user,
    login_headers,
    prepare_authenticated_tenant,
)

client = TestClient(app)


def test_bootstrap_current_tenant_returns_system_roles() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        f"/api/v1/rbac/bootstrap/organization/{organization['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == len(SYSTEM_ROLE_CATALOG)

    role_codes = {item["role_code"] for item in data}

    assert role_codes == {role.role_code for role in SYSTEM_ROLE_CATALOG}

    assert all(item["organization_id"] == organization["id"] for item in data)


def test_bootstrap_current_tenant_is_idempotent() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    first = client.post(
        f"/api/v1/rbac/bootstrap/organization/{organization['id']}",
        headers=headers,
    )

    second = client.post(
        f"/api/v1/rbac/bootstrap/organization/{organization['id']}",
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    with SessionLocal() as db:
        roles = tuple(
            db.execute(
                select(Role).where(
                    Role.organization_id == organization["id"],
                )
            ).scalars()
        )

        permission_codes = set(
            db.execute(
                select(Permission.permission_code).where(
                    Permission.permission_code.in_(
                        [item.permission_code for item in PERMISSION_CATALOG]
                    )
                )
            ).scalars()
        )

    assert len(roles) == len(SYSTEM_ROLE_CATALOG)

    assert permission_codes == {item.permission_code for item in PERMISSION_CATALOG}


def test_bootstrap_requires_authentication() -> None:
    response = client.post(
        "/api/v1/rbac/bootstrap/organization/999999999",
    )

    assert response.status_code == 401


def test_bootstrap_requires_role_manage_permission() -> None:
    organization, _, _ = prepare_authenticated_tenant(client)

    user = create_test_user(
        client,
        organization_id=organization["id"],
    )

    headers = login_headers(
        client,
        organization_id=organization["id"],
        email=user["email"],
    )

    response = client.post(
        f"/api/v1/rbac/bootstrap/organization/{organization['id']}",
        headers=headers,
    )

    assert response.status_code == 403


def test_cross_tenant_bootstrap_returns_404() -> None:
    first_organization, _, first_headers = prepare_authenticated_tenant(client)
    second_organization, _, _ = prepare_authenticated_tenant(client)

    response = client.post(
        (f"/api/v1/rbac/bootstrap/organization/{second_organization['id']}"),
        headers=first_headers,
    )

    assert response.status_code == 404, response.text

    assert first_organization["id"] != second_organization["id"]


def test_unknown_organization_returns_404() -> None:
    _, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/rbac/bootstrap/organization/999999999",
        headers=headers,
    )

    assert response.status_code == 404
