from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compressed_air_leak import (
    CompressedAirLeak,
    CompressedAirLeakKpiSnapshot,
    CompressedAirLeakStatusHistory,
)
from app.models.project import Project


class CompressedAirLeakLifecycleRepository:
    """Persistence operations for tenant-scoped leak lifecycles."""

    def create_with_history(
        self,
        db: Session,
        *,
        leak: CompressedAirLeak,
        history: CompressedAirLeakStatusHistory,
    ) -> CompressedAirLeak:
        db.add(leak)
        db.flush()

        history.leak_id = leak.id
        db.add(history)

        db.commit()
        db.refresh(leak)
        return leak

    def get_by_id(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> CompressedAirLeak | None:
        statement = (
            select(CompressedAirLeak)
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeak.id == leak_id,
                Project.organization_id == organization_id,
            )
        )

        return db.scalar(statement)

    def get_by_id_for_update(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> CompressedAirLeak | None:
        statement = (
            select(CompressedAirLeak)
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeak.id == leak_id,
                Project.organization_id == organization_id,
            )
            .with_for_update(of=CompressedAirLeak)
        )

        return db.scalar(statement)

    def get_by_code(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
        leak_code: str,
    ) -> CompressedAirLeak | None:
        statement = (
            select(CompressedAirLeak)
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeak.project_id == project_id,
                CompressedAirLeak.leak_code == leak_code,
                Project.organization_id == organization_id,
            )
        )

        return db.scalar(statement)

    def list_by_project(
        self,
        db: Session,
        *,
        organization_id: int,
        project_id: int,
    ) -> list[CompressedAirLeak]:
        statement = (
            select(CompressedAirLeak)
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeak.project_id == project_id,
                Project.organization_id == organization_id,
            )
            .order_by(
                CompressedAirLeak.created_at.desc(),
                CompressedAirLeak.id.desc(),
            )
        )

        return list(db.scalars(statement).all())

    def save_transition(
        self,
        db: Session,
        *,
        leak: CompressedAirLeak,
        history: CompressedAirLeakStatusHistory,
    ) -> CompressedAirLeak:
        db.add_all([leak, history])
        db.commit()
        db.refresh(leak)
        return leak

    def list_status_history(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> list[CompressedAirLeakStatusHistory]:
        statement = (
            select(CompressedAirLeakStatusHistory)
            .join(
                CompressedAirLeak,
                CompressedAirLeak.id == CompressedAirLeakStatusHistory.leak_id,
            )
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeakStatusHistory.leak_id == leak_id,
                Project.organization_id == organization_id,
            )
            .order_by(
                CompressedAirLeakStatusHistory.changed_at.asc(),
                CompressedAirLeakStatusHistory.id.asc(),
            )
        )

        return list(db.scalars(statement).all())

    def get_kpi_snapshot_by_code(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
        snapshot_code: str,
    ) -> CompressedAirLeakKpiSnapshot | None:
        statement = (
            select(CompressedAirLeakKpiSnapshot)
            .join(
                CompressedAirLeak,
                CompressedAirLeak.id == CompressedAirLeakKpiSnapshot.leak_id,
            )
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeakKpiSnapshot.leak_id == leak_id,
                CompressedAirLeakKpiSnapshot.snapshot_code == snapshot_code,
                Project.organization_id == organization_id,
            )
        )

        return db.scalar(statement)

    def create_kpi_snapshot(
        self,
        db: Session,
        snapshot: CompressedAirLeakKpiSnapshot,
    ) -> CompressedAirLeakKpiSnapshot:
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def list_kpi_snapshots(
        self,
        db: Session,
        *,
        organization_id: int,
        leak_id: int,
    ) -> list[CompressedAirLeakKpiSnapshot]:
        statement = (
            select(CompressedAirLeakKpiSnapshot)
            .join(
                CompressedAirLeak,
                CompressedAirLeak.id == CompressedAirLeakKpiSnapshot.leak_id,
            )
            .join(
                Project,
                Project.id == CompressedAirLeak.project_id,
            )
            .where(
                CompressedAirLeakKpiSnapshot.leak_id == leak_id,
                Project.organization_id == organization_id,
            )
            .order_by(
                CompressedAirLeakKpiSnapshot.captured_at.asc(),
                CompressedAirLeakKpiSnapshot.id.asc(),
            )
        )

        return list(db.scalars(statement).all())


compressed_air_leak_lifecycle_repository = CompressedAirLeakLifecycleRepository()
