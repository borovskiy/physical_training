from celery import Celery
from dotenv import load_dotenv

from app.core.config import settings

load_dotenv()

celery_app = Celery(
    "physical_training",
    broker=settings.AMQP_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    task_default_queue="default",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_heartbeat=30,
    broker_pool_limit=10,
    result_expires=86400,
)
