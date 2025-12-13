# backend/app/api/v1/film_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ...db import get_mongo_client
from ...config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/films/locations", tags=["Analytics"])
async def get_films_with_locations(
        limit: int = Query(50, ge=1, le=1000),
        skip: int = Query(0, ge=0),
        country: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None
):
    """
    Vraća filmove sa lokacijama sa filterima
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        films_collection = db["films"]
        locations_collection = db["film_locations"]

        # Build filter
        filter_query = {}
        if country:
            filter_query["production_countries"] = {"$regex": country, "$options": "i"}
        if genre:
            filter_query["genres"] = {"$regex": genre, "$options": "i"}
        if year:
            filter_query["release_date"] = {"$regex": f"^{year}"}

        # Get films - DODAJ AWAIT!
        films_cursor = films_collection.find(
            filter_query,
            {"_id": 0, "film_id": 1, "title": 1, "release_date": 1, "genres": 1,
             "production_countries": 1, "popularity": 1, "vote_average": 1}
        ).sort("popularity", -1).skip(skip).limit(limit)

        films = await films_cursor.to_list(length=limit)

        # Get locations for each film
        for film in films:
            film_id = film.get("film_id")
            locations_cursor = locations_collection.find(
                {"film_id": film_id},
                {"_id": 0, "city_name": 1, "country": 1, "latitude": 1, "longitude": 1, "confidence": 1}
            ).limit(5)
            locations = await locations_cursor.to_list(length=5)
            film["locations"] = locations
            film["locations_count"] = len(locations)

        return {
            "total": len(films),
            "limit": limit,
            "skip": skip,
            "filters": {
                "country": country,
                "genre": genre,
                "year": year
            },
            "films": films
        }

    except Exception as e:
        logger.error(f"Error getting films with locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/films/trending", tags=["Analytics"])
async def get_trending_films(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(20, ge=1, le=100)
):
    """
    Vraća trenutno popularne filmove (basirano na popularity score)
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        films_collection = db["films"]

        # Calculate date threshold
        threshold_date = datetime.utcnow() - timedelta(days=days)

        # Get trending films - DODAJ AWAIT!
        films_cursor = films_collection.find(
            {
                "$or": [
                    {"fetched_at": {"$gte": threshold_date}},
                    {"release_date": {"$regex": f"^{datetime.now().year}"}}
                ]
            },
            {"_id": 0, "film_id": 1, "title": 1, "release_date": 1, "overview": 1,
             "popularity": 1, "vote_average": 1, "vote_count": 1, "genres": 1}
        ).sort([("popularity", -1), ("vote_average", -1)]).limit(limit)

        films = await films_cursor.to_list(length=limit)

        # Calculate trending score
        for film in films:
            popularity = film.get("popularity", 0)
            vote_avg = film.get("vote_average", 0)
            vote_count = film.get("vote_count", 0)

            # Simple trending algorithm
            trending_score = (popularity * 0.5) + (vote_avg * 20 * 0.3) + (min(vote_count, 1000) / 1000 * 0.2)
            film["trending_score"] = round(trending_score, 2)

        # Sort by trending score
        films.sort(key=lambda x: x.get("trending_score", 0), reverse=True)

        return {
            "period_days": days,
            "total": len(films),
            "films": films[:limit]
        }

    except Exception as e:
        logger.error(f"Error getting trending films: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities/popular", tags=["Analytics"])
async def get_popular_cities(
        limit: int = Query(20, ge=1, le=100),
        min_population: int = Query(100000, ge=0),
        country_code: Optional[str] = None
):
    """
    Vraća popularne gradove za filmsku produkciju
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        cities_collection = db["cities"]
        locations_collection = db["film_locations"]

        # Build filter
        filter_query = {"population": {"$gte": min_population}}
        if country_code:
            filter_query["country_code"] = country_code.upper()

        # Get popular cities - DODAJ AWAIT!
        cities_cursor = cities_collection.find(
            filter_query,
            {"_id": 0, "city_id": 1, "name": 1, "country": 1, "country_code": 1,
             "population": 1, "latitude": 1, "longitude": 1}
        ).sort("population", -1).limit(limit)

        cities = await cities_cursor.to_list(length=limit)

        # Get film count for each city
        for city in cities:
            city_id = city.get("city_id")
            film_count = await locations_collection.count_documents({"city_id": city_id})
            city["film_count"] = film_count

            # Get sample films
            sample_films_cursor = locations_collection.find(
                {"city_id": city_id},
                {"_id": 0, "film_id": 1, "film_title": 1}
            ).limit(3)
            sample_films = await sample_films_cursor.to_list(length=3)
            city["sample_films"] = [film.get("film_title") for film in sample_films if film.get("film_title")]

        # Sort by film count (most film-friendly cities first)
        cities.sort(key=lambda x: x.get("film_count", 0), reverse=True)

        return {
            "total": len(cities),
            "min_population": min_population,
            "country_filter": country_code,
            "cities": cities
        }

    except Exception as e:
        logger.error(f"Error getting popular cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/films-by-country", tags=["Analytics"])
async def get_films_by_country():
    """
    Analiza filmova po zemljama produkcije
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        films_collection = db["films"]

        # Aggregate films by country - DODAJ AWAIT!
        pipeline = [
            {"$unwind": "$production_countries"},
            {"$group": {
                "_id": "$production_countries",
                "film_count": {"$sum": 1},
                "avg_popularity": {"$avg": "$popularity"},
                "avg_vote": {"$avg": "$vote_average"},
                "total_votes": {"$sum": "$vote_count"},
                "sample_films": {"$push": {"title": "$title", "popularity": "$popularity"}}
            }},
            {"$sort": {"film_count": -1}},
            {"$limit": 20},
            {"$project": {
                "_id": 0,
                "country": "$_id",
                "film_count": 1,
                "avg_popularity": {"$round": ["$avg_popularity", 2]},
                "avg_vote": {"$round": ["$avg_vote", 2]},
                "total_votes": 1,
                "sample_films": {"$slice": ["$sample_films", 3]}
            }}
        ]

        results_cursor = films_collection.aggregate(pipeline)
        results = await results_cursor.to_list(length=20)

        # Get total stats - DODAJ AWAIT!
        total_films = await films_collection.count_documents({})

        return {
            "total_films": total_films,
            "countries_analyzed": len(results),
            "data": results
        }

    except Exception as e:
        logger.error(f"Error analyzing films by country: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/cities-near-films", tags=["Analytics"])
async def get_cities_near_film_locations(
        radius_km: int = Query(100, ge=10, le=500),
        limit: int = Query(20, ge=1, le=100)
):
    """
    Pronalazi gradove u blizini filmskih lokacija
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        locations_collection = db["film_locations"]
        cities_collection = db["cities"]

        # Get unique film locations - DODAJ AWAIT!
        pipeline = [
            {"$group": {
                "_id": {"city_id": "$city_id", "city_name": "$city_name"},
                "film_count": {"$sum": 1},
                "latitude": {"$first": "$latitude"},
                "longitude": {"$first": "$longitude"},
                "sample_films": {"$push": "$film_title"}
            }},
            {"$limit": 50}
        ]

        unique_locations_cursor = locations_collection.aggregate(pipeline)
        unique_locations = await unique_locations_cursor.to_list(length=50)

        nearby_cities = []

        for loc in unique_locations:
            if not loc.get("latitude") or not loc.get("longitude"):
                continue

            lat = loc["latitude"]
            lng = loc["longitude"]

            # Find cities within radius - DODAJ AWAIT!
            nearby_cursor = cities_collection.find({
                "latitude": {"$gte": lat - (radius_km / 111), "$lte": lat + (radius_km / 111)},
                "longitude": {"$gte": lng - (radius_km / (111 * abs(lat))),
                              "$lte": lng + (radius_km / (111 * abs(lat)))},
                "city_id": {"$ne": loc["_id"]["city_id"]}
            }, {
                "_id": 0, "city_id": 1, "name": 1, "country": 1,
                "population": 1, "latitude": 1, "longitude": 1
            }).limit(5)

            nearby = await nearby_cursor.to_list(length=5)

            for city in nearby:
                # Calculate approximate distance
                distance = ((city["latitude"] - lat) ** 2 + (city["longitude"] - lng) ** 2) ** 0.5 * 111
                if distance <= radius_km:
                    nearby_cities.append({
                        **city,
                        "distance_km": round(distance, 1),
                        "near_film_location": loc["_id"]["city_name"],
                        "film_count_at_location": loc["film_count"],
                        "sample_films": loc["sample_films"][:2]
                    })

        # Remove duplicates and sort
        unique_nearby = {}
        for city in nearby_cities:
            key = f"{city['city_id']}_{city['near_film_location']}"
            if key not in unique_nearby:
                unique_nearby[key] = city

        result = sorted(unique_nearby.values(), key=lambda x: x["distance_km"])[:limit]

        return {
            "radius_km": radius_km,
            "locations_analyzed": len(unique_locations),
            "nearby_cities_found": len(result),
            "cities": result
        }

    except Exception as e:
        logger.error(f"Error finding cities near film locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/stats", tags=["Analytics"])
async def get_analytics_stats():
    """
    Osnovne statistike platforme
    """
    try:
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]

        # Count documents - SVI DODAJ AWAIT!
        film_count = await db["films"].count_documents({})
        city_count = await db["cities"].count_documents({})
        location_count = await db["film_locations"].count_documents({})
        etl_job_count = await db["etl_jobs"].count_documents({})

        # Get latest film - DODAJ AWAIT!
        latest_film_cursor = db["films"].find_one(
            {},
            {"_id": 0, "title": 1, "release_date": 1, "fetched_at": 1},
            sort=[("fetched_at", -1)]
        )
        latest_film = await latest_film_cursor

        # Get ETL stats - DODAJ AWAIT!
        pipeline = [
            {"$group": {
                "_id": "$job_type",
                "count": {"$sum": 1},
                "last_run": {"$max": "$started_at"},
                "success_rate": {
                    "$avg": {
                        "$cond": [{"$eq": ["$status", "completed"]}, 1, 0]
                    }
                }
            }}
        ]

        etl_stats_cursor = db["etl_jobs"].aggregate(pipeline)
        etl_stats = await etl_stats_cursor.to_list(length=None)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "counts": {
                "films": film_count,
                "cities": city_count,
                "film_locations": location_count,
                "etl_jobs": etl_job_count
            },
            "latest_film": latest_film,
            "etl_stats": etl_stats,
            "collection_sizes": {
                "films": "movies from TMDB",
                "cities": "cities from GeoDB",
                "film_locations": "film-city associations",
                "etl_jobs": "ETL execution history"
            }
        }

    except Exception as e:
        logger.error(f"Error getting analytics stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))