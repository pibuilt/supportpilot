from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse,
)
from app.services.generation_service import (
    generate_text,
    stream_generate_text,
)

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate(payload: GenerationRequest):
    output = await generate_text(
        prompt=payload.prompt,
        provider=payload.provider,
        model=payload.model,
    )

    return GenerationResponse(output=output)


@router.post("/generate/stream")
async def stream_generate(payload: GenerationRequest):
    async def generator():
        async for token in stream_generate_text(
            prompt=payload.prompt,
            provider=payload.provider,
            model=payload.model,
        ):
            yield token

    return StreamingResponse(
        generator(),
        media_type="text/plain",
    )