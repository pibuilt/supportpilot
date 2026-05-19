from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_id = Column(
        String,
        nullable=False,
        index=True,
    )

    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    api_key_id = Column(
        String,
        ForeignKey(
            "api_keys.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    event_type = Column(
        String,
        nullable=False,
        index=True,
    )

    resource_type = Column(
        String,
        nullable=True,
    )

    resource_id = Column(
        String,
        nullable=True,
    )

    action = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="success",
    )

    ip_address = Column(
        String,
        nullable=True,
    )

    user_agent = Column(
        String,
        nullable=True,
    )

    event_metadata = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_tenant_event",
            "tenant_id",
            "event_type",
        ),
    )