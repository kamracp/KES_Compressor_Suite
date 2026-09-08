from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now() -> datetime:
    """Return the current UTC time as a naive datetime for DB compatibility."""

    return datetime.now(UTC).replace(tzinfo=None)


class CompressedAirLeakLifecycleStatus(StrEnum):
    """Workflow status for one persistent compressed-air leak record."""

    TAGGED = "TAGGED"
    ASSIGNED = "ASSIGNED"
    CLOSED = "CLOSED"


class CompressedAirLeak(Base):
    """Project-scoped compressed-air leak lifecycle record."""

    __tablename__ = "compressed_air_leaks"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "leak_code",
            name="uq_compressed_air_leaks_project_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    leak_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    lifecycle_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CompressedAirLeakLifecycleStatus.TAGGED.value,
        index=True,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    source_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    closure_evidence: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    closure_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tagged_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class CompressedAirLeakStatusHistory(Base):
    """Immutable transition history for a compressed-air leak."""

    __tablename__ = "compressed_air_leak_status_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    leak_id: Mapped[int] = mapped_column(
        ForeignKey(
            "compressed_air_leaks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    changed_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    change_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
        index=True,
    )


class CompressedAirLeakKpiSnapshot(Base):
    """Historical KPI snapshot for one compressed-air leak."""

    __tablename__ = "compressed_air_leak_kpi_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "leak_id",
            "snapshot_code",
            name="uq_compressed_air_leak_kpi_snapshots_leak_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    leak_id: Mapped[int] = mapped_column(
        ForeignKey(
            "compressed_air_leaks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    snapshot_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    lifecycle_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    metrics_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    captured_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
        index=True,
    )
