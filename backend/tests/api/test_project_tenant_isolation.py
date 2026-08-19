from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.project import Project
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)


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


def prepare_tenant() -> tuple[dict, dict, dict[str, str]]:
    return prepare_authenticated_tenant(client)


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
