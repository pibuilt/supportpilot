import uuid
from datetime import (
    datetime,
)

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
)

from app.db.base import Base


class APIKey(
    Base
):
    __tablename__ = (
        "api_keys"
    )

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(
            uuid.uuid4()
        ),
    )

    key_prefix = Column(
        String,
        nullable=False,
    )

    hashed_key = Column(
        String,
        nullable=False,
    )

    # Legacy compatibility
    owner = Column(
        String,
        nullable=False,
        index=True,
    )

    # Stable identity
    user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    role = Column(
        String,
        nullable=False,
        default="user",
    )

    tenant_id = Column(
        String,
        nullable=False,
        default="default",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )