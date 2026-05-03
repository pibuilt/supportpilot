"""add ticket category and priority

Revision ID: 5363c037621c
Revises: b2854419a025
Create Date: 2026-05-03 11:24:03.561485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5363c037621c'
down_revision: Union[str, None] = 'b2854419a025'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "category",
            sa.String(),
            nullable=False,
            server_default="general",
        ),
    )

    op.add_column(
        "tickets",
        sa.Column(
            "priority",
            sa.String(),
            nullable=False,
            server_default="low",
        ),
    )


def downgrade() -> None:
    op.drop_column("tickets", "priority")
    op.drop_column("tickets", "category")