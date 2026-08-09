from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CalculationType(StrEnum):
    """Supported compressor engineering calculation types."""

    COMPRESSION = "COMPRESSION"
    RECIPROCATING = "RECIPROCATING"
    CENTRIFUGAL = "CENTRIFUGAL"
    SELECTION = "SELECTION"


class CalculationStatus(StrEnum):
    """Lifecycle status of an engineering calculation case."""

    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    SUPERSEDED = "SUPERSEDED"


class CalculationCase(Base):
    """Persisted compressor engineering calculation case."""

    __tablename__ = "calculation_cases"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    calculation_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    calculation_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CalculationStatus.DRAFT.value,
        index=True,
    )

    revision: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    input_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    result_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    engineering_notes: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_calculation_cases_project_type",
            "project_id",
            "calculation_type",
        ),
        Index(
            "ix_calculation_cases_project_status",
            "project_id",
            "status",
        ),
    )
