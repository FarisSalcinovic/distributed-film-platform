# backend/app/tasks/__init__.py
from .celery_app import celery_app
from .etl_tasks import (
    fetch_and_store_films,
    fetch_and_store_places,  # ISPRAVLJENO: umesto fetch_and_store_cities
    enrich_films_with_places,
    test_api_connections,
    run_combined_etl,
    cleanup_old_data,
    generate_daily_report
)

# Ostavite ovo za celery
__all__ = [
    'celery_app',
    'fetch_and_store_films',
    'fetch_and_store_places',  # ISPRAVLJENO
    'enrich_films_with_places',
    'test_api_connections',
    'run_combined_etl',
    'cleanup_old_data',
    'generate_daily_report'
]