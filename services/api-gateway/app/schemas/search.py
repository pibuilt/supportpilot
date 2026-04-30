from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    semantic_score: float
    keyword_score: float
    rerank_score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]