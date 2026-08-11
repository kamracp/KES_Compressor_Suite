from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now() -> datetime:
    """Return current UTC time as a naive datetime for DB compatibility."""

    return datetime.now(UTC).replace(tzinfo=None)


class User(Base):
    """Tenant-scoped SaaS user identity."""

    __tablename__ = "users"

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

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=False,
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
