from fastapi import APIRouter
from app.schemas.embeddings import (
    EmbeddingRequest,
    EmbeddingResponse,
)
from app.services.embedding_service import generate_embedding


router = APIRouter()


@router.post("/embed", response_model=EmbeddingResponse)
async def embed(payload: EmbeddingRequest):
    embedding = await generate_embedding(
        text=payload.text,
    )

    return EmbeddingResponse(embedding=embedding)