from app.celery_app import celery_app


@celery_app.task
def ping():

    print(
        "PING TASK EXECUTED"
    )

    return "pong"