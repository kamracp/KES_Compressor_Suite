"""add organization ownership to projects

Revision ID: ff4d2fabaf6b
Revises: 653d7d548414
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ff4d2fabaf6b"
down_revision: str | None = "653d7d548414"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_projects_organization_id",
        "projects",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_projects_organization_id",
        "projects",
        ["organization_id"],
    )

    op.drop_index(
        "ix_projects_project_code",
        table_name="projects",
    )

    op.create_index(
        "ix_projects_project_code",
        "projects",
        ["project_code"],
    )

    op.create_unique_constraint(
        "uq_projects_organization_code",
        "projects",
        [
            "organization_id",
            "project_code",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_projects_organization_code",
        "projects",
        type_="unique",
    )

    op.drop_index(
        "ix_projects_project_code",
        table_name="projects",
    )

    op.create_index(
        "ix_projects_project_code",
        "projects",
        ["project_code"],
        unique=True,
    )

    op.drop_index(
        "ix_projects_organization_id",
        table_name="projects",
    )

    op.drop_constraint(
        "fk_projects_organization_id",
        "projects",
        type_="foreignkey",
    )

    op.drop_column(
        "projects",
        "organization_id",
    )
