from sqlalchemy.orm import Session

from app.models.compressed_air_leak import (
    CompressedAirLeak,
    CompressedAirLeakKpiSnapshot,
    CompressedAirLeakLifecycleStatus,
    CompressedAirLeakStatusHistory,
    utc_now,
)
from app.repositories.compressed_air_leak_lifecycle import (
    compressed_air_leak_lifecycle_repository,
)
from app.repositories.project import project_repository
from app.schemas.compressed_air_leak_lifecycle import (
    CompressedAirLeakAssignRequest,
    CompressedAirLeakCloseRequest,
    CompressedAirLeakCreateRequest,
    CompressedAirLeakKpiSnapshotCreateRequest,
    CompressedAirLeakKpiSnapshotResponse,
    CompressedAirLeakListResponse,
    CompressedAirLeakResponse,
    CompressedAirLeakStatusHistoryResponse,
)


class CompressedAirLeakNotFoundError(LookupError):
    """Raised when a tenant-scoped leak cannot be found."""


class CompressedAirLeakProjectNotFoundError(LookupError):
    """Raised when the tenant-scoped parent project cannot be found."""


class DuplicateCompressedAirLeakCodeError(ValueError):
    """Raised when a leak code already exists within a project."""


class DuplicateCompressedAirLeakKpiSnapshotCodeError(ValueError):
    """Raised when a KPI snapshot code already exists for a leak."""


class InvalidCompressedAirLeakTransitionError(ValueError):
    """Raised when a requested lifecycle transition is invalid."""


class CompressedAirLeakLifecycleService:
    """Application service for tenant-scoped leak lifecycles."""

    def _validate_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> None:
        project = project_repository.get_by_id(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        if project is None:
            raise CompressedAirLeakProjectNotFoundError(
                f"Project with id {project_id} was not found."
            )

    def _get_for_update(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> CompressedAirLeak:
        leak = compressed_air_leak_lifecycle_repository.get_by_id_for_update(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        if leak is None:
            raise CompressedAirLeakNotFoundError("Compressed-air leak not found.")

        return leak

    def create(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
        request: CompressedAirLeakCreateRequest,
        actor: str | None,
    ) -> CompressedAirLeakResponse:
        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        existing = compressed_air_leak_lifecycle_repository.get_by_code(
            db,
            organization_id=organization_id,
            project_id=project_id,
            leak_code=request.leak_code,
        )

        if existing is not None:
            raise DuplicateCompressedAirLeakCodeError(
                "Compressed-air leak code already exists in this project."
            )

        now = utc_now()

        leak = CompressedAirLeak(
            project_id=project_id,
            leak_code=request.leak_code,
            location=request.location,
            lifecycle_status=(CompressedAirLeakLifecycleStatus.TAGGED.value),
            source_snapshot=request.source_snapshot,
            created_by=actor,
            updated_by=actor,
            tagged_at=now,
            created_at=now,
            updated_at=now,
        )

        history = CompressedAirLeakStatusHistory(
            previous_status=None,
            new_status=CompressedAirLeakLifecycleStatus.TAGGED.value,
            changed_by=actor,
            change_notes="Leak tagged.",
            changed_at=now,
        )

        created = compressed_air_leak_lifecycle_repository.create_with_history(
            db,
            leak=leak,
            history=history,
        )

        return CompressedAirLeakResponse.model_validate(created)

    def get_by_id(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> CompressedAirLeakResponse:
        leak = compressed_air_leak_lifecycle_repository.get_by_id(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        if leak is None:
            raise CompressedAirLeakNotFoundError("Compressed-air leak not found.")

        return CompressedAirLeakResponse.model_validate(leak)

    def list_by_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> CompressedAirLeakListResponse:
        self._validate_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        leaks = compressed_air_leak_lifecycle_repository.list_by_project(
            db,
            organization_id=organization_id,
            project_id=project_id,
        )

        items = tuple(CompressedAirLeakResponse.model_validate(leak) for leak in leaks)

        return CompressedAirLeakListResponse(
            project_id=project_id,
            total_leaks=len(items),
            tagged_leaks=sum(
                item.lifecycle_status is CompressedAirLeakLifecycleStatus.TAGGED for item in items
            ),
            assigned_leaks=sum(
                item.lifecycle_status is CompressedAirLeakLifecycleStatus.ASSIGNED for item in items
            ),
            closed_leaks=sum(
                item.lifecycle_status is CompressedAirLeakLifecycleStatus.CLOSED for item in items
            ),
            items=items,
        )

    def assign(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
        request: CompressedAirLeakAssignRequest,
        actor: str | None,
    ) -> CompressedAirLeakResponse:
        leak = self._get_for_update(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        previous_status = CompressedAirLeakLifecycleStatus(leak.lifecycle_status)

        if previous_status is not CompressedAirLeakLifecycleStatus.TAGGED:
            raise InvalidCompressedAirLeakTransitionError("Only a TAGGED leak can be assigned.")

        now = utc_now()

        leak.lifecycle_status = CompressedAirLeakLifecycleStatus.ASSIGNED.value
        leak.assigned_to = request.assigned_to
        leak.assigned_at = now
        leak.updated_by = actor
        leak.updated_at = now

        history = CompressedAirLeakStatusHistory(
            leak_id=leak.id,
            previous_status=previous_status.value,
            new_status=CompressedAirLeakLifecycleStatus.ASSIGNED.value,
            changed_by=actor,
            change_notes=request.change_notes,
            changed_at=now,
        )

        updated = compressed_air_leak_lifecycle_repository.save_transition(
            db,
            leak=leak,
            history=history,
        )

        return CompressedAirLeakResponse.model_validate(updated)

    def close(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
        request: CompressedAirLeakCloseRequest,
        actor: str | None,
    ) -> CompressedAirLeakResponse:
        leak = self._get_for_update(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        previous_status = CompressedAirLeakLifecycleStatus(leak.lifecycle_status)

        if previous_status is not CompressedAirLeakLifecycleStatus.ASSIGNED:
            raise InvalidCompressedAirLeakTransitionError("Only an ASSIGNED leak can be closed.")

        now = utc_now()

        leak.lifecycle_status = CompressedAirLeakLifecycleStatus.CLOSED.value
        leak.closure_evidence = request.closure_evidence
        leak.closure_notes = request.closure_notes
        leak.closed_at = now
        leak.updated_by = actor
        leak.updated_at = now

        history = CompressedAirLeakStatusHistory(
            leak_id=leak.id,
            previous_status=previous_status.value,
            new_status=CompressedAirLeakLifecycleStatus.CLOSED.value,
            changed_by=actor,
            change_notes=request.change_notes,
            changed_at=now,
        )

        updated = compressed_air_leak_lifecycle_repository.save_transition(
            db,
            leak=leak,
            history=history,
        )

        return CompressedAirLeakResponse.model_validate(updated)

    def list_status_history(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> tuple[CompressedAirLeakStatusHistoryResponse, ...]:
        self.get_by_id(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        history = compressed_air_leak_lifecycle_repository.list_status_history(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        return tuple(
            CompressedAirLeakStatusHistoryResponse.model_validate(item) for item in history
        )

    def create_kpi_snapshot(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
        request: CompressedAirLeakKpiSnapshotCreateRequest,
        actor: str | None,
    ) -> CompressedAirLeakKpiSnapshotResponse:
        leak = compressed_air_leak_lifecycle_repository.get_by_id(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        if leak is None:
            raise CompressedAirLeakNotFoundError("Compressed-air leak not found.")

        existing = compressed_air_leak_lifecycle_repository.get_kpi_snapshot_by_code(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
            snapshot_code=request.snapshot_code,
        )

        if existing is not None:
            raise DuplicateCompressedAirLeakKpiSnapshotCodeError(
                "KPI snapshot code already exists for this leak."
            )

        snapshot = CompressedAirLeakKpiSnapshot(
            leak_id=leak.id,
            snapshot_code=request.snapshot_code,
            lifecycle_status=leak.lifecycle_status,
            metrics_payload=request.metrics_payload,
            captured_by=actor,
            captured_at=utc_now(),
        )

        created = compressed_air_leak_lifecycle_repository.create_kpi_snapshot(
            db,
            snapshot,
        )

        return CompressedAirLeakKpiSnapshotResponse.model_validate(created)

    def list_kpi_snapshots(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> tuple[CompressedAirLeakKpiSnapshotResponse, ...]:
        self.get_by_id(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        snapshots = compressed_air_leak_lifecycle_repository.list_kpi_snapshots(
            db,
            organization_id=organization_id,
            leak_id=leak_id,
        )

        return tuple(
            CompressedAirLeakKpiSnapshotResponse.model_validate(item) for item in snapshots
        )


compressed_air_leak_lifecycle_service = CompressedAirLeakLifecycleService()
