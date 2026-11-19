"""
Celery Application for Sailight
Background task processing (e.g., plan generation, reports)
"""

from celery import Celery
from app.config import settings

# Celery configuration
celery_app = Celery(
    'sailight_tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Luxembourg',
    enable_utc=True,
)

# Import tasks to register them
from app import tasks  # noqa: F401
