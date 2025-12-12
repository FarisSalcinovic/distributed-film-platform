# backend/app/tasks/__init__.py
from .celery_app import celery_app
from .etl_tasks import (
    fetch_trending_movies,
    fetch_movie_details,
    fetch_geographical_data,
    daily_etl_pipeline,
    enrich_movies_with_locations
)

__all__ = [
    'celery_app',
    'fetch_trending_movies',
    'fetch_movie_details',
    'fetch_geographical_data',
    'daily_etl_pipeline',
    'enrich_movies_with_locations'
]