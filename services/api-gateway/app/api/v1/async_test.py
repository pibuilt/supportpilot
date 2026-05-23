from fastapi import APIRouter
from fastapi import Depends

from app.db.session import get_db
from app.services.async_job_service import AsyncJobService
from app.tasks.ingestion_tasks import (
    process_ingestion_job,
)

router = APIRouter()


@router.post("/test-async")
def test_async(
    db=Depends(get_db),
):

    service = AsyncJobService(db)

    job = service.create_job(
        owner_id="system",
        tenant_id="system",
        document_id=None,
        job_type="TEST",
    )

    process_ingestion_job.delay(
        str(job.id)
    )

    return {
        "job_id": job.id,
        "status": job.status,
    }