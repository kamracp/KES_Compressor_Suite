from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.models.user import User

client = TestClient(app)


def cleanup_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(User))
        db.execute(delete(Organization))
        db.commit()


def create_organization(
    *,
    organization_code: str | None = None,
) -> dict:
    code = organization_code or f"ORG-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": code,
            "organization_name": "User API Test Organization",
            "country_code": "IN",
            "timezone": "Asia/Kolkata",
            "default_currency": "INR",
            "active": True,
        },
    )

    assert response.status_code == 201

    return response.json()


def build_user_payload(
    *,
    organization_id: int,
    email: str | None = None,
    active: bool = True,
) -> dict:
    return {
        "organization_id": organization_id,
        "email": email or f"user-{uuid4().hex[:8]}@example.com",
        "full_name": "Engineering Test User",
        "password": "Strong-Test-Password-123!",
        "active": active,
        "verified": False,
    }


def test_create_user() -> None:
    cleanup_data()

    organization = create_organization()

    payload = build_user_payload(
        organization_id=organization["id"],
        email="ENGINEER@example.com",
    )

    response = client.post(
        "/api/v1/users",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["organization_id"] == organization["id"]
    assert data["email"] == "engineer@example.com"
    assert data["full_name"] == "Engineering Test User"
    assert data["active"] is True
    assert data["verified"] is False


def test_user_response_does_not_expose_password() -> None:
    cleanup_data()

    organization = create_organization()

    response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data


def test_unknown_organization_returns_404() -> None:
    cleanup_data()

    response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=999999999,
        ),
    )

    assert response.status_code == 404


def test_duplicate_email_within_same_organization_returns_409() -> None:
    cleanup_data()

    organization = create_organization()

    payload = build_user_payload(
        organization_id=organization["id"],
        email="duplicate@example.com",
    )

    first = client.post(
        "/api/v1/users",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/users",
        json={
            **payload,
            "email": "DUPLICATE@example.com",
        },
    )

    assert second.status_code == 409
    assert "already exists" in second.json()["detail"]


def test_same_email_is_allowed_in_different_organizations() -> None:
    cleanup_data()

    first_organization = create_organization()
    second_organization = create_organization()

    email = "shared@example.com"

    first = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=first_organization["id"],
            email=email,
        ),
    )

    second = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=second_organization["id"],
            email=email,
        ),
    )

    assert first.status_code == 201
    assert second.status_code == 201


def test_get_user_by_id() -> None:
    cleanup_data()

    organization = create_organization()

    create_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
        ),
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_by_email() -> None:
    cleanup_data()

    organization = create_organization()

    email = "lookup@example.com"

    create_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
            email=email,
        ),
    )

    assert create_response.status_code == 201

    response = client.get(f"/api/v1/users/organization/{organization['id']}/email/{email}")

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_list_users_by_organization() -> None:
    cleanup_data()

    organization = create_organization()

    for _ in range(2):
        response = client.post(
            "/api/v1/users",
            json=build_user_payload(
                organization_id=organization["id"],
            ),
        )

        assert response.status_code == 201

    response = client.get(f"/api/v1/users/organization/{organization['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_active_users_only() -> None:
    cleanup_data()

    organization = create_organization()

    active_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
            active=True,
        ),
    )

    inactive_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
            active=False,
        ),
    )

    assert active_response.status_code == 201
    assert inactive_response.status_code == 201

    response = client.get(
        f"/api/v1/users/organization/{organization['id']}",
        params={
            "active_only": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["active"] is True


def test_update_user() -> None:
    cleanup_data()

    organization = create_organization()

    create_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            organization_id=organization["id"],
        ),
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "email": "UPDATED@example.com",
            "full_name": "Updated Engineering User",
            "active": False,
            "verified": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "updated@example.com"
    assert data["full_name"] == "Updated Engineering User"
    assert data["active"] is False
    assert data["verified"] is True


def test_unknown_user_returns_404() -> None:
    cleanup_data()

    response = client.get("/api/v1/users/999999999")

    assert response.status_code == 404
