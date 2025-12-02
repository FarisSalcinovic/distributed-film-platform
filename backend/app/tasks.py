# backend/app/tasks.py
from celery import Celery
import os

# Koristimo CELERY_BROKER_URL iz environment varijable
celery_app = Celery('app', broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

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