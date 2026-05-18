from fastapi import (
    APIRouter,
    Request,
)

from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
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
    "/completions",
    response_model=ChatCompletionResponse,
)
async def chat_completions(
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

    return await service.process(
        owner_id=owner_id,
        tenant_id=tenant_id,
        api_key=api_key,

        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        session_id=request.session_id,
    )