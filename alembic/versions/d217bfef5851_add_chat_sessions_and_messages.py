"""add_chat_sessions_and_messages

Revision ID: d217bfef5851
Revises: e8ff39ec5540
Create Date: 2026-05-23 23:15:43.165469
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d217bfef5851"
down_revision: Union[str, None] = "e8ff39ec5540"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "chat_sessions",
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
            "title",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "message_count",
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
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chat_sessions_owner_id",
        "chat_sessions",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        "ix_chat_sessions_tenant_id",
        "chat_sessions",
        ["tenant_id"],
        unique=False,
    )

    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "session_id",
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
            "role",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat_sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chat_messages_owner_id",
        "chat_messages",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        "ix_chat_messages_session_id",
        "chat_messages",
        ["session_id"],
        unique=False,
    )

    op.create_index(
        "ix_chat_messages_tenant_id",
        "chat_messages",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_chat_messages_tenant_id",
        table_name="chat_messages",
    )

    op.drop_index(
        "ix_chat_messages_session_id",
        table_name="chat_messages",
    )

    op.drop_index(
        "ix_chat_messages_owner_id",
        table_name="chat_messages",
    )

    op.drop_table(
        "chat_messages",
    )

    op.drop_index(
        "ix_chat_sessions_tenant_id",
        table_name="chat_sessions",
    )

    op.drop_index(
        "ix_chat_sessions_owner_id",
        table_name="chat_sessions",
    )

    op.drop_table(
        "chat_sessions",
    )