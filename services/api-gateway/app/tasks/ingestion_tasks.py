from datetime import datetime, UTC

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.async_job import AsyncJob
from app.services.ingestion_service import (
    IngestionService,
)


@celery_app.task
def process_ingestion_job(
    job_id: str,
    owner_id: str,
    tenant_id: str,
    document_id: str,
    text: str,
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
            print(
                f"JOB NOT FOUND: {job_id}"
            )
            return

        job.status = "PROCESSING"
        job.started_at = datetime.now(
            UTC
        )

        db.commit()

        service = IngestionService(db)

        service.ingest_document(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=document_id,
            text=text,
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