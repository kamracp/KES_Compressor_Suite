from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.project import Project

client = TestClient(app)


def reset_projects() -> None:
    with SessionLocal() as db:
        db.execute(delete(Project))
        db.commit()


def test_create_project() -> None:
    reset_projects()

    payload = {
        "project_code": "KESC-T001",
        "project_name": "Test Compressor Project",
        "client_name": "Test Client",
        "plant_name": "Test Plant",
        "location": "India",
        "service_description": "Natural gas compression test project",
        "status": "DRAFT",
    }

    response = client.post("/api/v1/projects", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["project_code"] == "KESC-T001"
    assert data["project_name"] == "Test Compressor Project"
    assert data["status"] == "DRAFT"
    assert data["id"] > 0


def test_list_projects() -> None:
    reset_projects()

    client.post(
        "/api/v1/projects",
        json={
            "project_code": "KESC-T002",
            "project_name": "List Test Project",
        },
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["project_code"] == "KESC-T002"


def test_get_project() -> None:
    reset_projects()

    create_response = client.post(
        "/api/v1/projects",
        json={
            "project_code": "KESC-T003",
            "project_name": "Get Test Project",
        },
    )

    project_id = create_response.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["project_code"] == "KESC-T003"


def test_update_project() -> None:
    reset_projects()

    create_response = client.post(
        "/api/v1/projects",
        json={
            "project_code": "KESC-T004",
            "project_name": "Original Project Name",
        },
    )

    project_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "project_name": "Updated Project Name",
            "status": "ACTIVE",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_name"] == "Updated Project Name"
    assert data["status"] == "ACTIVE"


def test_delete_project() -> None:
    reset_projects()

    create_response = client.post(
        "/api/v1/projects",
        json={
            "project_code": "KESC-T005",
            "project_name": "Delete Test Project",
        },
    )

    project_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/projects/{project_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/projects/{project_id}")

    assert get_response.status_code == 404


def test_duplicate_project_code_returns_conflict() -> None:
    reset_projects()

    payload = {
        "project_code": "KESC-T006",
        "project_name": "Duplicate Test Project",
    }

    first_response = client.post("/api/v1/projects", json=payload)
    second_response = client.post("/api/v1/projects", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
