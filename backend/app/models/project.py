from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    """Tenant-scoped compressor engineering project master record."""

    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "project_code",
            name="uq_projects_organization_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    project_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    project_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    client_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    plant_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    service_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DRAFT",
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
