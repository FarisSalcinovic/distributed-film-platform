# backend/app/api/v1/etl.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from ...config import settings
from ...db import get_mongo_client
from ...tasks.etl_tasks import fetch_trending_movies
from ...dependencies.auth import require_admin

router = APIRouter(prefix="/etl", tags=["ETL Operations"])


@router.post("/trending-movies/run")
async def run_trending_movies_etl(
        background_tasks: BackgroundTasks,
        admin: bool = Depends(require_admin)
):
    """Pokreće ETL za trending filmove"""
    background_tasks.add_task(fetch_trending_movies)
    return {"message": "ETL job started for trending movies"}


@router.get("/trending-movies/results")
async def get_trending_movies_results(admin: bool = Depends(require_admin)):
    """Dohvata rezultate posljednjeg ETL-a za trending filmove"""
    client = get_mongo_client()
    if not client:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    db = client[settings.MONGO_DB]
    collection = db["trending_movies"]

    # Dohvati posljednje filmove
    results = list(collection.find().sort("fetched_at", -1).limit(50))

    return {"count": len(results), "movies": results}