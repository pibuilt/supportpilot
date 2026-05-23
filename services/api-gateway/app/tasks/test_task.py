from app.celery_app import celery_app


@celery_app.task
def ping(
    job_id: str,
):

    print(
        f"PROCESSING JOB {job_id}"
    )

    return {
        "job_id": job_id,
        "status": "COMPLETED",
    }