from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.project import Project
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole

client = TestClient(app)

PASSWORD = "Strong-Test-Password-123!"


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(UserRole))
        db.execute(delete(RolePermission))
        db.execute(delete(Project))
        db.execute(delete(User))
        db.execute(delete(Role))
        db.execute(delete(Permission))
        db.execute(delete(Organization))
        db.commit()


def create_organization() -> dict:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": f"ORG-{uuid4().hex[:8]}",
            "organization_name": "Project Tenant Test Organization",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_user(
    *,
    organization_id: int,
) -> dict:
    email = f"user-{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": organization_id,
            "email": email,
            "full_name": "Tenant Project User",
            "password": PASSWORD,
            "active": True,
            "verified": True,
        },
    )

    assert response.status_code == 201

    data = response.json()
    data["password"] = PASSWORD

    return data


def bootstrap_admin_role(
    *,
    organization_id: int,
    user_id: int,
) -> None:
    response = client.post(f"/api/v1/rbac/bootstrap/organization/{organization_id}")

    assert response.status_code == 200

    with SessionLocal() as db:
        role = db.scalar(
            select(Role).where(
                Role.organization_id == organization_id,
                Role.role_code == "TENANT_ADMIN",
            )
        )

        assert role is not None
        role_id = role.id

    response = client.post(
        "/api/v1/rbac/user-roles",
        json={
            "user_id": user_id,
            "role_id": role_id,
        },
    )

    assert response.status_code == 201


def login_headers(
    *,
    organization_id: int,
    email: str,
    password: str,
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": organization_id,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def prepare_tenant() -> tuple[dict, dict, dict[str, str]]:
    organization = create_organization()

    user = create_user(
        organization_id=organization["id"],
    )

    bootstrap_admin_role(
        organization_id=organization["id"],
        user_id=user["id"],
    )

    headers = login_headers(
        organization_id=organization["id"],
        email=user["email"],
        password=user["password"],
    )

    return organization, user, headers


def create_project(
    *,
    headers: dict[str, str],
    project_code: str,
) -> dict:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": project_code,
            "project_name": "Tenant Isolation Project",
            "status": "DRAFT",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_project_is_owned_by_authenticated_tenant() -> None:
    cleanup_data()

    organization, _, headers = prepare_tenant()

    project = create_project(
        headers=headers,
        project_code="TENANT-PROJECT-001",
    )

    assert project["organization_id"] == organization["id"]


def test_same_project_code_is_allowed_in_different_tenants() -> None:
    cleanup_data()

    first_organization, _, first_headers = prepare_tenant()
    second_organization, _, second_headers = prepare_tenant()

    first = create_project(
        headers=first_headers,
        project_code="COMMON-001",
    )

    second = create_project(
        headers=second_headers,
        project_code="COMMON-001",
    )

    assert first["project_code"] == second["project_code"]
    assert first["organization_id"] == first_organization["id"]
    assert second["organization_id"] == second_organization["id"]


def test_duplicate_project_code_is_rejected_within_same_tenant() -> None:
    cleanup_data()

    _, _, headers = prepare_tenant()

    create_project(
        headers=headers,
        project_code="DUPLICATE-001",
    )

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": "DUPLICATE-001",
            "project_name": "Duplicate Project",
        },
    )

    assert response.status_code == 409


def test_project_list_contains_only_current_tenant_projects() -> None:
    cleanup_data()

    first_organization, _, first_headers = prepare_tenant()
    second_organization, _, second_headers = prepare_tenant()

    create_project(
        headers=first_headers,
        project_code="FIRST-001",
    )

    create_project(
        headers=second_headers,
        project_code="SECOND-001",
    )

    response = client.get(
        "/api/v1/projects",
        headers=first_headers,
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["project_code"] == "FIRST-001"
    assert projects[0]["organization_id"] == first_organization["id"]
    assert projects[0]["organization_id"] != second_organization["id"]


def test_cross_tenant_project_read_returns_not_found() -> None:
    cleanup_data()

    _, _, first_headers = prepare_tenant()
    _, _, second_headers = prepare_tenant()

    project = create_project(
        headers=first_headers,
        project_code="PRIVATE-001",
    )

    response = client.get(
        f"/api/v1/projects/{project['id']}",
        headers=second_headers,
    )

    assert response.status_code == 404


def test_cross_tenant_project_update_returns_not_found() -> None:
    cleanup_data()

    _, _, first_headers = prepare_tenant()
    _, _, second_headers = prepare_tenant()

    project = create_project(
        headers=first_headers,
        project_code="PRIVATE-UPDATE-001",
    )

    response = client.patch(
        f"/api/v1/projects/{project['id']}",
        headers=second_headers,
        json={
            "project_name": "Unauthorized Update",
        },
    )

    assert response.status_code == 404


def test_cross_tenant_project_delete_returns_not_found() -> None:
    cleanup_data()

    _, _, first_headers = prepare_tenant()
    _, _, second_headers = prepare_tenant()

    project = create_project(
        headers=first_headers,
        project_code="PRIVATE-DELETE-001",
    )

    response = client.delete(
        f"/api/v1/projects/{project['id']}",
        headers=second_headers,
    )

    assert response.status_code == 404

    response = client.get(
        f"/api/v1/projects/{project['id']}",
        headers=first_headers,
    )

    assert response.status_code == 200


def test_project_endpoint_requires_authentication() -> None:
    cleanup_data()

    response = client.get("/api/v1/projects")

    assert response.status_code == 401
