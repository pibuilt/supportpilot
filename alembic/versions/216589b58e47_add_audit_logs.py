"""add_audit_logs

Revision ID: 216589b58e47
Revises: 218012d74783
Create Date: 2026-05-19

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "216589b58e47"
down_revision: Union[str, None] = "218012d74783"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "api_key_id",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "event_type",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "resource_type",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "resource_id",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "action",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "ip_address",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "user_agent",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "event_metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),

        sa.ForeignKeyConstraint(
            ["api_key_id"],
            ["api_keys.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_audit_logs_user_id",
        "audit_logs",
        ["user_id"],
    )

    op.create_index(
        "ix_audit_logs_api_key_id",
        "audit_logs",
        ["api_key_id"],
    )

    op.create_index(
        "ix_audit_logs_event_type",
        "audit_logs",
        ["event_type"],
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
    )

    op.create_index(
        "ix_audit_logs_tenant_event",
        "audit_logs",
        ["tenant_id", "event_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_audit_logs_tenant_event",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_event_type",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_api_key_id",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_user_id",
        table_name="audit_logs",
    )

    op.drop_table("audit_logs")