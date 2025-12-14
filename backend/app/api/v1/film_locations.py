# backend/app/api/v1/film_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ...db import get_mongo_client
from ...config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/cities/geoapify", tags=["Analytics"])
async def get_cities_from_geoapify(
        limit: int = Query(4, ge=1, le=10),
        country_code: Optional[str] = Query("US", description="Country code: US, GB, FR, DE, etc.")
):
    """
    Vraća gradove direktno iz Geoapify API-ja
    """
    try:
        logger.info(f"Fetching {limit} cities from Geoapify for country {country_code}")

        from ...services.etl.geoapify_service import geoapify_service

        # Provjeri da li je Geoapify dostupan
        if not geoapify_service.api_key:
            logger.warning("Geoapify API key not set, returning fallback data")
            return await get_featured_cities(limit=limit, country_codes=country_code)

        # Koristi postojeću funkciju za dobijanje gradova
        major_cities = await geoapify_service._get_major_cities(
            country_code=country_code.upper() if country_code else "US",
            limit=limit
        )

        if not major_cities:
            logger.warning(f"No cities found from Geoapify for {country_code}, using fallback")
            return await get_featured_cities(limit=limit, country_codes=country_code)

        # Transformuj podatke u naš format
        cities = []
        for i, city_data in enumerate(major_cities[:limit]):
            city = {
                "city_id": f"geoapify_{i}_{country_code.lower()}",
                "name": city_data.get("name", f"City {i + 1}"),
                "country": city_data.get("country", country_code),
                "country_code": country_code.upper() if country_code else "US",
                "population": city_data.get("population", 0),
                "film_importance": "Major city with filming potential",
                "sample_films": ["Various film productions"],
                "description": f"Major city in {country_code} suitable for film production",
                "source": "geoapify_api"
            }
            cities.append(city)

        return {
            "source": "geoapify_api",
            "country_code": country_code,
            "count": len(cities),
            "cities": cities
        }

    except Exception as e:
        logger.error(f"Error getting cities from Geoapify: {e}")
        # Fallback na featured cities
        return await get_featured_cities(limit=limit)


@router.get("/cities/featured", tags=["Analytics"])
async def get_featured_cities(
        limit: int = Query(4, ge=1, le=10),
        use_api: bool = Query(True, description="Use Geoapify API or fallback data")
):
    """
    Vraća izabrane gradove za filmsku produkciju

    Parameters:
    - limit: Broj gradova za vraćanje (1-10)
    - use_api: Da li koristiti Geoapify API ili fallback podatke
    """
    try:
        logger.info(f"Fetching {limit} featured cities (use_api={use_api})")

        if use_api:
            try:
                from ...services.etl.geoapify_service import geoapify_service

                # Provjeri da li je API key postavljen
                if not geoapify_service.api_key or geoapify_service.api_key == "your_geoapify_api_key_here":
                    logger.warning("Geoapify API key not properly set, using fallback")
                    use_api = False
                else:
                    # Testiraj konekciju
                    is_connected = await geoapify_service.test_connection()
                    if not is_connected:
                        logger.warning("Geoapify API connection failed, using fallback")
                        use_api = False
            except ImportError:
                logger.warning("Geoapify service not available, using fallback")
                use_api = False

        if use_api:
            # Koristi Geoapify API
            cities = await geoapify_service.get_featured_cities(limit=limit)
            source = "geoapify_api"
        else:
            # Koristi fallback podatke
            cities = [
                {
                    "city_id": "los_angeles",
                    "name": "Los Angeles",
                    "country": "United States",
                    "country_code": "US",
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "population": 3976000,
                    "film_importance": "Hollywood - glavni filmski centar svijeta",
                    "description": "Dom Hollywooda i najveća filmska industrija na svijetu sa preko 100 godina filmske historije.",
                    "sample_films": ["Titanic", "Avatar", "Star Wars", "The Godfather", "La La Land"],
                    "source": "fallback_data"
                },
                {
                    "city_id": "london",
                    "name": "London",
                    "country": "United Kingdom",
                    "country_code": "GB",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "population": 8982000,
                    "film_importance": "Glavni evropski filmski centar",
                    "description": "Bogata filmska historija od Shakespeareovog vremena do modernih blockbustera.",
                    "sample_films": ["Harry Potter", "James Bond", "Sherlock Holmes", "The King's Speech",
                                     "Notting Hill"],
                    "source": "fallback_data"
                },
                {
                    "city_id": "paris",
                    "name": "Paris",
                    "country": "France",
                    "country_code": "FR",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "population": 2148000,
                    "film_importance": "Centar evropske kinematografije i umjetnosti",
                    "description": "Grad ljubavi i svjetla, inspirativna lokacija za umjetničke i romantične filmove.",
                    "sample_films": ["Amélie", "The Da Vinci Code", "Midnight in Paris", "Ratatouille",
                                     "Léon: The Professional"],
                    "source": "fallback_data"
                },
                {
                    "city_id": "tokyo",
                    "name": "Tokyo",
                    "country": "Japan",
                    "country_code": "JP",
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                    "population": 13960000,
                    "film_importance": "Važan azijski filmski centar sa jedinstvenom kinematografijom",
                    "description": "Dinamičan grad koji kombinira tradiciju i modernu tehnologiju u filmovima.",
                    "sample_films": ["Godzilla", "Lost in Translation", "The Wolverine", "Kill Bill", "Your Name"],
                    "source": "fallback_data"
                },
                {
                    "city_id": "vancouver",
                    "name": "Vancouver",
                    "country": "Canada",
                    "country_code": "CA",
                    "latitude": 49.2827,
                    "longitude": -123.1207,
                    "population": 675000,
                    "film_importance": "Hollywood North - popularna lokacija za snimanje",
                    "description": "Popularna lokacija zbog raznovrsnih scenerija i povoljnih poreskih olakšica.",
                    "sample_films": ["Deadpool", "Twilight", "The X-Files", "Supernatural", "The Last of Us"],
                    "source": "fallback_data"
                },
                {
                    "city_id": "sydney",
                    "name": "Sydney",
                    "country": "Australia",
                    "country_code": "AU",
                    "latitude": -33.8688,
                    "longitude": 151.2093,
                    "population": 5312000,
                    "film_importance": "Glavni filmski centar Australije i Pacifika",
                    "description": "Spektakularne luke i plaže čine ga popularnom lokacijom za filmsku produkciju.",
                    "sample_films": ["Mad Max", "The Matrix", "Mission: Impossible 2", "The Great Gatsby",
                                     "Finding Nemo"],
                    "source": "fallback_data"
                }
            ][:limit]
            source = "fallback_data"

        return {
            "source": source,
            "count": len(cities),
            "limit": limit,
            "use_api": use_api,
            "cities": cities
        }

    except Exception as e:
        logger.error(f"Error getting featured cities: {e}")
        return {
            "source": "error",
            "count": 0,
            "cities": [],
            "error": str(e)
        }

@router.get("/films/popular", tags=["Analytics"])
async def get_popular_films(
        limit: int = Query(4, ge=1, le=20)
):
    """
    Vraća popularne filmove - ISPRAVLJENA VERZIJA
    """
    try:
        logger.info(f"Fetching popular films, limit: {limit}")

        # Prvo probaj iz TMDB API-ja
        try:
            from ...services.etl.tmdb_service import tmdb_service

            logger.info("Attempting to fetch from TMDB API...")
            movies = await tmdb_service.fetch_trending_movies(limit=limit)

            if movies:
                popular_films = []
                for movie in movies:
                    # OVO JE KLJUČNO: movie je dict, koristi .get() ali sa default vrijednostima
                    film_data = {
                        "film_id": movie.get("id", 0),
                        "title": movie.get("title", "Unknown Title"),
                        "original_title": movie.get("original_title", ""),
                        "release_date": movie.get("release_date", ""),
                        "overview": movie.get("overview", ""),
                        "popularity": float(movie.get("popularity", 0)),
                        "vote_average": float(movie.get("vote_average", 0)),
                        "vote_count": int(movie.get("vote_count", 0)),
                        "poster_path": movie.get("poster_path", ""),
                        "backdrop_path": movie.get("backdrop_path", ""),
                        "genre_ids": movie.get("genre_ids", []),
                        "adult": bool(movie.get("adult", False)),
                        "video": bool(movie.get("video", False))
                    }

                    # Dodaj full image URL
                    if film_data["poster_path"]:
                        film_data["poster_url"] = f"https://image.tmdb.org/t/p/w500{film_data['poster_path']}"
                    else:
                        film_data["poster_url"] = "https://via.placeholder.com/500x750?text=No+Poster"

                    # Dodaj backdrop URL
                    if film_data["backdrop_path"]:
                        film_data["backdrop_url"] = f"https://image.tmdb.org/t/p/original{film_data['backdrop_path']}"

                    popular_films.append(film_data)

                logger.info(f"Successfully fetched {len(popular_films)} films from TMDB")
                return {
                    "source": "tmdb_api",
                    "count": len(popular_films),
                    "films": popular_films
                }
            else:
                logger.warning("TMDB returned empty movies list")
        except Exception as tmdb_error:
            logger.warning(f"TMDB API error: {tmdb_error}")

        # Fallback: probaj iz baze
        logger.info("Falling back to database...")
        client = get_mongo_client()
        if not client:
            raise HTTPException(status_code=500, detail="MongoDB not connected")

        db = client[settings.MONGO_DB]
        films_collection = db["films"]

        # Dohvati filmove iz baze
        films_cursor = films_collection.find(
            {},
            {"_id": 0, "film_id": 1, "title": 1, "release_date": 1, "overview": 1,
             "popularity": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1}
        ).sort("popularity", -1).limit(limit)

        films = await films_cursor.to_list(length=limit)

        # Dodaj URL za slike
        for film in films:
            if film.get("poster_path"):
                film["poster_url"] = f"https://image.tmdb.org/t/p/w500{film['poster_path']}"
            else:
                film["poster_url"] = "https://via.placeholder.com/500x750?text=No+Poster"

        return {
            "source": "database",
            "count": len(films),
            "films": films
        }

    except Exception as e:
        logger.error(f"Error in get_popular_films: {e}", exc_info=True)
        import traceback
        traceback.print_exc()

        # Final fallback: hardcoded podaci
        fallback_films = [
            {
                "film_id": 1,
                "title": "The Shawshank Redemption",
                "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "release_date": "1994-09-23",
                "popularity": 100.0,
                "vote_average": 8.7,
                "vote_count": 24000,
                "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
            },
            {
                "film_id": 2,
                "title": "The Godfather",
                "overview": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
                "release_date": "1972-03-24",
                "popularity": 95.0,
                "vote_average": 8.7,
                "vote_count": 18000,
                "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"
            },
            {
                "film_id": 3,
                "title": "The Dark Knight",
                "overview": "When the menace known as the Joker wreaks havoc on Gotham City, Batman must accept one of the greatest psychological tests.",
                "release_date": "2008-07-18",
                "popularity": 90.0,
                "vote_average": 8.5,
                "vote_count": 30000,
                "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
            },
            {
                "film_id": 4,
                "title": "Pulp Fiction",
                "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
                "release_date": "1994-10-14",
                "popularity": 85.0,
                "vote_average": 8.5,
                "vote_count": 25000,
                "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
                "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"
            }
        ][:limit]

        return {
            "source": "fallback",
            "count": len(fallback_films),
            "films": fallback_films,
            "error": str(e)
        }



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


def _get_fallback_coordinates(country_code: str):
    """Vraća fallback koordinate za zemlju ako API ne radi"""
    fallback_data = {
        "US": (38.89511, -77.03637, "Washington, D.C."),
        "GB": (51.5074, -0.1278, "London"),
        "FR": (48.8566, 2.3522, "Paris"),
        "DE": (52.5200, 13.4050, "Berlin"),
        "JP": (35.6762, 139.6503, "Tokyo"),
        "CA": (45.4215, -75.6972, "Ottawa"),
        "AU": (-35.2809, 149.1300, "Canberra"),
        "IT": (41.9028, 12.4964, "Rome"),
        "ES": (40.4168, -3.7038, "Madrid"),
        "BR": (-15.7801, -47.9292, "Brasília"),
        "IN": (28.6139, 77.2090, "New Delhi"),
        "CN": (39.9042, 116.4074, "Beijing"),
        "RU": (55.7558, 37.6173, "Moscow"),
        "KR": (37.5665, 126.9780, "Seoul"),
        "MX": (19.4326, -99.1332, "Mexico City")
    }
    return fallback_data.get(country_code, (0, 0, "Capital"))


@router.get("/map/regional-popularity", tags=["Analytics"])
async def get_regional_popularity_map():
    """
    Mapa filmske popularnosti po regionu
    Vraća podatke za prikaz mape sa najpopularnijim filmovima po zemljama
    """
    try:
        logger.info("Generating regional popularity map data")

        from ...services.etl.tmdb_service import tmdb_service
        from ...services.etl.geoapify_service import geoapify_service

        # Lista zemalja za koje želimo prikazati podatke
        countries = [
            {"code": "US", "name": "United States"},
            {"code": "GB", "name": "United Kingdom"},
            {"code": "FR", "name": "France"},
            {"code": "DE", "name": "Germany"},
            {"code": "JP", "name": "Japan"},
            {"code": "CA", "name": "Canada"},
            {"code": "AU", "name": "Australia"},
            {"code": "IT", "name": "Italy"},
            {"code": "ES", "name": "Spain"},
            {"code": "BR", "name": "Brazil"},
            {"code": "IN", "name": "India"},
            {"code": "CN", "name": "China"},
            {"code": "RU", "name": "Russia"},
            {"code": "KR", "name": "South Korea"},
            {"code": "MX", "name": "Mexico"}
        ]

        regional_data = []

        for country in countries:
            try:
                country_code = country["code"]
                country_name = country["name"]

                logger.info(f"Processing country: {country_name} ({country_code})")

                # 1. Dohvati popularne filmove za ovu regiju
                # Prvo probaj sa fetch_popular_movies_by_region ako postoji
                # Ako ne postoji, koristi fetch_trending_movies kao fallback
                movies = []
                try:
                    # Pokušaj da pozoveš novu funkciju
                    movies = await tmdb_service.fetch_popular_movies_by_region(
                        region=country_code,
                        limit=10
                    )
                except AttributeError:
                    # Fallback: koristi trending movies ako nova funkcija ne postoji
                    logger.info(f"Using trending movies as fallback for {country_code}")
                    all_movies = await tmdb_service.fetch_trending_movies(limit=20)
                    # Filtriranje po production_countries ili original_language
                    movies = [
                        m for m in all_movies
                        if country_code in str(m.get("original_language", "")).upper()
                           or any(country_name.lower() in str(c).lower() for c in m.get("production_countries", []))
                    ][:10]

                if not movies or len(movies) < 3:
                    logger.warning(
                        f"Insufficient movies for region {country_code} ({len(movies) if movies else 0} found)")
                    # Koristi globalne trending filmove kao fallback
                    fallback_movies = await tmdb_service.fetch_trending_movies(limit=10)
                    movies = fallback_movies[:5] if fallback_movies else []

                # 2. Odaberi top 3 filma za prikaz
                top_movies = []
                for movie in movies[:3]:
                    movie_data = {
                        "film_id": movie.get("id"),
                        "title": movie.get("title", "Unknown"),
                        "release_date": movie.get("release_date", ""),
                        "vote_average": round(movie.get("vote_average", 0), 1),
                        "poster_path": movie.get("poster_path"),
                        "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get(
                            "poster_path") else "https://via.placeholder.com/500x750?text=No+Poster",
                        "overview": (movie.get("overview", "")[:100] + "...") if len(
                            movie.get("overview", "")) > 100 else movie.get("overview", "")
                    }
                    top_movies.append(movie_data)

                # 3. Analiziraj žanrove za filmove
                genre_counter = {}
                for movie in movies[:10]:
                    genre_ids = movie.get("genre_ids", [])
                    for genre_id in genre_ids:
                        genre_counter[genre_id] = genre_counter.get(genre_id, 0) + 1

                # Ako nema genre_ids, probaj sa genres listom
                if not genre_counter and movies:
                    for movie in movies[:10]:
                        genres = movie.get("genres", [])
                        if isinstance(genres, list):
                            for genre in genres:
                                if isinstance(genre, dict):
                                    genre_id = genre.get("id")
                                    if genre_id:
                                        genre_counter[genre_id] = genre_counter.get(genre_id, 0) + 1

                # Sortiraj žanrove po učestalosti
                sorted_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)

                # Mapiranje ID-jeva žanrova na nazive
                genre_map = {
                    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
                    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
                    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
                    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
                    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
                }

                top_genres = []
                for genre_id, count in sorted_genres[:3]:  # Top 3 žanra
                    genre_name = genre_map.get(genre_id, f"Genre {genre_id}")
                    percentage = round((count / max(len(movies[:10]), 1)) * 100, 1) if movies else 0
                    top_genres.append({
                        "name": genre_name,
                        "count": count,
                        "percentage": percentage
                    })

                # Ako nema žanrova, dodaj generic
                if not top_genres:
                    top_genres = [
                        {"name": "Various", "count": 1, "percentage": 100},
                        {"name": "Entertainment", "count": 1, "percentage": 100},
                        {"name": "Movies", "count": 1, "percentage": 100}
                    ]

                # 4. Dohvati geografske podatke za zemlju
                try:
                    # Prvo pokušaj da koristiš postojeći servis
                    if hasattr(geoapify_service, '_get_major_cities'):
                        cities = await geoapify_service._get_major_cities(country_code, limit=1)
                        if cities:
                            capital_city = cities[0].get("name", "Capital")
                            # Fallback koordinate za sada
                            latitude, longitude, _ = _get_fallback_coordinates(country_code)
                        else:
                            latitude, longitude, capital_city = _get_fallback_coordinates(country_code)
                    else:
                        latitude, longitude, capital_city = _get_fallback_coordinates(country_code)
                except Exception as geo_error:
                    logger.warning(f"Geoapify error for {country_code}: {geo_error}")
                    latitude, longitude, capital_city = _get_fallback_coordinates(country_code)

                # 5. Kreiraj regionalni podatak za mapu
                region_data = {
                    "country_code": country_code,
                    "country_name": country_name,
                    "capital_city": capital_city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "total_movies_analyzed": min(len(movies), 10),
                    "top_movies": top_movies,
                    "top_genres": top_genres,
                    "source": "tmdb_api",
                    "last_updated": datetime.utcnow().isoformat()
                }

                regional_data.append(region_data)
                logger.info(f"✓ Processed {country_name}: {len(top_movies)} movies, {len(top_genres)} genres")

                # Rate limiting između zahtjeva za API-je
                import asyncio
                await asyncio.sleep(0.3)  # 300ms delay između zemalja

            except Exception as country_error:
                logger.error(f"Error processing country {country['name']}: {country_error}")
                # Dodaj minimalne podatke za ovu zemlju
                latitude, longitude, capital_city = _get_fallback_coordinates(country["code"])
                regional_data.append({
                    "country_code": country["code"],
                    "country_name": country["name"],
                    "capital_city": capital_city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "total_movies_analyzed": 0,
                    "top_movies": [],
                    "top_genres": [{"name": "Data unavailable", "count": 0, "percentage": 0}],
                    "source": "error",
                    "last_updated": datetime.utcnow().isoformat()
                })
                continue

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_regions": len(regional_data),
            "regions": regional_data,
            "map_center": {"lat": 20, "lng": 0},  # Centar mape (Africa)
            "map_zoom": 2,
            "status": "success",
            "message": f"Regional popularity data for {len(regional_data)} countries"
        }

    except Exception as e:
        logger.error(f"Error generating regional popularity map: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate regional popularity map: {str(e)}"
        )


@router.get("/map/test-minimal", tags=["Analytics"])
async def test_minimal_map_data():
    """
    Minimalni test endpoint za mapu (brži za testiranje)
    """
    try:
        from ...services.etl.tmdb_service import tmdb_service

        # Samo 3 zemlje za brzo testiranje
        test_countries = [
            {"code": "US", "name": "United States"},
            {"code": "GB", "name": "United Kingdom"},
            {"code": "FR", "name": "France"}
        ]

        regional_data = []

        for country in test_countries:
            # Dohvati neke filmove
            movies = await tmdb_service.fetch_trending_movies(limit=3)

            top_movies = []
            for movie in movies[:2]:  # Samo 2 filma za test
                top_movies.append({
                    "film_id": movie.get("id"),
                    "title": movie.get("title", "Test Movie"),
                    "vote_average": round(movie.get("vote_average", 0), 1),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get(
                        "poster_path") else ""
                })

            # Dodaj podatke
            latitude, longitude, capital = _get_fallback_coordinates(country["code"])
            regional_data.append({
                "country_code": country["code"],
                "country_name": country["name"],
                "capital_city": capital,
                "latitude": latitude,
                "longitude": longitude,
                "top_movies": top_movies,
                "top_genres": [
                    {"name": "Action", "count": 5, "percentage": 50},
                    {"name": "Drama", "count": 3, "percentage": 30},
                    {"name": "Comedy", "count": 2, "percentage": 20}
                ]
            })

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_regions": len(regional_data),
            "regions": regional_data,
            "status": "test_success"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "test_data": [
                {
                    "country_code": "US",
                    "country_name": "United States",
                    "capital_city": "Washington, D.C.",
                    "latitude": 38.89511,
                    "longitude": -77.03637,
                    "top_movies": [
                        {"title": "Test Movie 1", "vote_average": 8.5},
                        {"title": "Test Movie 2", "vote_average": 7.8}
                    ],
                    "top_genres": [
                        {"name": "Action", "percentage": 45},
                        {"name": "Drama", "percentage": 30},
                        {"name": "Comedy", "percentage": 25}
                    ]
                }
            ]
        }

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