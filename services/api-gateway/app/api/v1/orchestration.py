from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.orchestration import (
    OrchestrationRequest,
    OrchestrationResponse,
)
from app.services.orchestration_service import OrchestrationService


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
    db: Session = Depends(get_db),
):
    return service.process(
        db=db,
        document_id=request.document_id,
        query=request.query,
    )