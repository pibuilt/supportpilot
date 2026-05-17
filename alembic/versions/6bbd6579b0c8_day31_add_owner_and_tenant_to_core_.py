"""day31_add_owner_and_tenant_to_core_models

Revision ID: 6bbd6579b0c8
Revises: 47b46b8a7183
Create Date: 2026-05-17 12:28:31.830214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6bbd6579b0c8"
down_revision: Union[str, None] = "47b46b8a7183"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # clause_analyses
    op.add_column(
        "clause_analyses",
        sa.Column(
            "owner_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.add_column(
        "clause_analyses",
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.create_index(
        op.f("ix_clause_analyses_owner_id"),
        "clause_analyses",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clause_analyses_tenant_id"),
        "clause_analyses",
        ["tenant_id"],
        unique=False,
    )

    # embeddings
    op.add_column(
        "embeddings",
        sa.Column(
            "owner_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.add_column(
        "embeddings",
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.create_index(
        op.f("ix_embeddings_owner_id"),
        "embeddings",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_embeddings_tenant_id"),
        "embeddings",
        ["tenant_id"],
        unique=False,
    )

    # tickets
    op.add_column(
        "tickets",
        sa.Column(
            "owner_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.add_column(
        "tickets",
        sa.Column(
            "tenant_id",
            sa.String(),
            nullable=False,
            server_default="system",
        ),
    )
    op.create_index(
        op.f("ix_tickets_owner_id"),
        "tickets",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tickets_tenant_id"),
        "tickets",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    # tickets
    op.drop_index(
        op.f("ix_tickets_tenant_id"),
        table_name="tickets",
    )
    op.drop_index(
        op.f("ix_tickets_owner_id"),
        table_name="tickets",
    )
    op.drop_column("tickets", "tenant_id")
    op.drop_column("tickets", "owner_id")

    # embeddings
    op.drop_index(
        op.f("ix_embeddings_tenant_id"),
        table_name="embeddings",
    )
    op.drop_index(
        op.f("ix_embeddings_owner_id"),
        table_name="embeddings",
    )
    op.drop_column("embeddings", "tenant_id")
    op.drop_column("embeddings", "owner_id")

    # clause_analyses
    op.drop_index(
        op.f("ix_clause_analyses_tenant_id"),
        table_name="clause_analyses",
    )
    op.drop_index(
        op.f("ix_clause_analyses_owner_id"),
        table_name="clause_analyses",
    )
    op.drop_column("clause_analyses", "tenant_id")
    op.drop_column("clause_analyses", "owner_id")