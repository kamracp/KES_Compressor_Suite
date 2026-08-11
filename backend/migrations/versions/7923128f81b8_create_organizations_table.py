"""create organizations table

Revision ID: 7923128f81b8
Revises: e3ed2b2d3d03
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7923128f81b8"
down_revision: str | None = "e3ed2b2d3d03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "organization_code",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "organization_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "legal_name",
            sa.String(length=250),
            nullable=True,
        ),
        sa.Column(
            "country_code",
            sa.String(length=2),
            nullable=False,
        ),
        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "default_currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
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
    )

    op.create_index(
        "ix_organizations_organization_code",
        "organizations",
        ["organization_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organizations_organization_code",
        table_name="organizations",
    )

    op.drop_table("organizations")
