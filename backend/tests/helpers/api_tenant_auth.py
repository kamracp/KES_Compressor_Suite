from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.role import Role

TEST_PASSWORD = "Strong-Test-Password-123!"


def create_test_organization(
    client: TestClient,
) -> dict:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": f"ORG-{uuid4().hex[:8]}",
            "organization_name": "Authenticated API Test Organization",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_user(
    client: TestClient,
    *,
    organization_id: int,
) -> dict:
    email = f"user-{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": organization_id,
            "email": email,
            "full_name": "Authenticated API Test User",
            "password": TEST_PASSWORD,
            "active": True,
            "verified": True,
        },
    )

    assert response.status_code == 201
    return response.json()


def bootstrap_tenant_admin(
    client: TestClient,
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

    assert response.status_code in {201, 409}


def login_headers(
    client: TestClient,
    *,
    organization_id: int,
    email: str,
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": organization_id,
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def prepare_authenticated_tenant(
    client: TestClient,
) -> tuple[dict, dict, dict[str, str]]:
    organization = create_test_organization(client)

    user = create_test_user(
        client,
        organization_id=organization["id"],
    )

    bootstrap_tenant_admin(
        client,
        organization_id=organization["id"],
        user_id=user["id"],
    )

    headers = login_headers(
        client,
        organization_id=organization["id"],
        email=user["email"],
    )

    return organization, user, headers
