"""create compressed air assessments table

Revision ID: e3ed2b2d3d03
Revises: cbfc55903131
Create Date: 2026-08-09 15:26:27.786690
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e3ed2b2d3d03"
down_revision: str | None = "cbfc55903131"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "compressed_air_assessments",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey(
                "projects.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "assessment_code",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "assessment_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "engineering_basis",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "input_payload",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "result_payload",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "standards_snapshot",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "calculation_version",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            sa.String(length=255),
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
        "ix_compressed_air_assessments_project_id",
        "compressed_air_assessments",
        ["project_id"],
    )

    op.create_index(
        "ix_compressed_air_assessments_assessment_code",
        "compressed_air_assessments",
        ["assessment_code"],
        unique=True,
    )

    op.create_index(
        "ix_compressed_air_assessments_assessment_type",
        "compressed_air_assessments",
        ["assessment_type"],
    )

    op.create_index(
        "ix_compressed_air_assessments_status",
        "compressed_air_assessments",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_compressed_air_assessments_status",
        table_name="compressed_air_assessments",
    )

    op.drop_index(
        "ix_compressed_air_assessments_assessment_type",
        table_name="compressed_air_assessments",
    )

    op.drop_index(
        "ix_compressed_air_assessments_assessment_code",
        table_name="compressed_air_assessments",
    )

    op.drop_index(
        "ix_compressed_air_assessments_project_id",
        table_name="compressed_air_assessments",
    )

    op.drop_table("compressed_air_assessments")
