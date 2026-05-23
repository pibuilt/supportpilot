from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.db.session import get_db
from app.services.async_job_service import (
    AsyncJobService,
)

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    db=Depends(get_db),
):
    service = AsyncJobService(db)

    job = service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }