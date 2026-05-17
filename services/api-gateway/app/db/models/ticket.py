import uuid
from app.db.base import Base
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    owner_id = Column(String, nullable=False, index=True, default="system")
    tenant_id = Column(String, nullable=False, index=True, default="system")

    status = Column(String, nullable=False)
    ticket_text = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    category = Column(String, nullable=False, default="general")
    priority = Column(String, nullable=False, default="low")