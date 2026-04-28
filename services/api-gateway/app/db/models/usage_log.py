import uuid
from sqlalchemy import Column, String, Integer
from app.db.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)