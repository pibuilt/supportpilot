from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    text: str

    provider: str = "ollama"
    model: str = "nomic-embed-text"


class EmbeddingResponse(BaseModel):
    embedding: list[float]