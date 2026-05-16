"""add_rbac_fields_to_api_keys_and_usage_logs

Revision ID: 35e1d71641ed
Revises: 5363c037621c
Create Date: 2026-05-16 18:01:34.015745
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "35e1d71641ed"
down_revision: Union[str, None] = "5363c037621c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "api_keys",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="enterprise",
        ),
    )

    op.add_column(
        "api_keys",
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
            server_default="default",
        ),
    )

    op.add_column(
        "api_keys",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "api_keys",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "usage_logs",
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
            server_default="default",
        ),
    )

    op.add_column(
        "usage_logs",
        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=False,
            server_default="200",
        ),
    )

    op.add_column(
        "usage_logs",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("usage_logs", "created_at")
    op.drop_column("usage_logs", "status_code")
    op.drop_column("usage_logs", "tenant_id")

    op.drop_column("api_keys", "created_at")
    op.drop_column("api_keys", "is_active")
    op.drop_column("api_keys", "tenant_id")
    op.drop_column("api_keys", "role")