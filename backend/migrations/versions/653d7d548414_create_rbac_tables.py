"""create rbac tables

Revision ID: 653d7d548414
Revises: e57fc539b166
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "653d7d548414"
down_revision: str | None = "e57fc539b166"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "roles",
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
            "role_code",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "role_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "system_role",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "active",
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
            "role_code",
            name="uq_roles_organization_code",
        ),
    )

    op.create_index(
        "ix_roles_organization_id",
        "roles",
        ["organization_id"],
    )

    op.create_table(
        "permissions",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "permission_code",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "permission_name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "resource",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "active",
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
    )

    op.create_index(
        "ix_permissions_permission_code",
        "permissions",
        ["permission_code"],
        unique=True,
    )

    op.create_index(
        "ix_permissions_resource",
        "permissions",
        ["resource"],
    )

    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey(
                "roles.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            sa.Integer(),
            sa.ForeignKey(
                "permissions.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "granted_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey(
                "roles.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("role_permissions")

    op.drop_index(
        "ix_permissions_resource",
        table_name="permissions",
    )

    op.drop_index(
        "ix_permissions_permission_code",
        table_name="permissions",
    )

    op.drop_table("permissions")

    op.drop_index(
        "ix_roles_organization_id",
        table_name="roles",
    )

    op.drop_table("roles")
