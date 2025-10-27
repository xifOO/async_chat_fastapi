from celery import Celery

from app.config import settings

redis_url = f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db}"

celery_app = Celery("celery_worker", broker_url=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    enable_utc=True,
    timezone="Europe/Moscow",
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "kafka-to-mongo-task": {
        "task": "app.tasks.run_kafka_to_mongo",
        "schedule": settings.celery.INTERVAL_SERVICE_TIME,
        "options": {
            "expires": settings.celery.INTERVAL_SERVICE_TIME - 1,
            "queue": "default",
        },
    },
    "redis-to-kafka-task": {
        "task": "app.tasks.run_redis_to_kafka",
        "schedule": settings.celery.INTERVAL_SERVICE_TIME,
        "options": {
            "expires": settings.celery.INTERVAL_SERVICE_TIME - 1,
            "queue": "default",
        },
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
