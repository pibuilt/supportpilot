from fastapi import APIRouter

from app.schemas.orchestration import (
    OrchestrationRequest,
    OrchestrationResponse,
)
from app.services.orchestration_service import (
    OrchestrationService,
)


router = APIRouter(
    prefix="/v1/orchestrate",
    tags=["Orchestration"],
)

service = OrchestrationService()


@router.post(
    "",
    response_model=OrchestrationResponse,
)
def orchestrate(
    request: OrchestrationRequest,
):
    return service.process(
        document_id=request.document_id,
        query=request.query,
        session_id=request.session_id,
        context_limit=request.context_limit,
    )