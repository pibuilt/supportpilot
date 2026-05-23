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
)
from app.services.async_job_service import (
    AsyncJobService,
)
from app.tasks.orchestration_tasks import (
    process_orchestration_job,
)


router = APIRouter(
    prefix="/v1/orchestrate",
    tags=["Orchestration"],
)


@router.post("")
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

        embedding_repo = (
            EmbeddingRepository(db)
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

    job_service = AsyncJobService(
        db
    )

    job = job_service.create_job(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=request.document_id,
        job_type="ORCHESTRATION",
    )

    process_orchestration_job.delay(
        str(job.id),
        owner_id,
        tenant_id,
        api_key,
        request.document_id,
        request.query,
        request.session_id,
        request.context_limit,
    )

    return {
        "job_id": job.id,
        "status": job.status,
    }