"""add async jobs table

Revision ID: f2adadd12bb3
Revises: 216589b58e47
Create Date: 2026-05-23 17:28:34.143506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2adadd12bb3"
down_revision: Union[str, None] = "216589b58e47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "async_jobs",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "job_type",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        op.f("ix_async_jobs_document_id"),
        "async_jobs",
        ["document_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_async_jobs_owner_id"),
        "async_jobs",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_async_jobs_tenant_id"),
        "async_jobs",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_async_jobs_tenant_id"),
        table_name="async_jobs",
    )

    op.drop_index(
        op.f("ix_async_jobs_owner_id"),
        table_name="async_jobs",
    )

    op.drop_index(
        op.f("ix_async_jobs_document_id"),
        table_name="async_jobs",
    )

    op.drop_table(
        "async_jobs",
    )