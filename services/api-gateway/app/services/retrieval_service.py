from app.repositories.embedding_repository import EmbeddingRepository
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_results


def search_documents(db, query: str, top_k: int = 5):
    repository = EmbeddingRepository(db)

    candidate_k = max(top_k * 3, 15)

    query_vector = generate_embedding(query)

    semantic_results = repository.search_similar_embeddings(
        query_vector=query_vector,
        limit=candidate_k,
    )

    reranked_results = rerank_results(query, semantic_results)

    return reranked_results[:top_k]