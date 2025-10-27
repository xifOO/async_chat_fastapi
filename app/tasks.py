import asyncio
from app.kafka.services.mongo import KafkaToMongoDB
from app.kafka.services.redis import RedisToKafkaService
from app.worker import celery_app
from app.config import settings


@celery_app.task(
    bind=True,
    name='app.tasks.run_kafka_to_mongo',
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=settings.celery.TASK_SOFT_TIME_LIMIT,
    time_limit=settings.celery.TASK_TIME_LIMIT,
    acks_late=True
)
def run_kafka_to_mongo(self):
    async def _run():
        service = KafkaToMongoDB(
            topic="chat-messages", 
            headers=[
                ("source", b"kafka"),
                ("service", b"kafka-to-mongo"),
                ("version", b"1.0"),
            ]
        )
        batches = 0

        try:
            await service.start()

            max_batches = settings.celery.MAX_BATCHES

            for _ in range(max_batches):
                await service.process()

                batches += 1
            
            return {
                "status": "success",
                "batches": batches,
                "service": "kafka-to-mongo"
            }
        
        except Exception as e:
            raise self.retry(exc=e, countdown=min(60 * (2 ** self.request.retries), 300))
        finally:
            await service.stop()

    return asyncio.run(_run())


@celery_app.task(
    bind=True,
    name='app.tasks.run_redis_to_kafka',
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=settings.celery.TASK_SOFT_TIME_LIMIT,
    time_limit=settings.celery.TASK_TIME_LIMIT,
    acks_late=True,
)
def run_redis_to_kafka(self):
    async def _run():
        service = RedisToKafkaService(topic="chat-messages", headers=[
            ("source", b"redis"),
            ("service", b"redis-to-kafka"),
            ("version", b"1.0"),
        ])
        iterations = 0

        try:
            await service.start()
            for _ in range(settings.celery.MAX_ITERATIONS):
                await service.process()
                iterations += 1

            return {
                "status": "success",
                "iterations": iterations,
                "service": "redis-to-kafka"
            }
        except Exception as e:
            raise self.retry(exc=e, countdown=min(60 * (2 ** self.request.retries), 300))
        finally:
            await service.stop()

    asyncio.run(_run())