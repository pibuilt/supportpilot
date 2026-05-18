"""day33_identity_rbac_refactor

Revision ID: cbdfc9c1fb88
Revises: 64317bbd1f1e
Create Date: 2026-05-18 09:47:43.048598
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = (
    "cbdfc9c1fb88"
)

down_revision: Union[
    str,
    None,
] = "64317bbd1f1e"

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
            "user_id",
            sa.String(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE api_keys
        SET user_id = owner
        """
    )

    op.alter_column(
        "api_keys",
        "user_id",
        nullable=False,
    )

    op.create_index(
        "ix_api_keys_user_id",
        "api_keys",
        ["user_id"],
    )

    op.drop_column(
        "api_keys",
        "owner",
    )


def downgrade() -> None:
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
        SET owner = user_id
        """
    )

    op.alter_column(
        "api_keys",
        "owner",
        nullable=False,
    )

    op.drop_index(
        "ix_api_keys_user_id",
        table_name="api_keys",
    )

    op.drop_column(
        "api_keys",
        "user_id",
    )