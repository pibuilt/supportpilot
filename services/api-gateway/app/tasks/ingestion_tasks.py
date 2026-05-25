import json
from datetime import datetime, UTC

from langsmith import traceable

from app.celery_app import celery_app
from app.db.models.async_job import AsyncJob
from app.db.session import SessionLocal
from app.services.ingestion_service import (
    IngestionService,
)


MAX_RETRIES = 3


@celery_app.task(
    bind=True,
)
@traceable(name="ingestion_job")
def process_ingestion_job(
    self,
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

        if document_id == "FAIL_TEST":
            raise Exception(
                "Simulated ingestion failure"
            )

        result = service.ingest_document(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=document_id,
            text=text,
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

            current_retry = (
                self.request.retries
            )

            job.retry_count = (
                current_retry
            )

            job.error_message = str(e)

            if (
                current_retry
                >= MAX_RETRIES
            ):
                job.status = (
                    "DEAD_LETTER"
                )

                job.completed_at = (
                    datetime.now(
                        UTC
                    )
                )

                db.commit()

                raise

            job.status = "FAILED"

            db.commit()

        raise self.retry(
            exc=e,
            countdown=(
                2
                ** self.request.retries
            ),
            max_retries=MAX_RETRIES,
        )

    finally:
        db.close()