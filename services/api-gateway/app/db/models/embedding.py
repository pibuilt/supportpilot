import uuid
from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, nullable=False)
    chunk_id = Column(String, nullable=False)

    chunk_text = Column(Text, nullable=True)

    embedding_model = Column(String, nullable=False)
    embedding_version = Column(String, nullable=False)

    embedding = Column(Vector(768), nullable=False)