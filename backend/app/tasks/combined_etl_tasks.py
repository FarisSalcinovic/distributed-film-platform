# backend/app/tasks/combined_etl_tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def scheduled_daily_etl():
    """Dnevni ETL pipeline koji se automatski pokreće"""
    try:
        logger.info("Starting scheduled daily ETL pipeline")

        # Import here to avoid circular imports
        from .etl_tasks import run_combined_etl

        result = run_combined_etl.delay()

        return {
            "status": "scheduled",
            "message": "Daily ETL pipeline scheduled",
            "task_id": result.id
        }
    except Exception as e:
        logger.error(f"Error scheduling daily ETL: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def scheduled_weekly_etl():
    """Nedeljni ETL pipeline za kompletnu sinhronizaciju"""
    try:
        logger.info("Starting scheduled weekly ETL pipeline")

        # Import here to avoid circular imports
        from .etl_tasks import fetch_and_store_films, fetch_and_store_cities

        # Fetch more data weekly
        films_task = fetch_and_store_films.delay(pages=10, movies_per_page=30)
        cities_task = fetch_and_store_cities.delay(limit=200)

        return {
            "status": "scheduled",
            "message": "Weekly ETL pipeline scheduled",
            "task_ids": {
                "films": films_task.id,
                "cities": cities_task.id
            }
        }
    except Exception as e:
        logger.error(f"Error scheduling weekly ETL: {e}")
        return {"status": "error", "message": str(e)}