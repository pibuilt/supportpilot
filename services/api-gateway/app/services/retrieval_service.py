from app.repositories.embedding_repository import EmbeddingRepository
from app.services.embedding_service import generate_fake_embedding


def search_documents(db, query: str, top_k: int = 5):
    repository = EmbeddingRepository(db)

    query_vector = generate_fake_embedding(query)

    return repository.search_similar_embeddings(
        query_vector=query_vector,
        limit=top_k,
    )