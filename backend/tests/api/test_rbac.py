from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.permission import Permission
from tests.helpers.api_tenant_auth import (
    create_test_user,
    login_headers,
    prepare_authenticated_tenant,
)

client = TestClient(app)


def create_custom_role(
    *,
    organization_id: int,
    headers: dict[str, str],
    role_code: str = "CUSTOM_AUDITOR",
) -> dict:
    response = client.post(
        "/api/v1/rbac/roles",
        headers=headers,
        json={
            "organization_id": organization_id,
            "role_code": role_code,
            "role_name": "Custom Auditor",
        },
    )

    assert response.status_code == 201
    return response.json()


def get_permission_id(
    permission_code: str,
) -> int:
    with SessionLocal() as db:
        permission_id = db.scalar(
            select(Permission.id).where(
                Permission.permission_code == permission_code,
            )
        )

    assert permission_id is not None
    return permission_id


def test_create_get_and_update_current_tenant_role() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    role = create_custom_role(
        organization_id=organization["id"],
        headers=headers,
    )

    response = client.get(
        f"/api/v1/rbac/roles/{role['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == role["id"]

    response = client.patch(
        f"/api/v1/rbac/roles/{role['id']}",
        headers=headers,
        json={
            "role_name": "Updated Custom Auditor",
        },
    )

    assert response.status_code == 200
    assert response.json()["role_name"] == "Updated Custom Auditor"


def test_duplicate_role_returns_409() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    create_custom_role(
        organization_id=organization["id"],
        headers=headers,
        role_code="CUSTOM_DUPLICATE",
    )

    response = client.post(
        "/api/v1/rbac/roles",
        headers=headers,
        json={
            "organization_id": organization["id"],
            "role_code": "CUSTOM_DUPLICATE",
            "role_name": "Duplicate Role",
        },
    )

    assert response.status_code == 409


def test_list_current_tenant_roles() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    role = create_custom_role(
        organization_id=organization["id"],
        headers=headers,
    )

    response = client.get(
        f"/api/v1/rbac/roles/organization/{organization['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    role_ids = {item["id"] for item in response.json()}

    assert role["id"] in role_ids

    assert all(item["organization_id"] == organization["id"] for item in response.json())


def test_list_permissions_requires_role_read() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        "/api/v1/rbac/permissions",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) > 0

    user = create_test_user(
        client,
        organization_id=organization["id"],
    )

    no_role_headers = login_headers(
        client,
        organization_id=organization["id"],
        email=user["email"],
    )

    response = client.get(
        "/api/v1/rbac/permissions",
        headers=no_role_headers,
    )

    assert response.status_code == 403


def test_assign_permission_and_role_and_resolve_permissions() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    user = create_test_user(
        client,
        organization_id=organization["id"],
    )

    role = create_custom_role(
        organization_id=organization["id"],
        headers=headers,
        role_code="CUSTOM_PROJECT_READER",
    )

    permission_id = get_permission_id("project.read")

    response = client.post(
        "/api/v1/rbac/role-permissions",
        headers=headers,
        json={
            "role_id": role["id"],
            "permission_id": permission_id,
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/api/v1/rbac/user-roles",
        headers=headers,
        json={
            "user_id": user["id"],
            "role_id": role["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"/api/v1/rbac/users/{user['id']}/permissions",
        headers=headers,
    )

    assert response.status_code == 200
    assert "project.read" in response.json()


def test_rbac_requires_authentication() -> None:
    response = client.get(
        "/api/v1/rbac/permissions",
    )

    assert response.status_code == 401


def test_role_management_requires_role_manage() -> None:
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
        "/api/v1/rbac/roles",
        headers=headers,
        json={
            "organization_id": organization["id"],
            "role_code": "FORBIDDEN_ROLE",
            "role_name": "Forbidden Role",
        },
    )

    assert response.status_code == 403


def test_cross_tenant_role_create_and_list_return_404() -> None:
    first_organization, _, first_headers = prepare_authenticated_tenant(client)
    second_organization, _, _ = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/rbac/roles",
        headers=first_headers,
        json={
            "organization_id": second_organization["id"],
            "role_code": "CROSS_TENANT",
            "role_name": "Cross Tenant Role",
        },
    )

    assert response.status_code == 404

    response = client.get(
        (f"/api/v1/rbac/roles/organization/{second_organization['id']}"),
        headers=first_headers,
    )

    assert response.status_code == 404

    assert first_organization["id"] != second_organization["id"]


def test_cross_tenant_role_get_and_update_return_404() -> None:
    _, _, first_headers = prepare_authenticated_tenant(client)

    second_organization, _, second_headers = prepare_authenticated_tenant(client)

    role = create_custom_role(
        organization_id=second_organization["id"],
        headers=second_headers,
    )

    response = client.get(
        f"/api/v1/rbac/roles/{role['id']}",
        headers=first_headers,
    )

    assert response.status_code == 404

    response = client.patch(
        f"/api/v1/rbac/roles/{role['id']}",
        headers=first_headers,
        json={
            "role_name": "Cross Tenant Update",
        },
    )

    assert response.status_code == 404


def test_cross_tenant_role_permission_assignment_returns_404() -> None:
    _, _, first_headers = prepare_authenticated_tenant(client)

    second_organization, _, second_headers = prepare_authenticated_tenant(client)

    role = create_custom_role(
        organization_id=second_organization["id"],
        headers=second_headers,
    )

    permission_id = get_permission_id("project.read")

    response = client.post(
        "/api/v1/rbac/role-permissions",
        headers=first_headers,
        json={
            "role_id": role["id"],
            "permission_id": permission_id,
        },
    )

    assert response.status_code == 404


def test_cross_tenant_user_role_assignment_returns_404() -> None:
    first_organization, _, first_headers = prepare_authenticated_tenant(client)

    second_organization, second_user, second_headers = prepare_authenticated_tenant(client)

    role = create_custom_role(
        organization_id=second_organization["id"],
        headers=second_headers,
    )

    response = client.post(
        "/api/v1/rbac/user-roles",
        headers=first_headers,
        json={
            "user_id": second_user["id"],
            "role_id": role["id"],
        },
    )

    assert response.status_code == 404

    assert first_organization["id"] != second_organization["id"]


def test_cross_tenant_effective_permissions_returns_404() -> None:
    _, _, first_headers = prepare_authenticated_tenant(client)
    _, second_user, _ = prepare_authenticated_tenant(client)

    response = client.get(
        f"/api/v1/rbac/users/{second_user['id']}/permissions",
        headers=first_headers,
    )

    assert response.status_code == 404


def test_unknown_role_returns_404() -> None:
    _, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        "/api/v1/rbac/roles/999999999",
        headers=headers,
    )

    assert response.status_code == 404
