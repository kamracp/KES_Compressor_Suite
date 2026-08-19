from contextlib import suppress
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.organization import organization_service
from app.services.rbac import UserRoleConflictError, rbac_service
from app.services.rbac_bootstrap import rbac_bootstrap_service
from app.services.user import user_service

TEST_PASSWORD = "Strong-Test-Password-123!"


def create_test_organization(
    client: TestClient,
) -> dict:
    del client

    with SessionLocal() as db:
        organization = organization_service.create(
            db,
            OrganizationCreate(
                organization_code=f"ORG-{uuid4().hex[:8]}",
                organization_name="Authenticated API Test Organization",
            ),
        )

        return OrganizationResponse.model_validate(organization).model_dump(mode="json")


def create_test_user(
    client: TestClient,
    *,
    organization_id: int,
) -> dict:
    del client

    email = f"user-{uuid4().hex[:8]}@example.com"

    with SessionLocal() as db:
        user = user_service.create(
            db,
            UserCreate(
                organization_id=organization_id,
                email=email,
                full_name="Authenticated API Test User",
                password=TEST_PASSWORD,
                active=True,
                verified=True,
            ),
        )

        return UserResponse.model_validate(user).model_dump(mode="json")


def bootstrap_tenant_admin(
    client: TestClient,
    *,
    organization_id: int,
    user_id: int,
) -> None:
    del client

    with SessionLocal() as db:
        roles = rbac_bootstrap_service.bootstrap_organization(
            db,
            organization_id=organization_id,
        )

        tenant_admin = next(role for role in roles if role.role_code == "TENANT_ADMIN")

        with suppress(UserRoleConflictError):
            rbac_service.assign_role_to_user(
                db,
                user_id=user_id,
                role_id=tenant_admin.id,
            )


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

    return {"Authorization": (f"Bearer {response.json()['access_token']}")}


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
