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


def create_organization() -> dict:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": f"ORG-{uuid4().hex[:8]}",
            "organization_name": "Authentication Test Organization",
            "country_code": "IN",
            "timezone": "Asia/Kolkata",
            "default_currency": "INR",
            "active": True,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_user(
    *,
    organization_id: int,
    email: str = "auth-user@example.com",
    password: str = "Strong-Test-Password-123!",
    active: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": organization_id,
            "email": email,
            "full_name": "Authentication Test User",
            "password": password,
            "active": active,
            "verified": True,
        },
    )

    assert response.status_code == 201
    return response.json()


def login(
    *,
    organization_id: int,
    email: str,
    password: str,
):
    return client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": organization_id,
            "email": email,
            "password": password,
        },
    )


def test_login_returns_access_token() -> None:
    cleanup_data()

    organization = create_organization()

    create_user(
        organization_id=organization["id"],
    )

    response = login(
        organization_id=organization["id"],
        email="AUTH-USER@example.com",
        password="Strong-Test-Password-123!",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["expires_at"]


def test_login_rejects_wrong_password() -> None:
    cleanup_data()

    organization = create_organization()

    create_user(
        organization_id=organization["id"],
    )

    response = login(
        organization_id=organization["id"],
        email="auth-user@example.com",
        password="Wrong-Password",
    )

    assert response.status_code == 401


def test_login_rejects_unknown_email() -> None:
    cleanup_data()

    organization = create_organization()

    response = login(
        organization_id=organization["id"],
        email="unknown@example.com",
        password="Strong-Test-Password-123!",
    )

    assert response.status_code == 401


def test_login_rejects_inactive_user() -> None:
    cleanup_data()

    organization = create_organization()

    create_user(
        organization_id=organization["id"],
        active=False,
    )

    response = login(
        organization_id=organization["id"],
        email="auth-user@example.com",
        password="Strong-Test-Password-123!",
    )

    assert response.status_code == 403


def test_me_returns_authenticated_user() -> None:
    cleanup_data()

    organization = create_organization()

    user = create_user(
        organization_id=organization["id"],
    )

    login_response = login(
        organization_id=organization["id"],
        email="auth-user@example.com",
        password="Strong-Test-Password-123!",
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user["id"]
    assert data["organization_id"] == organization["id"]
    assert data["email"] == "auth-user@example.com"
    assert data["active"] is True
    assert data["verified"] is True


def test_me_requires_authentication() -> None:
    cleanup_data()

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token() -> None:
    cleanup_data()

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_token_cannot_authenticate_deleted_user() -> None:
    cleanup_data()

    organization = create_organization()

    user = create_user(
        organization_id=organization["id"],
    )

    login_response = login(
        organization_id=organization["id"],
        email="auth-user@example.com",
        password="Strong-Test-Password-123!",
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    with SessionLocal() as db:
        stored_user = db.get(
            User,
            user["id"],
        )

        db.delete(stored_user)
        db.commit()

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401
