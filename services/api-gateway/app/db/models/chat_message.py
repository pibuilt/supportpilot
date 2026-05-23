import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from app.db.base import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    session_id = Column(
        String,
        ForeignKey("chat_sessions.id"),
        nullable=False,
        index=True,
    )

    owner_id = Column(
        String,
        nullable=False,
        index=True,
    )

    tenant_id = Column(
        String,
        nullable=False,
        index=True,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )