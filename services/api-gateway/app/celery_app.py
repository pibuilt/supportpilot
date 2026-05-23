import os

from celery import Celery


REDIS_URL = os.environ["REDIS_URL"]

celery_app = Celery(
    "supportpilot",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

import app.tasks.test_task
import app.tasks.ingestion_tasks
import app.tasks.orchestration_tasks