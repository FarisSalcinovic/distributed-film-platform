# backend/app/api/v1/film_locations.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from ...db import get_mongo_client
from ...dependencies.auth import get_current_user
from ...models.user import User
from ...config import settings
from ...services.etl.geodb_service import GeoDBServices
import asyncio

router = APIRouter(prefix="/film-locations", tags=["Film Locations Analytics"])


@router.get("/movies-by-country")
async def get_movies_by_country(
        current_user: User = Depends(get_current_user),
        min_movies: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100)
):
    """Vraća filmove grupisane po zemljama produkcije"""
    client = get_mongo_client()
    if not client:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    db = client[settings.MONGO_DB]

    pipeline = [
        {"$match": {"production_countries": {"$exists": True, "$ne": []}}},
        {"$unwind": "$production_countries"},
        {"$group": {
            "_id": "$production_countries",
            "movies": {"$push": {"title": "$title", "release_date": "$release_date", "vote_average": "$vote_average"}},
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$vote_average"},
            "total_budget": {"$sum": "$budget"}
        }},
        {"$match": {"count": {"$gte": min_movies}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    results = list(db.movies.aggregate(pipeline))

    # Obogatite sa GeoDB podacima
    geo_service = GeoDBServices()
    enriched_results = []

    for result in results:
        country_name = result["_id"]
        # Pokušajte dobiti gradove za ovu zemlju
        try:
            # Ovo je pojednostavljeno - trebali biste mapirati nazive zemalja na country codes
            if country_name == "United States":
                cities = await geo_service.get_cities_by_country("US", limit=5)
            elif country_name == "United Kingdom":
                cities = await geo_service.get_cities_by_country("GB", limit=5)
            elif country_name == "France":
                cities = await geo_service.get_cities_by_country("FR", limit=5)
            elif country_name == "Germany":
                cities = await geo_service.get_cities_by_country("DE", limit=5)
            else:
                cities = []

            result["major_cities"] = cities
        except Exception as e:
            result["major_cities"] = []
            result["geo_error"] = str(e)

        enriched_results.append(result)

    return {"countries": enriched_results}


@router.get("/find-filming-locations")
async def find_filming_locations(
        current_user: User = Depends(get_current_user),
        city_name: Optional[str] = Query(None),
        country_code: Optional[str] = Query(None),
        radius_km: int = Query(100, ge=1, le=500)
):
    """Pronalazi moguće lokacije za snimanje na osnovu geografskih parametara"""
    geo_service = GeoDBServices()

    if city_name:
        # Pretraži gradove po nazivu
        result = await geo_service.search_cities(city_name, limit=10)
        cities = result.get("data", [])
    elif country_code:
        # Dohvati gradove po zemlji
        cities = await geo_service.get_cities_by_country(country_code, limit=20)
    else:
        raise HTTPException(status_code=400, detail="Either city_name or country_code must be provided")

    # Dohvati filmove koji bi mogli biti snimani u ovim gradovima
    client = get_mongo_client()
    if not client:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    db = client[settings.MONGO_DB]

    # Pretpostavimo da imamo neku logiku za match-ovanje
    # Ovo je pojednostavljena verzija
    films = list(db.movies.find(
        {"vote_average": {"$gte": 7.0}},
        {"title": 1, "genres": 1, "production_countries": 1, "budget": 1}
    ).limit(10))

    return {
        "search_criteria": {"city_name": city_name, "country_code": country_code},
        "found_cities": len(cities),
        "cities": cities[:5],  # Vrati samo prvih 5
        "suggested_films": [
            {
                "title": film["title"],
                "genres": film.get("genres", []),
                "countries": film.get("production_countries", []),
                "suitable_locations": cities[:3] if cities else []
            }
            for film in films
        ]
    }


@router.get("/production-hotspots")
async def get_production_hotspots(
        current_user: User = Depends(get_current_user),
        min_budget: int = Query(1000000, ge=0)
):
    """Identificira 'hotspot' gradove za filmsku produkciju na osnovu filmskih podataka"""
    client = get_mongo_client()
    if not client:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    db = client[settings.MONGO_DB]

    # Dohvati filmove sa velikim budžetom
    films = list(db.movies.find(
        {"budget": {"$gte": min_budget}},
        {"title": 1, "production_countries": 1, "budget": 1, "revenue": 1}
    ).limit(50))

    # Analiziraj koje zemlje su najzastupljenije
    country_stats = {}
    for film in films:
        for country in film.get("production_countries", []):
            if country not in country_stats:
                country_stats[country] = {
                    "film_count": 0,
                    "total_budget": 0,
                    "total_revenue": 0,
                    "films": []
                }

            country_stats[country]["film_count"] += 1
            country_stats[country]["total_budget"] += film.get("budget", 0)
            country_stats[country]["total_revenue"] += film.get("revenue", 0)
            country_stats[country]["films"].append(film["title"])

    # Sortiraj zemlje po budžetu
    sorted_countries = sorted(
        country_stats.items(),
        key=lambda x: x[1]["total_budget"],
        reverse=True
    )[:10]

    # Dohvati gradove za top zemlje
    geo_service = GeoDBServices()
    hotspots = []

    for country_name, stats in sorted_countries:
        try:
            # Mapiraj naziv zemlje na country code
            country_map = {
                "United States": "US",
                "United Kingdom": "GB",
                "France": "FR",
                "Germany": "DE",
                "Italy": "IT",
                "Spain": "ES",
                "Canada": "CA",
                "Australia": "AU"
            }

            country_code = country_map.get(country_name)
            if country_code:
                cities = await geo_service.get_cities_by_country(country_code, limit=5)
                stats["major_cities"] = cities
            else:
                stats["major_cities"] = []

        except Exception as e:
            stats["major_cities"] = []
            stats["geo_error"] = str(e)

        hotspots.append({
            "country": country_name,
            **stats
        })

    return {
        "hotspots": hotspots,
        "analysis": "Production hotspots based on film budget and frequency"
    }


@router.get("/compare-locations")
async def compare_locations(
        current_user: User = Depends(get_current_user),
        city1: str = Query(..., description="First city name"),
        city2: str = Query(..., description="Second city name")
):
    """Upoređuje dva grada kao potencijalne lokacije za filmsku produkciju"""
    geo_service = GeoDBServices()

    # Pretraži oba grada
    result1 = await geo_service.search_cities(city1, limit=5)
    result2 = await geo_service.search_cities(city2, limit=5)

    cities1 = result1.get("data", [])
    cities2 = result2.get("data", [])

    if not cities1 or not cities2:
        raise HTTPException(status_code=404, detail="One or both cities not found")

    city1_data = cities1[0]
    city2_data = cities2[0]

    # Dohvati filmove koji bi mogli biti relevantni
    client = get_mongo_client()
    if not client:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    db = client[settings.MONGO_DB]

    # Pretpostavimo neku logiku za preporuku filmova
    films = list(db.movies.find(
        {"vote_average": {"$gte": 6.0}},
        {"title": 1, "genres": 1, "production_countries": 1}
    ).limit(5))

    comparison = {
        "city1": {
            "name": city1_data.get("name"),
            "country": city1_data.get("country"),
            "population": city1_data.get("population"),
            "latitude": city1_data.get("latitude"),
            "longitude": city1_data.get("longitude")
        },
        "city2": {
            "name": city2_data.get("name"),
            "country": city2_data.get("country"),
            "population": city2_data.get("population"),
            "latitude": city2_data.get("latitude"),
            "longitude": city2_data.get("longitude")
        },
        "suggested_films": films,
        "analysis": {
            "city1_better_for": ["Large productions" if city1_data.get("population", 0) > 1000000 else "Indie films"],
            "city2_better_for": ["Large productions" if city2_data.get("population", 0) > 1000000 else "Indie films"],
            "recommendation": "Both cities have potential depending on film type"
        }
    }

    return comparison