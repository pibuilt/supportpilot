import json
from datetime import datetime, UTC

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.async_job import AsyncJob
from app.services.orchestration_service import (
    OrchestrationService,
)


@celery_app.task
def process_orchestration_job(
    job_id: str,
    owner_id: str,
    tenant_id: str,
    api_key: str,
    document_id: str | None,
    query: str,
    session_id: str | None,
    context_limit: int,
):
    db = SessionLocal()

    try:

        job = (
            db.query(AsyncJob)
            .filter(
                AsyncJob.id == job_id
            )
            .first()
        )

        if not job:
            return

        job.status = "PROCESSING"
        job.started_at = datetime.now(
            UTC
        )

        db.commit()

        service = OrchestrationService()

        result = service.process(
            owner_id=owner_id,
            tenant_id=tenant_id,
            api_key=api_key,
            document_id=document_id,
            query=query,
            session_id=session_id,
            context_limit=context_limit,
        )

        job.result_json = json.dumps(
            result
        )

        job.status = "COMPLETED"
        job.completed_at = datetime.now(
            UTC
        )

        db.commit()

        return {
            "job_id": job_id,
            "status": "COMPLETED",
        }

    except Exception as e:

        db.rollback()

        job = (
            db.query(AsyncJob)
            .filter(
                AsyncJob.id == job_id
            )
            .first()
        )

        if job:
            job.status = "FAILED"
            job.error_message = str(e)

            db.commit()

        raise

    finally:
        db.close()