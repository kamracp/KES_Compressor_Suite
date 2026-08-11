from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.organization import Organization

client = TestClient(app)


def cleanup_organizations() -> None:
    with SessionLocal() as db:
        db.execute(delete(Organization))
        db.commit()


def build_payload(
    *,
    organization_code: str | None = None,
    active: bool = True,
) -> dict:
    code = organization_code or f"ORG-{uuid4().hex[:8]}"

    return {
        "organization_code": code,
        "organization_name": "Kamra Engineering Test Organization",
        "legal_name": "Kamra Engineering Test Organization Private",
        "country_code": "in",
        "timezone": "Asia/Kolkata",
        "default_currency": "inr",
        "active": active,
        "notes": "Automated organization API test.",
    }


def test_create_organization() -> None:
    cleanup_organizations()

    payload = build_payload()

    response = client.post(
        "/api/v1/organizations",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["organization_code"] == payload["organization_code"].upper()
    assert data["organization_name"] == payload["organization_name"]
    assert data["country_code"] == "IN"
    assert data["default_currency"] == "INR"
    assert data["timezone"] == "Asia/Kolkata"
    assert data["active"] is True


def test_duplicate_organization_code_returns_409() -> None:
    cleanup_organizations()

    code = f"ORG-{uuid4().hex[:8]}"

    first_payload = build_payload(
        organization_code=code,
    )

    second_payload = build_payload(
        organization_code=code.lower(),
    )

    first = client.post(
        "/api/v1/organizations",
        json=first_payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/organizations",
        json=second_payload,
    )

    assert second.status_code == 409
    assert "already exists" in second.json()["detail"]


def test_get_organization_by_id() -> None:
    cleanup_organizations()

    create_response = client.post(
        "/api/v1/organizations",
        json=build_payload(),
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization_id


def test_get_organization_by_code_is_normalized() -> None:
    cleanup_organizations()

    code = f"ORG-{uuid4().hex[:8]}"

    create_response = client.post(
        "/api/v1/organizations",
        json=build_payload(
            organization_code=code,
        ),
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/api/v1/organizations/code/{code.lower()}"
    )

    assert response.status_code == 200
    assert response.json()["organization_code"] == code.upper()


def test_list_organizations() -> None:
    cleanup_organizations()

    assert (
        client.post(
            "/api/v1/organizations",
            json=build_payload(),
        ).status_code
        == 201
    )

    assert (
        client.post(
            "/api/v1/organizations",
            json=build_payload(),
        ).status_code
        == 201
    )

    response = client.get(
        "/api/v1/organizations"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_active_organizations_only() -> None:
    cleanup_organizations()

    assert (
        client.post(
            "/api/v1/organizations",
            json=build_payload(
                active=True,
            ),
        ).status_code
        == 201
    )

    assert (
        client.post(
            "/api/v1/organizations",
            json=build_payload(
                active=False,
            ),
        ).status_code
        == 201
    )

    response = client.get(
        "/api/v1/organizations",
        params={
            "active_only": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["active"] is True


def test_update_organization() -> None:
    cleanup_organizations()

    create_response = client.post(
        "/api/v1/organizations",
        json=build_payload(),
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/organizations/{organization_id}",
        json={
            "organization_name": "Updated Engineering Organization",
            "default_currency": "usd",
            "active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_name"] == (
        "Updated Engineering Organization"
    )

    assert data["default_currency"] == "USD"
    assert data["active"] is False


def test_unknown_organization_returns_404() -> None:
    cleanup_organizations()

    response = client.get(
        "/api/v1/organizations/999999999"
    )

    assert response.status_code == 404


def test_unknown_organization_code_returns_404() -> None:
    cleanup_organizations()

    response = client.get(
        "/api/v1/organizations/code/UNKNOWN-ORG"
    )

    assert response.status_code == 404
