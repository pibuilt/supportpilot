from fastapi import APIRouter

from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/v1/chat",
    tags=["chat"],
)

service = ChatService()


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
)
async def chat_completions(
    request: ChatCompletionRequest,
):
    return await service.process(
        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )