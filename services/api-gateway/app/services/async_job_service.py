from app.db.models.async_job import AsyncJob


class AsyncJobService:

    def __init__(self, db):
        self.db = db

    def create_job(
        self,
        owner_id: str,
        tenant_id: str,
        document_id: str | None,
        job_type: str,
    ) -> AsyncJob:

        job = AsyncJob(
            owner_id=owner_id,
            tenant_id=tenant_id,
            document_id=document_id,
            job_type=job_type,
            status="QUEUED",
            retry_count=0,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_job(
        self,
        job_id: str,
    ) -> AsyncJob | None:

        return (
            self.db.query(AsyncJob)
            .filter(
                AsyncJob.id == job_id
            )
            .first()
        )

    def reset_job_for_retry(
        self,
        job_id: str,
    ) -> AsyncJob | None:

        job = (
            self.db.query(AsyncJob)
            .filter(
                AsyncJob.id == job_id
            )
            .first()
        )

        if not job:
            return None

        job.status = "QUEUED"

        job.retry_count = 0

        job.error_message = None

        job.started_at = None

        job.completed_at = None

        self.db.commit()

        self.db.refresh(job)

        return job