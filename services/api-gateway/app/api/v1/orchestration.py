from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.embedding_repository import (
    EmbeddingRepository,
)
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
    raw_request: Request,
    db: Session = Depends(get_db),
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

    api_key = raw_request.headers.get(
        "x-api-key"
    )

    if request.document_id:
        embedding_repo = EmbeddingRepository(
            db
        )

        if not embedding_repo.document_exists_for_owner(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=request.document_id,
        ):
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

    return service.process(
        owner_id=owner_id,
        tenant_id=tenant_id,
        api_key=api_key,

        document_id=request.document_id,
        query=request.query,

        session_id=request.session_id,
        context_limit=request.context_limit,
    )
