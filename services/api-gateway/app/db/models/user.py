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


class User(
    Base
):
    __tablename__ = (
        "users"
    )

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(
            uuid.uuid4()
        ),
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String,
        nullable=False,
    )

    full_name = Column(
        String,
        nullable=False,
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
        index=True,
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