"""scope assessment codes to projects

Revision ID: dec0662d209f
Revises: ff4d2fabaf6b
Create Date: 2026-08-12 14:07:50.207201

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.

revision: str = "dec0662d209f"
down_revision: str | Sequence[str] | None = "ff4d2fabaf6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Scope assessment codes to their parent project."""

    op.drop_index(
        "ix_compressed_air_assessments_assessment_code",
        table_name="compressed_air_assessments",
    )

    op.create_index(
        "ix_compressed_air_assessments_assessment_code",
        "compressed_air_assessments",
        ["assessment_code"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_compressed_air_assessments_project_code",
        "compressed_air_assessments",
        [
            "project_id",
            "assessment_code",
        ],
    )


def downgrade() -> None:
    """Restore globally unique assessment codes."""

    op.drop_constraint(
        "uq_compressed_air_assessments_project_code",
        "compressed_air_assessments",
        type_="unique",
    )

    op.drop_index(
        "ix_compressed_air_assessments_assessment_code",
        table_name="compressed_air_assessments",
    )

    op.create_index(
        "ix_compressed_air_assessments_assessment_code",
        "compressed_air_assessments",
        ["assessment_code"],
        unique=True,
    )
