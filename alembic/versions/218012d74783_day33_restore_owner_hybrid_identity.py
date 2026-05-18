"""day33_restore_owner_hybrid_identity

Revision ID: 218012d74783
Revises: cbdfc9c1fb88
Create Date: 2026-05-18 20:19:23.282456
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = (
    "218012d74783"
)

down_revision: Union[
    str,
    None,
] = "cbdfc9c1fb88"

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
    op.add_column(
        "api_keys",
        sa.Column(
            "owner",
            sa.String(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE api_keys
        SET owner = users.full_name
        FROM users
        WHERE api_keys.user_id = users.id
        """
    )

    op.alter_column(
        "api_keys",
        "owner",
        nullable=False,
    )

    op.create_index(
        "ix_api_keys_owner",
        "api_keys",
        ["owner"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_api_keys_owner",
        table_name="api_keys",
    )

    op.drop_column(
        "api_keys",
        "owner",
    )