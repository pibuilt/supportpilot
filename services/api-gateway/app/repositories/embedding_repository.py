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
        chunk_text: str,
        embedding_model: str,
        embedding_version: str,
        vector: list[float],
    ) -> Embedding:
        embedding = Embedding(
            id=embedding_id,
            document_id=document_id,
            chunk_id=chunk_id,
            chunk_text=chunk_text,
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
        document_id: str | None = None,
    ):
        query = self.db.query(
            Embedding.document_id,
            Embedding.chunk_id,
            Embedding.chunk_text,
            Embedding.embedding.cosine_distance(query_vector).label("distance"),
        )

        if document_id:
            query = query.filter(
                Embedding.document_id == document_id
            )

        results = (
            query.order_by(
                Embedding.embedding.cosine_distance(query_vector)
            )
            .limit(limit)
            .all()
        )

        formatted_results = []

        for row in results:
            semantic_score = 1 - float(row.distance)

            formatted_results.append(
                {
                    "document_id": row.document_id,
                    "chunk_id": row.chunk_id,
                    "chunk_text": row.chunk_text,
                    "score": semantic_score,
                    "preview": (
                        row.chunk_text[:120]
                        if row.chunk_text
                        else row.chunk_id
                    ),
                }
            )

        return formatted_results