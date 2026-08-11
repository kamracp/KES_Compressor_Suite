from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole

client = TestClient(app)


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(UserRole))
        db.execute(delete(RolePermission))
        db.execute(delete(Permission))
        db.execute(delete(Role))
        db.execute(delete(User))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> dict:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": f"ORG-{uuid4().hex[:8]}",
            "organization_name": "RBAC API Organization",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_user(
    organization_id: int,
) -> dict:
    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": organization_id,
            "email": f"user-{uuid4().hex[:8]}@example.com",
            "full_name": "RBAC API User",
            "password": "Strong-Test-Password-123!",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_permission(
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


def test_create_and_get_role() -> None:
    cleanup_data()
    organization = create_organization()

    response = client.post(
        "/api/v1/rbac/roles",
        json={
            "organization_id": organization["id"],
            "role_code": "ENGINEER",
            "role_name": "Engineer",
        },
    )

    assert response.status_code == 201

    role = response.json()

    assert role["role_code"] == "ENGINEER"
    assert role["organization_id"] == organization["id"]

    response = client.get(f"/api/v1/rbac/roles/{role['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == role["id"]


def test_duplicate_role_returns_conflict() -> None:
    cleanup_data()
    organization = create_organization()

    payload = {
        "organization_id": organization["id"],
        "role_code": "ADMIN",
        "role_name": "Administrator",
    }

    first = client.post(
        "/api/v1/rbac/roles",
        json=payload,
    )

    second = client.post(
        "/api/v1/rbac/roles",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_list_roles_for_organization() -> None:
    cleanup_data()
    organization = create_organization()

    for code in ("ENGINEER", "VIEWER"):
        response = client.post(
            "/api/v1/rbac/roles",
            json={
                "organization_id": organization["id"],
                "role_code": code,
                "role_name": code.title(),
            },
        )

        assert response.status_code == 201

    response = client.get(f"/api/v1/rbac/roles/organization/{organization['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_assign_permission_and_resolve_effective_permissions() -> None:
    cleanup_data()

    organization = create_organization()
    user = create_user(organization["id"])

    permission = create_permission("project.read")

    role_response = client.post(
        "/api/v1/rbac/roles",
        json={
            "organization_id": organization["id"],
            "role_code": "VIEWER",
            "role_name": "Viewer",
        },
    )

    assert role_response.status_code == 201
    role = role_response.json()

    response = client.post(
        "/api/v1/rbac/role-permissions",
        json={
            "role_id": role["id"],
            "permission_id": permission.id,
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/api/v1/rbac/user-roles",
        json={
            "user_id": user["id"],
            "role_id": role["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(f"/api/v1/rbac/users/{user['id']}/permissions")

    assert response.status_code == 200
    assert response.json() == ["project.read"]


def test_cross_tenant_role_assignment_is_forbidden() -> None:
    cleanup_data()

    first_organization = create_organization()
    second_organization = create_organization()

    user = create_user(first_organization["id"])

    role_response = client.post(
        "/api/v1/rbac/roles",
        json={
            "organization_id": second_organization["id"],
            "role_code": "ADMIN",
            "role_name": "Administrator",
        },
    )

    assert role_response.status_code == 201

    response = client.post(
        "/api/v1/rbac/user-roles",
        json={
            "user_id": user["id"],
            "role_id": role_response.json()["id"],
        },
    )

    assert response.status_code == 403


def test_unknown_role_returns_not_found() -> None:
    cleanup_data()

    response = client.get("/api/v1/rbac/roles/999999999")

    assert response.status_code == 404
