from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingestion import (
    DocumentIngestRequest,
)
from app.services.async_job_service import (
    AsyncJobService,
)
from app.tasks.ingestion_tasks import (
    process_ingestion_job,
)
from app.utils.response import (
    success_response,
)

router = APIRouter()


@router.post("/ingest")
def ingest_document(
    payload: DocumentIngestRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_id = getattr(
        request.state,
        "owner",
        None,
    )

    tenant_id = getattr(
        request.state,
        "tenant_id",
        None,
    )

    job_service = AsyncJobService(db)

    job = job_service.create_job(
        owner_id=owner_id,
        tenant_id=tenant_id,
        document_id=payload.document_id,
        job_type="DOCUMENT_INGESTION",
    )

    process_ingestion_job.delay(
        str(job.id),
        owner_id,
        tenant_id,
        payload.document_id,
        payload.text,
    )

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    return success_response(
        {
            "job_id": job.id,
            "status": job.status,
        },
        request_id,
    )