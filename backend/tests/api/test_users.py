from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.api_tenant_auth import (
    TEST_PASSWORD,
    create_test_user,
    login_headers,
    prepare_authenticated_tenant,
)

client = TestClient(app)


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
        "password": TEST_PASSWORD,
        "active": active,
        "verified": False,
    }


def test_create_user_in_current_tenant() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            organization_id=organization["id"],
            email="ENGINEER@example.com",
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["organization_id"] == organization["id"]
    assert data["email"] == "engineer@example.com"
    assert data["full_name"] == "Engineering Test User"
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_within_tenant_returns_409() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    payload = build_user_payload(
        organization_id=organization["id"],
        email="duplicate@example.com",
    )

    first = client.post(
        "/api/v1/users",
        headers=headers,
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            **payload,
            "email": "DUPLICATE@example.com",
        },
    )

    assert second.status_code == 409


def test_read_current_tenant_users() -> None:
    organization, admin_user, headers = prepare_authenticated_tenant(client)

    created = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            organization_id=organization["id"],
            email="lookup@example.com",
        ),
    )

    assert created.status_code == 201

    created_user = created.json()

    list_response = client.get(
        f"/api/v1/users/organization/{organization['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200

    returned_ids = {item["id"] for item in list_response.json()}

    assert admin_user["id"] in returned_ids
    assert created_user["id"] in returned_ids

    id_response = client.get(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
    )

    assert id_response.status_code == 200
    assert id_response.json()["id"] == created_user["id"]

    email_response = client.get(
        (f"/api/v1/users/organization/{organization['id']}/email/lookup@example.com"),
        headers=headers,
    )

    assert email_response.status_code == 200
    assert email_response.json()["id"] == created_user["id"]


def test_list_active_users_only() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    inactive = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            organization_id=organization["id"],
            active=False,
        ),
    )

    assert inactive.status_code == 201

    response = client.get(
        f"/api/v1/users/organization/{organization['id']}",
        headers=headers,
        params={
            "active_only": True,
        },
    )

    assert response.status_code == 200

    returned_ids = {item["id"] for item in response.json()}

    assert inactive.json()["id"] not in returned_ids
    assert all(item["active"] for item in response.json())


def test_update_current_tenant_user() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    created = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            organization_id=organization["id"],
        ),
    )

    assert created.status_code == 201

    response = client.patch(
        f"/api/v1/users/{created.json()['id']}",
        headers=headers,
        json={
            "email": "UPDATED@example.com",
            "full_name": "Updated Engineering User",
            "verified": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "updated@example.com"
    assert data["full_name"] == "Updated Engineering User"
    assert data["verified"] is True


def test_users_require_authentication() -> None:
    response = client.get(
        "/api/v1/users/999999999",
    )

    assert response.status_code == 401


def test_users_require_read_permission() -> None:
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

    response = client.get(
        f"/api/v1/users/organization/{organization['id']}",
        headers=headers,
    )

    assert response.status_code == 403


def test_user_create_requires_manage_permission() -> None:
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
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            organization_id=organization["id"],
        ),
    )

    assert response.status_code == 403


def test_cross_tenant_user_create_returns_404() -> None:
    _, _, first_headers = prepare_authenticated_tenant(client)
    second_organization, _, _ = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/users",
        headers=first_headers,
        json=build_user_payload(
            organization_id=second_organization["id"],
        ),
    )

    assert response.status_code == 404


def test_cross_tenant_user_access_returns_404() -> None:
    first_organization, first_user, first_headers = prepare_authenticated_tenant(client)
    second_organization, second_user, _ = prepare_authenticated_tenant(client)

    list_response = client.get(
        f"/api/v1/users/organization/{second_organization['id']}",
        headers=first_headers,
    )

    assert list_response.status_code == 404

    get_response = client.get(
        f"/api/v1/users/{second_user['id']}",
        headers=first_headers,
    )

    assert get_response.status_code == 404

    email_response = client.get(
        (f"/api/v1/users/organization/{second_organization['id']}/email/{second_user['email']}"),
        headers=first_headers,
    )

    assert email_response.status_code == 404

    update_response = client.patch(
        f"/api/v1/users/{second_user['id']}",
        headers=first_headers,
        json={
            "full_name": "Cross Tenant Update",
        },
    )

    assert update_response.status_code == 404

    assert first_user["organization_id"] == first_organization["id"]


def test_unknown_user_returns_404() -> None:
    _, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        "/api/v1/users/999999999",
        headers=headers,
    )

    assert response.status_code == 404
