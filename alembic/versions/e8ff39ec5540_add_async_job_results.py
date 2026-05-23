"""add async job results

Revision ID: e8ff39ec5540
Revises: f2adadd12bb3
Create Date: 2026-05-23 20:49:05.654651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8ff39ec5540"
down_revision: Union[str, None] = "f2adadd12bb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "async_jobs",
        sa.Column(
            "result_json",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "async_jobs",
        "result_json",
    )