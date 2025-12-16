# backend/app/tasks/celery_app.py
from celery import Celery
from sqlalchemy.util.concurrency import asyncio

from .etl_tasks import run_tmdb_etl_task
from ..config import settings

# Koristi environment varijable iz settings
celery_app = Celery(
    "film_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.etl_tasks",
        "app.tasks.combined_etl_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "daily-etl-pipeline": {
        "task": "app.tasks.combined_etl_tasks.scheduled_daily_etl",
        "schedule": 86400.0,  # Every 24 hours
    },
    "weekly-etl-pipeline": {
        "task": "app.tasks.combined_etl_tasks.scheduled_weekly_etl",
        "schedule": 604800.0,  # Every 7 days
    },
}


@celery_app.task
def scheduled_tmdb_etl():
    """Scheduled task za TMDB ETL (pokreće se svaki dan u 2 AM)"""
    try:
        # Pokreni asyncio task
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_tmdb_etl_task())
        return result
    except Exception as e:
        print(f"Scheduled task failed: {e}")
        return {"status": "failed", "error": str(e)}