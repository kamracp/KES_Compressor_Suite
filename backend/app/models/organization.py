from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now() -> datetime:
    """Return current UTC time as a naive datetime for DB compatibility."""

    return datetime.now(UTC).replace(tzinfo=None)


class Organization(Base):
    """Top-level SaaS tenant organization."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    organization_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    organization_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="IN",
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Asia/Kolkata",
    )

    default_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
