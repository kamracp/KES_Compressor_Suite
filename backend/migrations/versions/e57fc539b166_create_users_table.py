"""create users table

Revision ID: e57fc539b166
Revises: 7923128f81b8
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e57fc539b166"
down_revision: str | None = "7923128f81b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey(
                "organizations.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "verified",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "organization_id",
            "email",
            name="uq_users_organization_email",
        ),
    )

    op.create_index(
        "ix_users_organization_id",
        "users",
        ["organization_id"],
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_index(
        "ix_users_organization_id",
        table_name="users",
    )

    op.drop_table("users")
