from fastapi import APIRouter

from app.schemas.embeddings import (
    EmbeddingRequest,
    EmbeddingResponse
)

from app.services.embedding_service import generate_embedding


router = APIRouter()


@router.post(
    "/embeddings",
    response_model=EmbeddingResponse
)
async def embeddings(payload: EmbeddingRequest):

    embedding = await generate_embedding(
        text=payload.text,
        provider=payload.provider,
        model=payload.model
    )

    return EmbeddingResponse(embedding=embedding)