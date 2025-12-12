# backend/app/tasks/etl_tasks.py
from celery import shared_task
from datetime import datetime, timezone
import logging
from ..services.etl.tmdb_service import TMDBServices
from ..services.etl.geodb_service import GeoDBServices
from ..db import get_mongo_client
from ..config import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def fetch_trending_movies(self, time_window: str = "day", limit: int = 30):
    """Task koji dohvata trenutno popularne filmove i sprema ih u MongoDB"""
    try:
        logger.info(f"Starting fetch_trending_movies task for {time_window} window")

        tmdb_service = TMDBServices()
        movies = tmdb_service.get_trending_movies(time_window=time_window, limit=limit)

        # Get MongoDB client
        client = get_mongo_client()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        collection = db["movies"]

        # Process each movie
        processed_count = 0
        for movie in movies:
            try:
                # Add metadata
                movie["fetched_at"] = datetime.now(timezone.utc)
                movie["source"] = "tmdb"
                movie["time_window"] = time_window

                # Check if movie already exists
                existing = collection.find_one({"tmdb_id": movie.get("tmdb_id", movie.get("id"))})

                if existing:
                    # Update existing
                    collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {**movie, "updated_at": datetime.now(timezone.utc)}}
                    )
                    logger.debug(f"Updated movie: {movie.get('title')}")
                else:
                    # Insert new
                    movie["created_at"] = datetime.now(timezone.utc)
                    movie["updated_at"] = datetime.now(timezone.utc)
                    collection.insert_one(movie)
                    logger.debug(f"Inserted movie: {movie.get('title')}")

                processed_count += 1

                # Add geographical data if available
                if movie.get("production_countries"):
                    try:
                        geo_service = GeoDBServices()
                        locations = geo_service.get_locations_for_film_production(movie)
                        if locations:
                            collection.update_one(
                                {"tmdb_id": movie.get("tmdb_id", movie.get("id"))},
                                {"$set": {"possible_locations": locations}}
                            )
                    except Exception as e:
                        logger.warning(f"Could not add locations for movie {movie.get('title')}: {e}")

            except Exception as e:
                logger.error(f"Error processing movie {movie.get('title', 'Unknown')}: {e}")
                continue

        logger.info(f"Successfully processed {processed_count} movies")

        # Update statistics
        stats_collection = db["etl_stats"]
        stats_collection.insert_one({
            "task": "fetch_trending_movies",
            "time_window": time_window,
            "processed_count": processed_count,
            "timestamp": datetime.now(timezone.utc),
            "status": "success"
        })

        return {
            "status": "success",
            "message": f"Processed {processed_count} movies",
            "time_window": time_window
        }

    except Exception as e:
        logger.error(f"Error in fetch_trending_movies task: {e}")

        # Update statistics with error
        try:
            client = get_mongo_client()
            if client:
                db = client[settings.MONGO_DB]
                stats_collection = db["etl_stats"]
                stats_collection.insert_one({
                    "task": "fetch_trending_movies",
                    "time_window": time_window,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc),
                    "status": "error"
                })
        except Exception as stats_error:
            logger.error(f"Could not update stats: {stats_error}")

        # Retry logic
        try:
            self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for fetch_trending_movies")

        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2)
def fetch_movie_details(self, movie_id: int):
    """Task koji dohvata detalje za specifični film"""
    try:
        logger.info(f"Starting fetch_movie_details task for movie ID: {movie_id}")

        tmdb_service = TMDBServices()
        movie_details = tmdb_service.get_movie_details(movie_id)

        # Get MongoDB client
        client = get_mongo_client()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        collection = db["movie_details"]

        # Add metadata
        movie_details["fetched_at"] = datetime.now(timezone.utc)
        movie_details["source"] = "tmdb"

        # Check if details already exist
        existing = collection.find_one({"tmdb_id": movie_id})

        if existing:
            # Update existing
            collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {**movie_details, "updated_at": datetime.now(timezone.utc)}}
            )
            logger.info(f"Updated details for movie ID: {movie_id}")
        else:
            # Insert new
            movie_details["created_at"] = datetime.now(timezone.utc)
            movie_details["updated_at"] = datetime.now(timezone.utc)
            collection.insert_one(movie_details)
            logger.info(f"Inserted details for movie ID: {movie_id}")

        return {
            "status": "success",
            "message": f"Fetched details for movie ID: {movie_id}",
            "movie_title": movie_details.get("title")
        }

    except Exception as e:
        logger.error(f"Error in fetch_movie_details task for movie {movie_id}: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def fetch_geographical_data(city_name: str = None, country_code: str = None):
    """Task koji dohvata geografske podatke"""
    try:
        logger.info(f"Starting fetch_geographical_data task: city={city_name}, country={country_code}")

        geo_service = GeoDBServices()

        # Get MongoDB client
        client = get_mongo_client()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        collection = db["locations"]

        if city_name:
            # Search for cities
            result = geo_service.search_cities(city_name, limit=20)
            cities_data = result.get("data", [])

            for city in cities_data:
                city_data = {
                    "city_id": city.get("id"),
                    "name": city.get("name"),
                    "country": city.get("country"),
                    "country_code": city.get("countryCode"),
                    "region": city.get("region"),
                    "population": city.get("population"),
                    "latitude": city.get("latitude"),
                    "longitude": city.get("longitude"),
                    "fetched_at": datetime.now(timezone.utc),
                    "source": "geodb"
                }

                # Check if city already exists
                existing = collection.find_one({"city_id": city_data["city_id"]})

                if existing:
                    collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {**city_data, "updated_at": datetime.now(timezone.utc)}}
                    )
                else:
                    city_data["created_at"] = datetime.now(timezone.utc)
                    city_data["updated_at"] = datetime.now(timezone.utc)
                    collection.insert_one(city_data)

            return {
                "status": "success",
                "message": f"Fetched {len(cities_data)} cities for '{city_name}'"
            }

        elif country_code:
            # Get cities by country
            cities = geo_service.get_cities_by_country(country_code, limit=50)

            for city in cities:
                city_data = {
                    **city,
                    "fetched_at": datetime.now(timezone.utc),
                    "source": "geodb"
                }

                existing = collection.find_one({"city_id": city["city_id"]})

                if existing:
                    collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {**city_data, "updated_at": datetime.now(timezone.utc)}}
                    )
                else:
                    city_data["created_at"] = datetime.now(timezone.utc)
                    city_data["updated_at"] = datetime.now(timezone.utc)
                    collection.insert_one(city_data)

            return {
                "status": "success",
                "message": f"Fetched {len(cities)} cities for country '{country_code}'"
            }

        else:
            return {"status": "error", "message": "No search criteria provided"}

    except Exception as e:
        logger.error(f"Error in fetch_geographical_data task: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def daily_etl_pipeline():
    """Glavni ETL pipeline koji se izvršava dnevno"""
    try:
        logger.info("Starting daily ETL pipeline")

        # 1. Fetch trending movies
        trending_result = fetch_trending_movies.delay(time_window="day", limit=50)

        # 2. Fetch geographical data for major film production countries
        countries = ["US", "GB", "FR", "DE", "IT", "ES", "CA", "AU"]
        geo_results = []
        for country in countries:
            result = fetch_geographical_data.delay(country_code=country)
            geo_results.append(result)

        # 3. Update statistics
        client = get_mongo_client()
        if client:
            db = client[settings.MONGO_DB]
            stats_collection = db["etl_pipeline_stats"]
            stats_collection.insert_one({
                "pipeline": "daily",
                "tasks_started": len(geo_results) + 1,
                "timestamp": datetime.now(timezone.utc),
                "status": "started"
            })

        return {
            "status": "started",
            "message": "Daily ETL pipeline started",
            "trending_task_id": trending_result.id,
            "geo_task_count": len(geo_results)
        }

    except Exception as e:
        logger.error(f"Error starting daily ETL pipeline: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def enrich_movies_with_locations():
    """Task koji obogaćuje postojeće filmove sa lokacijskim podacima"""
    try:
        logger.info("Starting enrich_movies_with_locations task")

        client = get_mongo_client()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        movies_collection = db["movies"]
        locations_collection = db["locations"]

        # Get movies without location data
        movies = list(movies_collection.find(
            {"possible_locations": {"$exists": False}},
            limit=100
        ))

        geo_service = GeoDBServices()

        enriched_count = 0
        for movie in movies:
            try:
                locations = geo_service.get_locations_for_film_production(movie)
                if locations:
                    movies_collection.update_one(
                        {"_id": movie["_id"]},
                        {"$set": {"possible_locations": locations}}
                    )
                    enriched_count += 1
                    logger.debug(f"Enriched movie: {movie.get('title')}")
            except Exception as e:
                logger.warning(f"Could not enrich movie {movie.get('title')}: {e}")
                continue

        logger.info(f"Enriched {enriched_count} movies with location data")
        return {
            "status": "success",
            "message": f"Enriched {enriched_count} movies with location data"
        }

    except Exception as e:
        logger.error(f"Error in enrich_movies_with_locations task: {e}")
        return {"status": "error", "message": str(e)}