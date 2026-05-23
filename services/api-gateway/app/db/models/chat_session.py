import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
)

from sqlalchemy.sql import func

from app.db.base import Base


class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
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

    title = Column(
        String,
        nullable=True,
    )

    message_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )