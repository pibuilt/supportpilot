from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatCompletionRequest
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/v1/chat",
    tags=["chat"],
)

service = ChatService()


@router.post("/completions/stream")
async def stream_chat_completions(
    request: ChatCompletionRequest,
):
    generator = service.stream_process(
        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
    )