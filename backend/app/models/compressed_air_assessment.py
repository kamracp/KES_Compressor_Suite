from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CompressedAirAssessmentType(StrEnum):
    GREENFIELD = "GREENFIELD"
    BROWNFIELD = "BROWNFIELD"
    ADVANCED = "ADVANCED"
    STANDARDS = "STANDARDS"


class CompressedAirAssessmentStatus(StrEnum):
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    SUPERSEDED = "SUPERSEDED"


class CompressedAirAssessment(Base):
    """Persisted compressed-air engineering assessment snapshot."""

    __tablename__ = "compressed_air_assessments"

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

    assessment_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    assessment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CompressedAirAssessmentStatus.DRAFT.value,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    engineering_basis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    input_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    result_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    standards_snapshot: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    calculation_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
