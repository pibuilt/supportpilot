import uuid
from sqlalchemy import Column, String, Text
from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, nullable=False)
    ticket_text = Column(Text, nullable=False)