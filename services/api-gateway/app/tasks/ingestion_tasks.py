from app.celery_app import celery_app


@celery_app.task
def process_ingestion_job(
    job_id: str,
):

    print(
        f"PROCESSING INGESTION JOB {job_id}"
    )

    return {
        "job_id": job_id,
    }