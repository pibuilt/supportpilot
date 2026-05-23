import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
)

from sqlalchemy.sql import func

from app.db.base import Base


class AsyncJob(Base):

    __tablename__ = "async_jobs"

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

    document_id = Column(
        String,
        nullable=True,
        index=True,
    )

    job_type = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="QUEUED",
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    result_json = Column(
        Text,
        nullable=True,
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )