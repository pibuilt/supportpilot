import json
import asyncio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import StreamingResponse

from app.db.session import get_db
from app.db.session import SessionLocal
from app.services.async_job_service import (
    AsyncJobService,
)

router = APIRouter()
TERMINAL_STATUSES = {
    "COMPLETED",
    "FAILED",
    "DEAD_LETTER",
}


def serialize_job(job):
    result = None

    if job.result_json:
        try:
            result = json.loads(
                job.result_json
            )
        except Exception:
            result = job.result_json

    return {
        "job_id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "retry_count": job.retry_count,
        "error_message": job.error_message,
        "result": result,
        "started_at": job.started_at.isoformat()
        if job.started_at
        else None,
        "completed_at": job.completed_at.isoformat()
        if job.completed_at
        else None,
    }


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

    return serialize_job(job)


@router.get("/jobs/{job_id}/stream")
async def stream_job_status(
    job_id: str,
    request: Request,
):
    async def event_generator():
        last_payload = None

        while True:
            if await request.is_disconnected():
                break

            db = SessionLocal()
            try:
                service = AsyncJobService(db)
                job = service.get_job(job_id)
                if not job:
                    yield (
                        "event: error\n"
                        "data: "
                        + json.dumps(
                            {"detail": "Job not found"}
                        )
                        + "\n\n"
                    )
                    break

                payload = serialize_job(job)
                encoded = json.dumps(payload)

                if encoded != last_payload:
                    yield (
                        "event: job\n"
                        "data: "
                        + encoded
                        + "\n\n"
                    )
                    last_payload = encoded

                if job.status in TERMINAL_STATUSES:
                    break
            finally:
                db.close()

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
