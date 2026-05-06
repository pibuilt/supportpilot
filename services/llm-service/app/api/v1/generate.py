from fastapi import APIRouter

from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse
)

from app.services.generation_service import generate_text


router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerationResponse
)
async def generate(payload: GenerationRequest):

    output = await generate_text(
        system_prompt=payload.system_prompt,
        user_prompt=payload.user_prompt,
        provider=payload.provider,
        model=payload.model,
        temperature=payload.temperature
    )

    return GenerationResponse(output=output)