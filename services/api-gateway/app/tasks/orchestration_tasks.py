import json
from datetime import datetime, UTC

from langsmith import traceable

from app.celery_app import celery_app
from app.db.models.async_job import AsyncJob
from app.db.session import SessionLocal

from app.repositories.chat_message_repository import (
    ChatMessageRepository,
)

from app.repositories.chat_session_repository import (
    ChatSessionRepository,
)

from app.services.orchestration_service import (
    OrchestrationService,
)


MAX_RETRIES = 3


@celery_app.task(
    bind=True,
)
@traceable(name="orchestration_job")
def process_orchestration_job(
    self,
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

        session_repo = (
            ChatSessionRepository(db)
        )

        message_repo = (
            ChatMessageRepository(db)
        )

        actual_session_id = result[
            "session_id"
        ]

        session_repo.get_or_create(
            session_id=actual_session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )

        message_repo.create(
            session_id=actual_session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            role="user",
            content=query,
        )

        assistant_response = (
            result["tone"][
                "final_response"
            ]
        )

        message_repo.create(
            session_id=actual_session_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            role="assistant",
            content=assistant_response,
        )

        session_repo.increment_message_count(
            actual_session_id
        )

        session_repo.increment_message_count(
            actual_session_id
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

            job.error_message = str(
                e
            )

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