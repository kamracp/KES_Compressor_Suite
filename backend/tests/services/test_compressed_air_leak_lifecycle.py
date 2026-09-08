from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.compressed_air_leak import (
    CompressedAirLeak,
    CompressedAirLeakKpiSnapshot,
    CompressedAirLeakLifecycleStatus,
    CompressedAirLeakStatusHistory,
)
from app.models.project import Project
from app.repositories.project import project_repository
from app.schemas.compressed_air_leak_lifecycle import (
    CompressedAirLeakAssignRequest,
    CompressedAirLeakCloseRequest,
    CompressedAirLeakCreateRequest,
    CompressedAirLeakKpiSnapshotCreateRequest,
)
from app.schemas.project import ProjectCreate
from app.services.compressed_air_leak_lifecycle import (
    CompressedAirLeakNotFoundError,
    CompressedAirLeakProjectNotFoundError,
    DuplicateCompressedAirLeakCodeError,
    DuplicateCompressedAirLeakKpiSnapshotCodeError,
    InvalidCompressedAirLeakTransitionError,
    compressed_air_leak_lifecycle_service,
)
from tests.helpers.tenant_context import ensure_test_organization_id


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CompressedAirLeakKpiSnapshot))
        db.execute(delete(CompressedAirLeakStatusHistory))
        db.execute(delete(CompressedAirLeak))
        db.execute(delete(Project))
        db.commit()


def create_test_project(
    *,
    project_code: str,
) -> tuple[int, int]:
    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        project = project_repository.create(
            db,
            organization_id=organization_id,
            payload=ProjectCreate(
                project_code=project_code,
                project_name="Leak Lifecycle Test",
            ),
        )

        return organization_id, project.id


def create_test_leak(
    *,
    organization_id: int,
    project_id: int,
    leak_code: str,
) -> int:
    with SessionLocal() as db:
        leak = compressed_air_leak_lifecycle_service.create(
            db,
            organization_id=organization_id,
            project_id=project_id,
            request=CompressedAirLeakCreateRequest(
                leak_code=leak_code,
                location="Compressor room header",
                source_snapshot={
                    "baseline_leakage_flow_nm3_per_hr": "12.5",
                    "quantification_basis": "MEASURED",
                },
            ),
            actor="surveyor@example.com",
        )

        return leak.id


def test_leak_lifecycle_history_and_kpi_snapshot() -> None:
    reset_data()

    organization_id, project_id = create_test_project(
        project_code="KESC-LEAK-LIFE-001",
    )

    leak_id = create_test_leak(
        organization_id=organization_id,
        project_id=project_id,
        leak_code="LEAK-001",
    )

    with SessionLocal() as db:
        register = compressed_air_leak_lifecycle_service.list_by_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        assert register.total_leaks == 1
        assert register.tagged_leaks == 1
        assert register.assigned_leaks == 0
        assert register.closed_leaks == 0

        assigned = compressed_air_leak_lifecycle_service.assign(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            request=CompressedAirLeakAssignRequest(
                assigned_to="maintenance@example.com",
                change_notes="Assigned during weekly leak review.",
            ),
            actor="supervisor@example.com",
        )

        assert assigned.lifecycle_status is CompressedAirLeakLifecycleStatus.ASSIGNED
        assert assigned.assigned_to == "maintenance@example.com"
        assert assigned.assigned_at is not None

        assigned_snapshot = compressed_air_leak_lifecycle_service.create_kpi_snapshot(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            request=CompressedAirLeakKpiSnapshotCreateRequest(
                snapshot_code="ASSIGNED-001",
                metrics_payload={
                    "leakage_flow_nm3_per_hr": "12.5",
                    "annual_cost": "45000",
                },
            ),
            actor="energy@example.com",
        )

        assert assigned_snapshot.leak_id == leak_id
        assert assigned_snapshot.lifecycle_status is CompressedAirLeakLifecycleStatus.ASSIGNED

        closed = compressed_air_leak_lifecycle_service.close(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            request=CompressedAirLeakCloseRequest(
                closure_evidence={
                    "verified_post_repair_flow_nm3_per_hr": "0.8",
                    "verification_method": "ULTRASONIC",
                },
                closure_notes="Repair verified at operating pressure.",
                change_notes="Leak closed after verification.",
            ),
            actor="verifier@example.com",
        )

        assert closed.lifecycle_status is CompressedAirLeakLifecycleStatus.CLOSED
        assert closed.closed_at is not None
        assert closed.closure_evidence is not None

        history = compressed_air_leak_lifecycle_service.list_status_history(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        assert tuple(item.new_status for item in history) == (
            CompressedAirLeakLifecycleStatus.TAGGED,
            CompressedAirLeakLifecycleStatus.ASSIGNED,
            CompressedAirLeakLifecycleStatus.CLOSED,
        )
        assert history[0].previous_status is None
        assert history[1].previous_status is (CompressedAirLeakLifecycleStatus.TAGGED)
        assert history[2].previous_status is (CompressedAirLeakLifecycleStatus.ASSIGNED)

        snapshots = compressed_air_leak_lifecycle_service.list_kpi_snapshots(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        assert len(snapshots) == 1
        assert snapshots[0].snapshot_code == "ASSIGNED-001"


def test_invalid_lifecycle_transitions_are_rejected() -> None:
    reset_data()

    organization_id, project_id = create_test_project(
        project_code="KESC-LEAK-LIFE-002",
    )

    leak_id = create_test_leak(
        organization_id=organization_id,
        project_id=project_id,
        leak_code="LEAK-002",
    )

    with SessionLocal() as db:
        try:
            compressed_air_leak_lifecycle_service.close(
                db,
                organization_id=organization_id,
                leak_id=leak_id,
                request=CompressedAirLeakCloseRequest(
                    closure_evidence={"verified": True},
                ),
                actor="verifier@example.com",
            )
        except InvalidCompressedAirLeakTransitionError:
            db.rollback()
        else:
            raise AssertionError("Expected TAGGED to CLOSED transition rejection.")

        compressed_air_leak_lifecycle_service.assign(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            request=CompressedAirLeakAssignRequest(
                assigned_to="maintenance@example.com",
            ),
            actor="supervisor@example.com",
        )

        try:
            compressed_air_leak_lifecycle_service.assign(
                db,
                organization_id=organization_id,
                leak_id=leak_id,
                request=CompressedAirLeakAssignRequest(
                    assigned_to="other@example.com",
                ),
                actor="supervisor@example.com",
            )
        except InvalidCompressedAirLeakTransitionError:
            db.rollback()
        else:
            raise AssertionError("Expected ASSIGNED to ASSIGNED transition rejection.")


def test_duplicate_leak_and_kpi_codes_are_rejected() -> None:
    reset_data()

    organization_id, project_id = create_test_project(
        project_code="KESC-LEAK-LIFE-003",
    )

    leak_id = create_test_leak(
        organization_id=organization_id,
        project_id=project_id,
        leak_code="LEAK-003",
    )

    with SessionLocal() as db:
        try:
            compressed_air_leak_lifecycle_service.create(
                db,
                organization_id=organization_id,
                project_id=project_id,
                request=CompressedAirLeakCreateRequest(
                    leak_code="LEAK-003",
                    location="Duplicate location",
                    source_snapshot={"flow": "5.0"},
                ),
                actor="surveyor@example.com",
            )
        except DuplicateCompressedAirLeakCodeError:
            pass
        else:
            raise AssertionError("Expected duplicate leak code rejection.")

        request = CompressedAirLeakKpiSnapshotCreateRequest(
            snapshot_code="KPI-001",
            metrics_payload={"leakage_flow_nm3_per_hr": "12.5"},
        )

        compressed_air_leak_lifecycle_service.create_kpi_snapshot(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            request=request,
            actor="energy@example.com",
        )

        try:
            compressed_air_leak_lifecycle_service.create_kpi_snapshot(
                db,
                organization_id=organization_id,
                leak_id=leak_id,
                request=request,
                actor="energy@example.com",
            )
        except DuplicateCompressedAirLeakKpiSnapshotCodeError:
            pass
        else:
            raise AssertionError("Expected duplicate KPI snapshot code rejection.")


def test_missing_project_and_cross_tenant_leak_are_hidden() -> None:
    reset_data()

    organization_id, project_id = create_test_project(
        project_code="KESC-LEAK-LIFE-004",
    )

    leak_id = create_test_leak(
        organization_id=organization_id,
        project_id=project_id,
        leak_code="LEAK-004",
    )

    with SessionLocal() as db:
        try:
            compressed_air_leak_lifecycle_service.create(
                db,
                organization_id=organization_id,
                project_id=999999,
                request=CompressedAirLeakCreateRequest(
                    leak_code="LEAK-MISSING",
                    location="Missing project",
                    source_snapshot={"flow": "1.0"},
                ),
                actor="surveyor@example.com",
            )
        except CompressedAirLeakProjectNotFoundError:
            pass
        else:
            raise AssertionError("Expected missing project rejection.")

        try:
            compressed_air_leak_lifecycle_service.get_by_id(
                db,
                organization_id=organization_id + 10000,
                leak_id=leak_id,
            )
        except CompressedAirLeakNotFoundError:
            pass
        else:
            raise AssertionError("Expected cross-tenant leak lookup rejection.")
