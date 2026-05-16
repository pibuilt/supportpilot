import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from app.db.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    api_key_id = Column(
        String,
        nullable=False,
    )

    tenant_id = Column(
        String,
        nullable=False,
        default="default",
    )

    endpoint = Column(
        String,
        nullable=False,
    )

    tokens_used = Column(
        Integer,
        nullable=False,
    )

    status_code = Column(
        Integer,
        nullable=False,
        default=200,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )