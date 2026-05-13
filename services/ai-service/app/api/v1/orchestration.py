from fastapi import APIRouter

from app.schemas.orchestration import (
    OrchestrationRequest,
    OrchestrationResponse,
)
from app.services.orchestration_service import OrchestrationService

router = APIRouter(
    prefix="/v1/orchestrate",
    tags=["orchestration"],
)

service = OrchestrationService()


@router.post(
    "",
    response_model=OrchestrationResponse,
)
async def orchestrate(
    request: OrchestrationRequest,
):
    return await service.process(
        query=request.query,
        document_id=request.document_id,
        session_id=request.session_id,
    )