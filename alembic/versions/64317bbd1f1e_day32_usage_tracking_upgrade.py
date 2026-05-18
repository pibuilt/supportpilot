"""day32_usage_tracking_upgrade

Revision ID: 64317bbd1f1e
Revises: 6bbd6579b0c8
Create Date: 2026-05-18 09:06:10.224525
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = (
    "64317bbd1f1e"
)

down_revision: Union[
    str,
    None,
] = "6bbd6579b0c8"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    op.alter_column(
        "usage_logs",
        "tokens_used",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="0",
    )

    op.alter_column(
        "usage_logs",
        "status_code",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="200",
    )


def downgrade() -> None:
    op.alter_column(
        "usage_logs",
        "tokens_used",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=None,
    )

    op.alter_column(
        "usage_logs",
        "status_code",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=None,
    )