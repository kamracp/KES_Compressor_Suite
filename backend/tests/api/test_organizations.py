from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.api_tenant_auth import (
    create_test_user,
    login_headers,
    prepare_authenticated_tenant,
)

client = TestClient(app)


def test_list_current_organization() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        "/api/v1/organizations",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == organization["id"]
    assert data[0]["organization_code"] == organization["organization_code"]


def test_get_current_organization_by_id() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        f"/api/v1/organizations/{organization['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization["id"]


def test_get_current_organization_by_code_is_normalized() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.get(
        (f"/api/v1/organizations/code/{organization['organization_code'].lower()}"),
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization["id"]


def test_update_current_organization() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}",
        headers=headers,
        json={
            "organization_name": "Updated Engineering Organization",
            "default_currency": "usd",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_name"] == "Updated Engineering Organization"
    assert data["default_currency"] == "USD"


def test_active_only_excludes_inactive_current_organization() -> None:
    organization, _, headers = prepare_authenticated_tenant(client)

    update_response = client.patch(
        f"/api/v1/organizations/{organization['id']}",
        headers=headers,
        json={
            "active": False,
        },
    )

    assert update_response.status_code == 200

    response = client.get(
        "/api/v1/organizations",
        headers=headers,
        params={
            "active_only": True,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_organizations_require_authentication() -> None:
    response = client.get(
        "/api/v1/organizations",
    )

    assert response.status_code == 401


def test_organizations_require_read_permission() -> None:
    organization, _, admin_headers = prepare_authenticated_tenant(client)

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
        "/api/v1/organizations",
        headers=headers,
    )

    assert response.status_code == 403

    assert admin_headers


def test_organization_update_requires_manage_permission() -> None:
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

    response = client.patch(
        f"/api/v1/organizations/{organization['id']}",
        headers=headers,
        json={
            "organization_name": "Forbidden Update",
        },
    )

    assert response.status_code == 403


def test_cross_tenant_organization_by_id_returns_404() -> None:
    first_organization, _, _ = prepare_authenticated_tenant(client)
    _, _, second_headers = prepare_authenticated_tenant(client)

    response = client.get(
        f"/api/v1/organizations/{first_organization['id']}",
        headers=second_headers,
    )

    assert response.status_code == 404


def test_cross_tenant_organization_by_code_returns_404() -> None:
    first_organization, _, _ = prepare_authenticated_tenant(client)
    _, _, second_headers = prepare_authenticated_tenant(client)

    response = client.get(
        (f"/api/v1/organizations/code/{first_organization['organization_code']}"),
        headers=second_headers,
    )

    assert response.status_code == 404


def test_cross_tenant_organization_update_returns_404() -> None:
    first_organization, _, _ = prepare_authenticated_tenant(client)
    _, _, second_headers = prepare_authenticated_tenant(client)

    response = client.patch(
        f"/api/v1/organizations/{first_organization['id']}",
        headers=second_headers,
        json={
            "organization_name": "Cross Tenant Update",
        },
    )

    assert response.status_code == 404


def test_public_organization_creation_is_not_exposed() -> None:
    response = client.post(
        "/api/v1/organizations",
        json={
            "organization_code": "PUBLIC-CREATE",
            "organization_name": "Public Organization",
        },
    )

    assert response.status_code == 405
