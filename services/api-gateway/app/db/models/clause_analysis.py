from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, func
from app.db.base import Base


class ClauseAnalysis(Base):
    __tablename__ = "clause_analyses"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(String, nullable=False, index=True, default="system")
    tenant_id = Column(String, nullable=False, index=True, default="system")

    document_id = Column(String, nullable=False, index=True)
    chunk_id = Column(String, nullable=False, index=True)

    clause_type = Column(String, nullable=False, index=True)
    matched_text = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)

    analysis_metadata = Column("metadata", JSON, nullable=False)

    schema_version = Column(String, nullable=False, default="v1")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )