import os
import uuid
from sqlalchemy.orm import Session

from app.rag.chunker import chunk_text
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.embedding_service import generate_embedding


class IngestionService:
    EMBEDDING_DIMENSION = int(os.getenv("OLLAMA_EMBED_DIMENSION", "768"))
    EMBEDDING_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    EMBEDDING_VERSION = os.getenv("OLLAMA_EMBED_VERSION", "v1")

    def __init__(self, db: Session):
        self.db = db
        self.embedding_repo = EmbeddingRepository(db)

    def ingest_document(self, document_id: str, text: str):
        chunks = chunk_text(text)

        created_records = []

        try:
            for index, chunk in enumerate(chunks):
                embedding_id = str(uuid.uuid4())
                chunk_id = f"{document_id}_chunk_{index}"

                self.embedding_repo.create_embedding(
                    embedding_id=embedding_id,
                    document_id=document_id,
                    chunk_id=chunk_id,
                    chunk_text=chunk,
                    embedding_model=self.EMBEDDING_MODEL,
                    embedding_version=self.EMBEDDING_VERSION,
                    vector=generate_embedding(chunk),
                )

                created_records.append(
                    {
                        "embedding_id": embedding_id,
                        "chunk_id": chunk_id,
                        "preview": chunk[:100],
                    }
                )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return {
            "document_id": document_id,
            "chunks_created": len(created_records),
            "records": created_records,
        }