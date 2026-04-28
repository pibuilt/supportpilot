import uuid
from sqlalchemy import Column, String
from app.db.base import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_prefix = Column(String, nullable=False)
    hashed_key = Column(String, nullable=False)
    owner = Column(String, nullable=False)