from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import (
    StreamingResponse,
)

from app.schemas.chat import (
    ChatCompletionRequest,
)
from app.services.chat_service import (
    ChatService,
)

router = APIRouter(
    prefix="/v1/chat",
    tags=["chat"],
)

service = ChatService()


@router.post(
    "/completions/stream"
)
async def stream_chat_completions(
    request: ChatCompletionRequest,
    raw_request: Request,
):
    owner_id = getattr(
        raw_request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        raw_request.state,
        "tenant_id",
        None,
    )

    api_key = getattr(
        raw_request.state,
        "api_key",
        None,
    )

    generator = (
        service.stream_process(
            owner_id=owner_id,
            tenant_id=tenant_id,
            api_key=api_key,

            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            session_id=request.session_id,
        )
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
    )