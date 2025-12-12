# backend/app/tasks/celery_app.py
from celery import Celery
from ..config import settings

celery_app = Celery(
    'film_platform',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BROKER_URL  # Using same Redis for results
)

# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,

    # Beat schedule for periodic tasks
    beat_schedule={
        'daily-trending-movies': {
            'task': 'app.tasks.etl_tasks.fetch_trending_movies',
            'schedule': 86400.0,  # Every 24 hours
            'args': ('day', 50),
        },
        'weekly-trending-movies': {
            'task': 'app.tasks.etl_tasks.fetch_trending_movies',
            'schedule': 604800.0,  # Every week
            'args': ('week', 100),
        },
        'daily-etl-pipeline': {
            'task': 'app.tasks.etl_tasks.daily_etl_pipeline',
            'schedule': 86400.0,  # Every 24 hours
        },
        'enrich-movies-weekly': {
            'task': 'app.tasks.etl_tasks.enrich_movies_with_locations',
            'schedule': 604800.0,  # Every week
        },
    }
)

# Import tasks to ensure they're registered
from . import etl_tasks