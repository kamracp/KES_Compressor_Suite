from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.compressed_air_leak import (
    CompressedAirLeak,
    CompressedAirLeakKpiSnapshot,
    CompressedAirLeakStatusHistory,
)
from app.models.project import Project
from tests.helpers.api_tenant_auth import (
    prepare_authenticated_tenant,
)

client = TestClient(app)

BASE_PATH = "/api/v1/compressed-air/leakage"


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CompressedAirLeakKpiSnapshot))
        db.execute(delete(CompressedAirLeakStatusHistory))
        db.execute(delete(CompressedAirLeak))
        db.execute(delete(Project))
        db.commit()


def prepare_context() -> tuple[dict, dict[str, str], int]:
    organization, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": f"LEAK-{uuid4().hex[:8]}",
            "project_name": "Leak Lifecycle API Test Project",
        },
    )

    assert response.status_code == 201

    return organization, headers, response.json()["id"]


def build_leak_payload(
    *,
    leak_code: str | None = None,
) -> dict[str, object]:
    return {
        "leak_code": leak_code or f"LEAK-{uuid4().hex[:10]}",
        "location": "Compressor room header",
        "source_snapshot": {
            "baseline_leakage_flow_nm3_per_hr": "12.5",
            "quantification_basis": "ULTRASONIC_ESTIMATE",
        },
    }


def create_leak(
    *,
    headers: dict[str, str],
    project_id: int,
    leak_code: str | None = None,
) -> dict:
    response = client.post(
        f"{BASE_PATH}/projects/{project_id}/records",
        headers=headers,
        json=build_leak_payload(leak_code=leak_code),
    )

    assert response.status_code == 201
    return response.json()


def test_authenticated_leak_lifecycle_api_flow() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    created = create_leak(
        headers=headers,
        project_id=project_id,
        leak_code="LEAK-API-001",
    )

    leak_id = created["id"]

    assert created["project_id"] == project_id
    assert created["lifecycle_status"] == "TAGGED"
    assert created["assigned_to"] is None
    assert created["closed_at"] is None

    detail = client.get(
        f"{BASE_PATH}/records/{leak_id}",
        headers=headers,
    )

    assert detail.status_code == 200
    assert detail.json()["id"] == leak_id

    register = client.get(
        f"{BASE_PATH}/projects/{project_id}/records",
        headers=headers,
    )

    assert register.status_code == 200
    assert register.json()["total_leaks"] == 1
    assert register.json()["tagged_leaks"] == 1

    assigned = client.patch(
        f"{BASE_PATH}/records/{leak_id}/assign",
        headers=headers,
        json={
            "assigned_to": "maintenance@example.com",
            "change_notes": "Assigned during weekly review.",
        },
    )

    assert assigned.status_code == 200
    assert assigned.json()["lifecycle_status"] == "ASSIGNED"
    assert assigned.json()["assigned_to"] == "maintenance@example.com"

    snapshot = client.post(
        f"{BASE_PATH}/records/{leak_id}/kpi-snapshots",
        headers=headers,
        json={
            "snapshot_code": "ASSIGNED-001",
            "metrics_payload": {
                "leakage_flow_nm3_per_hr": "12.5",
                "annual_cost": "45000",
            },
        },
    )

    assert snapshot.status_code == 201
    assert snapshot.json()["lifecycle_status"] == "ASSIGNED"

    closed = client.patch(
        f"{BASE_PATH}/records/{leak_id}/close",
        headers=headers,
        json={
            "closure_evidence": {
                "verified_post_repair_flow_nm3_per_hr": "0.8",
                "verification_method": "ULTRASONIC",
            },
            "closure_notes": "Repair verified.",
            "change_notes": "Closed after verification.",
        },
    )

    assert closed.status_code == 200
    assert closed.json()["lifecycle_status"] == "CLOSED"
    assert closed.json()["closed_at"] is not None

    history = client.get(
        f"{BASE_PATH}/records/{leak_id}/history",
        headers=headers,
    )

    assert history.status_code == 200
    assert [item["new_status"] for item in history.json()] == [
        "TAGGED",
        "ASSIGNED",
        "CLOSED",
    ]

    snapshots = client.get(
        f"{BASE_PATH}/records/{leak_id}/kpi-snapshots",
        headers=headers,
    )

    assert snapshots.status_code == 200
    assert len(snapshots.json()) == 1
    assert snapshots.json()[0]["snapshot_code"] == "ASSIGNED-001"

    final_register = client.get(
        f"{BASE_PATH}/projects/{project_id}/records",
        headers=headers,
    )

    assert final_register.status_code == 200
    assert final_register.json()["tagged_leaks"] == 0
    assert final_register.json()["assigned_leaks"] == 0
    assert final_register.json()["closed_leaks"] == 1


def test_duplicate_codes_return_409() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    created = create_leak(
        headers=headers,
        project_id=project_id,
        leak_code="LEAK-DUP-001",
    )

    duplicate_leak = client.post(
        f"{BASE_PATH}/projects/{project_id}/records",
        headers=headers,
        json=build_leak_payload(
            leak_code="LEAK-DUP-001",
        ),
    )

    assert duplicate_leak.status_code == 409

    leak_id = created["id"]
    snapshot_payload = {
        "snapshot_code": "KPI-DUP-001",
        "metrics_payload": {
            "leakage_flow_nm3_per_hr": "12.5",
        },
    }

    first_snapshot = client.post(
        f"{BASE_PATH}/records/{leak_id}/kpi-snapshots",
        headers=headers,
        json=snapshot_payload,
    )

    duplicate_snapshot = client.post(
        f"{BASE_PATH}/records/{leak_id}/kpi-snapshots",
        headers=headers,
        json=snapshot_payload,
    )

    assert first_snapshot.status_code == 201
    assert duplicate_snapshot.status_code == 409


def test_invalid_transitions_return_409() -> None:
    reset_data()
    _, headers, project_id = prepare_context()

    created = create_leak(
        headers=headers,
        project_id=project_id,
    )
    leak_id = created["id"]

    close_tagged = client.patch(
        f"{BASE_PATH}/records/{leak_id}/close",
        headers=headers,
        json={
            "closure_evidence": {"verified": True},
        },
    )

    assert close_tagged.status_code == 409

    assigned = client.patch(
        f"{BASE_PATH}/records/{leak_id}/assign",
        headers=headers,
        json={
            "assigned_to": "maintenance@example.com",
        },
    )

    assert assigned.status_code == 200

    assign_again = client.patch(
        f"{BASE_PATH}/records/{leak_id}/assign",
        headers=headers,
        json={
            "assigned_to": "other@example.com",
        },
    )

    assert assign_again.status_code == 409


def test_lifecycle_routes_require_authentication() -> None:
    reset_data()

    read_response = client.get(
        f"{BASE_PATH}/records/999999999",
    )
    create_response = client.post(
        f"{BASE_PATH}/projects/999999999/records",
        json=build_leak_payload(),
    )

    assert read_response.status_code == 401
    assert create_response.status_code == 401


def test_validation_and_missing_project_errors() -> None:
    reset_data()
    _, headers, _ = prepare_context()

    missing_project = client.post(
        f"{BASE_PATH}/projects/999999999/records",
        headers=headers,
        json=build_leak_payload(),
    )

    empty_snapshot = client.post(
        f"{BASE_PATH}/projects/999999999/records",
        headers=headers,
        json={
            "leak_code": "LEAK-EMPTY",
            "location": "Compressor room",
            "source_snapshot": {},
        },
    )

    unexpected_field = client.post(
        f"{BASE_PATH}/projects/999999999/records",
        headers=headers,
        json={
            **build_leak_payload(),
            "unexpected": True,
        },
    )

    assert missing_project.status_code == 404
    assert empty_snapshot.status_code == 422
    assert unexpected_field.status_code == 422


def test_cross_tenant_lifecycle_access_returns_404() -> None:
    reset_data()

    _, first_headers, first_project_id = prepare_context()
    _, second_headers, _ = prepare_context()

    created = create_leak(
        headers=first_headers,
        project_id=first_project_id,
    )

    leak_id = created["id"]

    detail = client.get(
        f"{BASE_PATH}/records/{leak_id}",
        headers=second_headers,
    )

    register = client.get(
        f"{BASE_PATH}/projects/{first_project_id}/records",
        headers=second_headers,
    )

    transition = client.patch(
        f"{BASE_PATH}/records/{leak_id}/assign",
        headers=second_headers,
        json={
            "assigned_to": "unauthorized@example.com",
        },
    )

    assert detail.status_code == 404
    assert register.status_code == 404
    assert transition.status_code == 404
