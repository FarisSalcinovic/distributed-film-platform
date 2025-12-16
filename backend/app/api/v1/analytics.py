from django.contrib.postgres.aggregates import statistics
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ...dependencies.auth import get_current_user
from ...models.user import User
from ...db import get_mongo_client
from ...services.etl.aggregation_service import aggregation_service
import asyncio

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/film-location-correlations")
async def get_film_location_correlations(
        film_id: Optional[int] = Query(None, description="Filter by film ID"),
        genre: Optional[str] = Query(None, description="Filter by genre"),
        country_code: Optional[str] = Query(None, description="Filter by country"),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user)
):
    """
    Get correlations between films and locations
    """
    client = await get_mongo_client()
    db = client.film_data

    # Build query
    query = {}
    if film_id:
        query["film_id"] = film_id
    if genre:
        query["film_genres"] = {"$in": [genre.lower()]}

    # Get correlations
    correlations = list(db.film_place_correlations.find(
        query
    ).limit(limit))

    # Filter by country if needed
    if country_code:
        filtered = []
        for corr in correlations:
            locations = corr.get("suggested_locations", [])
            country_locations = [
                loc for loc in locations
                if loc.get("place", {}).get("country_code") == country_code.upper()
            ]
            if country_locations:
                filtered.append({
                    **corr,
                    "suggested_locations": country_locations
                })
        correlations = filtered

    return {
        "count": len(correlations),
        "correlations": correlations[:limit]
    }


@router.get("/location-success-analysis")
async def get_location_success_analysis(
        min_films: int = Query(1, ge=1, description="Minimum films per location"),
        current_user: User = Depends(get_current_user)
):
    """
    Analyze film success metrics by location
    """
    client = await get_mongo_client()
    db = client.film_data

    # Get latest analysis
    analysis = db.analytics.find_one(
        {"analysis_type": "film_success_by_location"},
        sort=[("created_at", -1)]
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis available. Run ETL first."
        )

    data = analysis.get("data", {})
    location_stats = data.get("location_stats", {})

    # Filter by minimum films
    filtered_stats = {
        pid: stats for pid, stats in location_stats.items()
        if stats.get("total_films", 0) >= min_films
    }

    # Calculate overall metrics
    if filtered_stats:
        avg_rating = statistics.mean([
            stats["average_rating"] for stats in filtered_stats.values()
            if stats["average_rating"] > 0
        ]) if filtered_stats else 0

        avg_popularity = statistics.mean([
            stats["average_popularity"] for stats in filtered_stats.values()
            if stats["average_popularity"] > 0
        ]) if filtered_stats else 0

    return {
        "analysis_date": analysis.get("created_at"),
        "total_locations": len(filtered_stats),
        "overall_average_rating": avg_rating,
        "overall_average_popularity": avg_popularity,
        "top_locations": [
            {
                "place_name": stats["place_name"],
                "city": stats["place_city"],
                "total_films": stats["total_films"],
                "average_rating": stats["average_rating"],
                "genres": stats.get("genres", [])[:3]
            }
            for pid, stats in list(filtered_stats.items())[:10]
        ]
    }


@router.get("/genre-location-matrix")
async def get_genre_location_matrix(
        current_user: User = Depends(get_current_user)
):
    """
    Get matrix of which genres correlate with which location categories
    """
    client = await get_mongo_client()
    db = client.film_data

    correlations = list(db.film_place_correlations.find())

    if not correlations:
        raise HTTPException(
            status_code=404,
            detail="No correlations available. Run ETL first."
        )

    # Build genre-location matrix
    matrix = {}

    for corr in correlations:
        genres = corr.get("film_genres", [])
        locations = corr.get("suggested_locations", [])

        for genre in genres:
            if genre not in matrix:
                matrix[genre] = {}

            for loc in locations:
                place = loc.get("place", {})
                categories = place.get("categories", [])

                for category in categories[:2]:  # Take top 2 categories
                    if category not in matrix[genre]:
                        matrix[genre][category] = 0
                    matrix[genre][category] += 1

    # Convert to sorted list
    result = []
    for genre, categories in matrix.items():
        top_categories = sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 categories per genre

        result.append({
            "genre": genre,
            "total_correlations": sum(categories.values()),
            "top_categories": [
                {"category": cat, "count": count}
                for cat, count in top_categories
            ]
        })

    # Sort by total correlations
    result.sort(key=lambda x: x["total_correlations"], reverse=True)

    return {
        "matrix": result,
        "total_genres": len(result),
        "most_common_genre": result[0]["genre"] if result else None
    }


@router.get("/location-recommendations")
async def get_location_recommendations(
        preferred_genres: List[str] = Query([], description="User's preferred genres"),
        preferred_categories: List[str] = Query([], description="Preferred location categories"),
        limit: int = Query(10, ge=1, le=50),
        current_user: User = Depends(get_current_user)
):
    """
    Get location recommendations based on user preferences
    """
    if not preferred_genres and not preferred_categories:
        raise HTTPException(
            status_code=400,
            detail="Provide at least preferred_genres or preferred_categories"
        )

    client = await get_mongo_client()
    db = client.film_data

    # Get places
    places = list(db.places.find().limit(100))

    if not places:
        raise HTTPException(
            status_code=404,
            detail="No places available. Run ETL first."
        )

    # Generate recommendations
    user_prefs = {
        "preferred_genres": preferred_genres,
        "preferred_categories": preferred_categories
    }

    recommendations = aggregation_service.generate_location_recommendations(
        user_prefs, places
    )

    return {
        "user_preferences": user_prefs,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations[:limit]
    }


@router.get("/cross-api-stats")
async def get_cross_api_stats(
        current_user: User = Depends(get_current_user)
):
    """
    Get statistics combining data from both TMDB and Geoapify
    """
    client = await get_mongo_client()
    db = client.film_data

    # Get counts
    film_count = await db.films.count_documents({})
    place_count = await db.places.count_documents({})
    correlation_count = await db.film_place_correlations.count_documents({})

    # Get average film ratings by country
    films = list(db.films.find({}, {"vote_average": 1, "production_countries": 1}))

    country_ratings = {}
    for film in films:
        rating = film.get("vote_average", 0)
        countries = film.get("production_countries", [])

        for country in countries[:2]:  # Take first 2 countries
            if country not in country_ratings:
                country_ratings[country] = {"total": 0, "count": 0, "ratings": []}

            country_ratings[country]["total"] += rating
            country_ratings[country]["count"] += 1
            country_ratings[country]["ratings"].append(rating)

    # Calculate averages
    for country, data in country_ratings.items():
        if data["count"] > 0:
            data["average"] = data["total"] / data["count"]
            # Remove lists to reduce response size
            del data["ratings"]
            del data["total"]

    # Get most common location categories
    places = list(db.places.find({}, {"categories": 1}))
    category_counts = {}

    for place in places:
        categories = place.get("categories", [])
        for category in categories[:3]:  # Take top 3 categories per place
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1

    top_categories = sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return {
        "data_summary": {
            "total_films": film_count,
            "total_places": place_count,
            "total_correlations": correlation_count,
            "coverage_ratio": f"{correlation_count / max(film_count, 1) * 100:.1f}%"
        },
        "film_insights": {
            "countries_with_films": len(country_ratings),
            "top_countries_by_rating": sorted(
                [
                    {"country": c, "average_rating": d["average"], "film_count": d["count"]}
                    for c, d in country_ratings.items() if d.get("average", 0) > 0
                ],
                key=lambda x: x["average_rating"],
                reverse=True
            )[:5]
        },
        "location_insights": {
            "total_categories": len(category_counts),
            "most_common_categories": [
                {"category": cat, "count": count}
                for cat, count in top_categories
            ]
        }
    }