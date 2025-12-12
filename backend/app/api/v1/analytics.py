# backend/app/api/v1/analytics.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta

from ...config import settings
from ...db import get_mongo_client
from ...dependencies.auth import get_current_user
from ...models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/movies/by-genre")
async def get_movies_by_genre(
        current_user: User = Depends(get_current_user),
        days: int = Query(30, ge=1, le=365)
):
    """Analiza filmova po žanrovima za posljednjih N dana"""
    client = get_mongo_client()
    db = client[settings.MONGO_DB]

    date_threshold = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {"fetched_at": {"$gte": date_threshold}}},
        {"$unwind": "$genre_ids"},
        {"$group": {
            "_id": "$genre_ids",
            "count": {"$sum": 1},
            "avg_vote": {"$avg": "$vote_average"},
            "total_popularity": {"$sum": "$popularity"}
        }},
        {"$sort": {"count": -1}}
    ]

    results = list(db.trending_movies.aggregate(pipeline))
    return {"analysis": results}


@router.get("/movies/release-trend")
async def get_movies_release_trend(
        current_user: User = Depends(get_current_user),
        months: int = Query(12, ge=1, le=60)
):
    """Trend izlazaka filmova po mjesecima"""
    client = get_mongo_client()
    db = client[settings.MONGO_DB]

    pipeline = [
        {"$match": {"release_date": {"$ne": None}}},
        {"$addFields": {
            "release_month": {"$substr": ["$release_date", 0, 7]}  # YYYY-MM
        }},
        {"$group": {
            "_id": "$release_month",
            "count": {"$sum": 1},
            "avg_vote": {"$avg": "$vote_average"}
        }},
        {"$sort": {"_id": 1}},
        {"$limit": months}
    ]

    results = list(db.trending_movies.aggregate(pipeline))
    return {"trend": results}


@router.get("/movies/country-analysis")
async def get_movies_by_country(
        current_user: User = Depends(get_current_user)
):
    """Analiza filmova po zemljama produkcije"""
    client = get_mongo_client()
    db = client[settings.MONGO_DB]

    # Ovo je pojednostavljeno - trebali biste imati proper field za zemlje
    pipeline = [
        {"$match": {"production_countries": {"$exists": True, "$ne": []}}},
        {"$unwind": "$production_countries"},
        {"$group": {
            "_id": "$production_countries",
            "count": {"$sum": 1},
            "avg_budget": {"$avg": "$budget"},
            "avg_revenue": {"$avg": "$revenue"}
        }},
        {"$sort": {"count": -1}}
    ]

    results = list(db.trending_movies.aggregate(pipeline))
    return {"countries": results}


@router.get("/correlation/budget-vs-rating")
async def get_budget_vs_rating_correlation(
        current_user: User = Depends(get_current_user)
):
    """Korelacija između budžeta i ocjena"""
    client = get_mongo_client()
    db = client[settings.MONGO_DB]

    pipeline = [
        {"$match": {
            "budget": {"$gt": 0},
            "vote_average": {"$gt": 0}
        }},
        {"$project": {
            "title": 1,
            "budget": 1,
            "vote_average": 1,
            "revenue": 1,
            "roi": {
                "$cond": [
                    {"$gt": ["$revenue", 0]},
                    {"$divide": ["$revenue", "$budget"]},
                    0
                ]
            }
        }},
        {"$sort": {"budget": -1}},
        {"$limit": 100}
    ]

    results = list(db.trending_movies.aggregate(pipeline))
    return {"correlation_data": results}


@router.get("/combined/locations-and-films")
async def get_films_with_locations(
        current_user: User = Depends(get_current_user),
        country_code: Optional[str] = None
):
    """Kombinirana analiza filmova i lokacija"""
    # Ovo bi kombiniralo podatke iz TMDB i GeoDB
    # Za sada vraćamo pojednostavljene podatke

    client = get_mongo_client()
    db = client[settings.MONGO_DB]

    query = {}
    if country_code:
        query["production_countries"] = country_code

    movies = list(db.trending_movies.find(query).limit(20))

    # Simulacija lokacijskih podataka
    for movie in movies:
        movie["simulated_locations"] = [
            {
                "city": "Los Angeles",
                "country": "USA",
                "reason": "Primary filming location"
            },
            {
                "city": "London",
                "country": "UK",
                "reason": "Additional scenes"
            }
        ]

    return {
        "total_films": len(movies),
        "films": movies,
        "analysis": "This combines film data with geographical information"
    }