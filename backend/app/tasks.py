# backend/app/tasks.py
from celery import Celery
from .config import settings

celery_app = Celery('app', broker=settings.CELERY_BROKER_URL)

# Opcionalno: konfiguracija Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def example_task():
    """Primjer zadatka"""
    return "Task executed successfully"