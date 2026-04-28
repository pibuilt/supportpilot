import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)