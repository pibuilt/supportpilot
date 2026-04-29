from sqlalchemy.orm import Session

from app.db.models.embedding import Embedding


class EmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_embedding(
        self,
        embedding_id: str,
        document_id: str,
        chunk_id: str,
        embedding_model: str,
        embedding_version: str,
        vector: list[float],
    ) -> Embedding:
        embedding = Embedding(
            id=embedding_id,
            document_id=document_id,
            chunk_id=chunk_id,
            embedding_model=embedding_model,
            embedding_version=embedding_version,
            embedding=vector,
        )

        self.db.add(embedding)

        return embedding

    def search_similar_embeddings(
        self,
        query_vector: list[float],
        limit: int = 5,
    ):
        return (
            self.db.query(
                Embedding.document_id,
                Embedding.chunk_id,
                Embedding.embedding.cosine_distance(query_vector).label("distance"),
            )
            .order_by(Embedding.embedding.cosine_distance(query_vector))
            .limit(limit)
            .all()
        )