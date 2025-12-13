# backend/app/tasks/etl_tasks.py
from celery import shared_task
from datetime import datetime, timezone
import logging
import uuid
import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional

# Koristi pravilne import putanje
from ..services.etl.tmdb_service import tmdb_service
from ..services.etl.geoapify_service import geoapify_service  # PROMENJENO: GeoDB → Geoapify
from ..services.etl.aggregation_service import aggregation_service  # NOVO
from ..config import settings
from pymongo import MongoClient
import traceback

logger = logging.getLogger(__name__)


def get_mongo_client_sync():
    """Sync MongoDB client for Celery tasks"""
    try:
        # Koristi pymongo za sync konekciju
        client = MongoClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            maxPoolSize=10
        )
        # Testiraj konekciju
        client.admin.command('ping')
        logger.info("✓ MongoDB sync connection successful")
        return client
    except Exception as e:
        logger.error(f"✗ MongoDB sync connection failed: {e}")
        return None


@shared_task(bind=True, max_retries=3)
def fetch_and_store_films(self, pages: int = 3, movies_per_page: int = 20):
    """Task koji dohvata filmove sa TMDB i sprema u MongoDB"""
    try:
        logger.info(f"🚀 Starting fetch_and_store_films task: {pages} pages")

        # Get MongoDB client
        client = get_mongo_client_sync()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        films_collection = db["films"]
        etl_jobs_collection = db["etl_jobs"]

        # Create ETL job record
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "job_type": "tmdb",
            "status": "running",
            "parameters": {
                "pages": pages,
                "movies_per_page": movies_per_page,
                "total_limit": pages * movies_per_page
            },
            "started_at": datetime.now(timezone.utc),
            "results": {
                "total_fetched": 0,
                "processed": 0,
                "errors": []
            }
        }
        etl_jobs_collection.insert_one(job_data)
        logger.info(f"Created ETL job: {job_id}")

        # Fetch trending movies
        logger.info("Fetching movies from TMDB...")
        try:
            # Run async function in sync context
            movies = asyncio.run(tmdb_service.fetch_trending_movies(limit=pages * movies_per_page))
        except Exception as e:
            logger.error(f"Error fetching movies: {e}")
            raise

        logger.info(f"Fetched {len(movies)} movies from TMDB")

        processed_count = 0
        error_count = 0

        for movie in movies:
            try:
                movie_id = movie.get("id")
                if not movie_id:
                    continue

                # Check if film already exists
                existing_film = films_collection.find_one({"film_id": movie_id})

                # Get detailed movie information
                try:
                    movie_details = asyncio.run(tmdb_service.fetch_movie_details(movie_id))
                    if not movie_details:
                        logger.warning(f"No details for movie {movie_id}")
                        continue
                except Exception as e:
                    logger.warning(f"Could not fetch details for movie {movie_id}: {e}")
                    continue

                # Transform data
                try:
                    film_data = asyncio.run(tmdb_service.transform_movie_data(movie_details))
                except Exception as e:
                    logger.warning(f"Could not transform data for movie {movie_id}: {e}")
                    continue

                # Add metadata
                film_data["fetched_at"] = datetime.now(timezone.utc)
                film_data["etl_job_id"] = job_id
                film_data["etl_status"] = "processed"

                if existing_film:
                    # Update existing film
                    films_collection.update_one(
                        {"_id": existing_film["_id"]},
                        {
                            "$set": {**film_data, "updated_at": datetime.now(timezone.utc)},
                            "$push": {
                                "etl_history": {
                                    "job_id": job_id,
                                    "fetched_at": datetime.now(timezone.utc),
                                    "status": "updated"
                                }
                            }
                        }
                    )
                    logger.debug(f"Updated film: {film_data.get('title')} (ID: {movie_id})")
                else:
                    # Insert new film
                    film_data["created_at"] = datetime.now(timezone.utc)
                    film_data["updated_at"] = datetime.now(timezone.utc)
                    film_data["etl_history"] = [{
                        "job_id": job_id,
                        "fetched_at": datetime.now(timezone.utc),
                        "status": "created"
                    }]

                    films_collection.insert_one(film_data)
                    logger.info(f"✓ Inserted film: {film_data.get('title')} (ID: {movie_id})")

                processed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing movie {movie.get('title', 'Unknown')}: {e}")
                logger.error(traceback.format_exc())
                continue

        # Update job status
        etl_jobs_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc),
                    "results.total_fetched": len(movies),
                    "results.processed": processed_count,
                    "results.error_count": error_count,
                    "results.message": f"Processed {processed_count} movies with {error_count} errors"
                }
            }
        )

        logger.info(f"✅ Successfully processed {processed_count} movies (errors: {error_count})")

        return {
            "job_id": job_id,
            "status": "success",
            "message": f"Processed {processed_count} movies",
            "stats": {
                "total_fetched": len(movies),
                "processed": processed_count,
                "errors": error_count
            }
        }

    except Exception as e:
        logger.error(f"❌ Error in fetch_and_store_films task: {e}")
        logger.error(traceback.format_exc())

        # Update job with error if possible
        try:
            client = get_mongo_client_sync()
            if client:
                db = client[settings.MONGO_DB]
                etl_jobs_collection = db["etl_jobs"]

                if 'job_id' in locals():
                    etl_jobs_collection.update_one(
                        {"job_id": job_id},
                        {
                            "$set": {
                                "status": "failed",
                                "completed_at": datetime.now(timezone.utc),
                                "error": str(e)
                            }
                        }
                    )
        except Exception as update_error:
            logger.error(f"Could not update job status: {update_error}")

        # Retry logic
        try:
            self.retry(exc=e, countdown=60 * 2)  # Retry after 2 minutes
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for fetch_and_store_films")

        return {
            "status": "error",
            "message": str(e)
        }


@shared_task(bind=True, max_retries=2)
def fetch_and_store_places(self, country_codes: List[str] = None, limit_per_country: int = 20):
    """Task koji dohvata mesta (places) sa Geoapify i skladišti ih"""
    try:
        logger.info(f"🚀 Starting fetch_and_store_places task")

        client = get_mongo_client_sync()
        if not client:
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]

        # Kreiraj kolekcije ako ne postoje
        if "places" not in db.list_collection_names():
            db.create_collection("places")
        if "film_place_correlations" not in db.list_collection_names():
            db.create_collection("film_place_correlations")

        # ETL job record
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "job_type": "geoapify_places",
            "status": "running",
            "parameters": {
                "country_codes": country_codes or ["US", "GB", "FR"],
                "limit_per_country": limit_per_country
            },
            "started_at": datetime.now(timezone.utc),
            "results": {"total_processed": 0}
        }
        db.etl_jobs.insert_one(job_data)
        logger.info(f"📝 Created Geoapify ETL job: {job_id}")

        # Podrazumevane zemlje ako nisu prosleđene
        countries = country_codes or ["US", "GB", "FR"]
        total_processed = 0

        for country_code in countries:
            try:
                logger.info(f"🌍 Fetching places for {country_code}...")

                # Dohvati mesta za zemlju - koristi novi Geoapify servis
                places = asyncio.run(
                    geoapify_service.get_places_by_country(
                        country_code=country_code,
                        limit_per_city=limit_per_country // len(countries)
                    )
                )

                if not places:
                    logger.warning(f"⚠️ No places found for {country_code}")
                    continue

                for place in places:
                    try:
                        # Dodaj metadata
                        place.update({
                            "fetched_at": datetime.now(timezone.utc),
                            "etl_job_id": job_id,
                            "source": "geoapify",
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        })

                        # Upsert u bazu
                        db.places.update_one(
                            {"place_id": place["place_id"]},
                            {"$set": place},
                            upsert=True
                        )

                        total_processed += 1
                        logger.info(f"📍 {place['name']}, {place['city']}")

                    except Exception as e:
                        logger.warning(f"Error processing place: {e}")
                        continue

                logger.info(f"📊 Processed {len(places)} places for {country_code}")

                # Rate limiting pauza između zemalja
                time.sleep(2)

            except Exception as e:
                logger.error(f"Failed for {country_code}: {e}")
                continue

        # Ažuriraj ETL job
        db.etl_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc),
                    "results.total_processed": total_processed,
                    "results.countries_processed": len(countries)
                }
            }
        )

        logger.info(f"🎉 Total: {total_processed} places processed")

        # Automatski pokreni korelaciju sa filmovima
        if total_processed > 0:
            correlation_job_id = asyncio.run(
                create_film_place_correlations(db, job_id)
            )
            logger.info(f"🔗 Correlation job created: {correlation_job_id}")

        return {
            "job_id": job_id,
            "status": "success",
            "message": f"Processed {total_processed} places",
            "stats": {
                "processed": total_processed,
                "countries": len(countries)
            }
        }

    except Exception as e:
        logger.error(f"❌ Error in fetch_and_store_places: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}


async def create_film_place_correlations(db, source_job_id: str) -> str:
    """Kreira korelacije između filmova i mesta"""
    try:
        # Dohvati filmove i mesta
        films = list(db.films.find().limit(50))
        places = list(db.places.find().limit(100))

        if not films or not places:
            logger.warning("⚠️ Not enough data for correlations")
            return ""

        # Kreiraj korelacije
        correlations = aggregation_service.correlate_films_with_locations(films, places)

        # Kreiraj novi ETL job za korelacije
        correlation_job_id = str(uuid.uuid4())
        correlation_job = {
            "job_id": correlation_job_id,
            "job_type": "film_place_correlation",
            "status": "completed",
            "source_job_id": source_job_id,
            "started_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
            "results": {
                "total_correlations": len(correlations),
                "films_analyzed": len(films),
                "places_analyzed": len(places)
            }
        }
        db.etl_jobs.insert_one(correlation_job)

        # Skladišti korelacije
        for correlation in correlations:
            correlation["correlation_job_id"] = correlation_job_id
            correlation["created_at"] = datetime.now(timezone.utc)

            db.film_place_correlations.update_one(
                {"film_id": correlation["film_id"]},
                {"$set": correlation},
                upsert=True
            )

        # Izvrši analizu uspeha
        success_analysis = aggregation_service.analyze_film_success_by_location(
            films, correlations
        )

        # Skladišti analizu
        if success_analysis:
            db.analytics.insert_one({
                "analysis_type": "film_success_by_location",
                "job_id": correlation_job_id,
                "data": success_analysis,
                "created_at": datetime.now(timezone.utc)
            })

        logger.info(f"🔗 Created {len(correlations)} film-place correlations")
        return correlation_job_id

    except Exception as e:
        logger.error(f"Error creating correlations: {e}")
        return ""


@shared_task
def enrich_films_with_places():
    """Task koji povezuje filmove sa mestima (places) iz Geoapify"""
    try:
        logger.info("Starting enrich_films_with_places task")

        client = get_mongo_client_sync()
        if not client:
            logger.error("MongoDB client not available")
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        films_collection = db["films"]
        places_collection = db["places"]

        # Kreiraj kolekciju ako ne postoji
        if "film_place_connections" not in db.list_collection_names():
            db.create_collection("film_place_connections")

        # Get films without place data (limit 15 za test)
        films = list(films_collection.find(
            {"places_enriched": {"$ne": True}},
            limit=15
        ))

        logger.info(f"Found {len(films)} films to enrich with places")

        enriched_count = 0

        for film in films:
            try:
                film_id = film.get("film_id")
                if not film_id:
                    continue

                film_title = film.get("title", "Unknown")
                film_genres = film.get("genres", [])

                logger.info(f"Processing film: {film_title}")

                # Dohvati mesta koja odgovaraju žanrovima filma
                suitable_places = []

                # Mapiranje žanrova na kategorije mesta
                genre_to_categories = {
                    "action": ["entertainment.cinema", "commercial", "building"],
                    "comedy": ["entertainment", "catering", "tourism"],
                    "drama": ["building.historic", "tourism.museum", "tourism.sights"],
                    "horror": ["building.abandoned", "tourism.sights", "natural"],
                    "romance": ["tourism.sights.viewpoint", "catering.cafe", "tourism"]
                }

                # Pronađi relevantne kategorije za film
                relevant_categories = []
                for genre in film_genres[:2]:  # Uzmi max 2 glavna žanra
                    genre_lower = genre.lower()
                    if genre_lower in genre_to_categories:
                        relevant_categories.extend(genre_to_categories[genre_lower])

                # Ako nema mapiranja, koristi opšte kategorije
                if not relevant_categories:
                    relevant_categories = ["entertainment", "tourism", "catering"]

                # Pretraži mesta po relevantnim kategorijama
                for category in relevant_categories[:3]:  # Uzmi max 3 kategorije
                    category_places = list(places_collection.find({
                        "categories": {"$regex": category, "$options": "i"}
                    }).limit(5))

                    for place in category_places:
                        # Izračunaj match score
                        match_score = _calculate_place_match_score(
                            film_genres,
                            place.get("categories", []),
                            place.get("primary_category", "")
                        )

                        if match_score > 0.3:  # Minimalni threshold
                            suitable_places.append({
                                "place": place,
                                "match_score": match_score,
                                "match_reason": f"Matches {category} category"
                            })

                # Skladišti veze ako postoje odgovarajuća mesta
                if suitable_places:
                    # Sortiraj po match score
                    suitable_places.sort(key=lambda x: x["match_score"], reverse=True)

                    for place_data in suitable_places[:3]:  # Uzmi top 3 mesta
                        place = place_data["place"]

                        connection = {
                            "film_id": film_id,
                            "film_title": film_title,
                            "place_id": place.get("place_id"),
                            "place_name": place.get("name"),
                            "place_city": place.get("city"),
                            "place_country": place.get("country"),
                            "place_categories": place.get("categories", []),
                            "match_score": place_data["match_score"],
                            "match_reason": place_data["match_reason"],
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        }

                        # Upsert vezu
                        db.film_place_connections.update_one(
                            {
                                "film_id": film_id,
                                "place_id": place.get("place_id")
                            },
                            {"$set": connection},
                            upsert=True
                        )

                    # Obeleži film kao обогаћен
                    films_collection.update_one(
                        {"_id": film["_id"]},
                        {
                            "$set": {
                                "places_enriched": True,
                                "matched_places_count": len(suitable_places),
                                "updated_at": datetime.now(timezone.utc)
                            }
                        }
                    )

                    enriched_count += 1
                    logger.info(f"✓ Enriched film: {film_title} with {len(suitable_places)} places")

                else:
                    logger.debug(f"No suitable places found for film: {film_title}")

            except Exception as e:
                logger.warning(f"Could not enrich film {film.get('title', 'Unknown')}: {e}")
                continue

        logger.info(f"✅ Enriched {enriched_count} films with places data")

        return {
            "status": "success",
            "message": f"Enriched {enriched_count} films with places data"
        }

    except Exception as e:
        logger.error(f"❌ Error in enrich_films_with_places task: {e}")
        return {"status": "error", "message": str(e)}


def _calculate_place_match_score(film_genres: List[str], place_categories: List[str],
                                 primary_category: str) -> float:
    """Izračunava koliko se dobro film i mesto poklapaju"""
    score = 0.0

    # Mapiranje žanrova na kategorije
    genre_category_map = {
        "action": ["entertainment.cinema", "commercial", "building"],
        "comedy": ["entertainment", "catering", "tourism"],
        "drama": ["building.historic", "tourism.museum", "tourism.sights"],
        "horror": ["building.abandoned", "tourism.sights", "natural"],
        "romance": ["tourism.sights.viewpoint", "catering.cafe", "tourism"]
    }

    # Proveri direktna poklapanja
    for genre in film_genres:
        genre_lower = genre.lower()
        if genre_lower in genre_category_map:
            for cat in genre_category_map[genre_lower]:
                if cat in primary_category or any(cat in pc for pc in place_categories):
                    score += 0.3

    # Bonus za specifične kategorije
    if "cinema" in primary_category or any("cinema" in cat for cat in place_categories):
        score += 0.4
    if "museum" in primary_category or any("museum" in cat for cat in place_categories):
        score += 0.3
    if "historic" in primary_category or any("historic" in cat for cat in place_categories):
        score += 0.2

    return min(score, 1.0)  # Normalizuj na 0-1


@shared_task
def test_api_connections():
    """Task za testiranje API konekcija"""
    try:
        logger.info("Testing API connections...")

        # Test TMDB connection
        tmdb_ok = asyncio.run(tmdb_service.test_connection())

        # Test Geoapify connection
        geoapify_ok = asyncio.run(geoapify_service.test_connection())

        return {
            "status": "success",
            "tmdb_connection": "ok" if tmdb_ok else "failed",
            "geoapify_connection": "ok" if geoapify_ok else "failed",
            "message": "API connection test completed"
        }

    except Exception as e:
        logger.error(f"Error testing API connections: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def run_combined_etl():
    """Glavni ETL pipeline koji pokreće sve taskove sa Geoapify"""
    try:
        logger.info("🚀 Starting combined ETL pipeline with Geoapify")

        # 1. Test API connections first
        test_task = test_api_connections.delay()

        # 2. Fetch and store films
        films_task = fetch_and_store_films.delay(pages=2, movies_per_page=15)

        # 3. Fetch and store places (after 45 seconds delay)
        places_task = fetch_and_store_places.apply_async(
            kwargs={"country_codes": ["US", "GB", "FR"], "limit_per_country": 15},
            countdown=45
        )

        # 4. Enrich films with places (after 2 minutes delay)
        enrich_task = enrich_films_with_places.apply_async(countdown=120)

        return {
            "status": "started",
            "message": "Combined ETL pipeline started",
            "task_ids": {
                "test": test_task.id,
                "films": films_task.id,
                "places": places_task.id,
                "enrich": enrich_task.id
            }
        }

    except Exception as e:
        logger.error(f"❌ Error starting combined ETL pipeline: {e}")
        return {"status": "error", "message": str(e)}


# Ostale pomoćne funkcije
@shared_task
def cleanup_old_data(days_old: int = 30):
    """Čisti stare podatke iz baze"""
    try:
        logger.info(f"Cleaning up data older than {days_old} days")

        client = get_mongo_client_sync()
        if not client:
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]
        cutoff_date = datetime.now(timezone.utc) - timezone.timedelta(days=days_old)

        # Broj obrisanih dokumenata po kolekciji
        deleted_counts = {}

        # Čisti stare ETL job-ove
        deleted_counts["etl_jobs"] = db.etl_jobs.delete_many({
            "completed_at": {"$lt": cutoff_date},
            "status": {"$in": ["completed", "failed"]}
        }).deleted_count

        # Čisti stare analize
        deleted_counts["analytics"] = db.analytics.delete_many({
            "created_at": {"$lt": cutoff_date}
        }).deleted_count

        logger.info(f"✅ Cleanup completed: {deleted_counts}")

        return {
            "status": "success",
            "message": f"Cleaned up {sum(deleted_counts.values())} old documents",
            "deleted_counts": deleted_counts
        }

    except Exception as e:
        logger.error(f"Error in cleanup: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def generate_daily_report():
    """Generiše dnevni izveštaj o ETL aktivnostima"""
    try:
        logger.info("Generating daily ETL report")

        client = get_mongo_client_sync()
        if not client:
            return {"status": "error", "message": "MongoDB not connected"}

        db = client[settings.MONGO_DB]

        # Dnevni period
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timezone.timedelta(days=1)

        # Statistika za danas
        today_stats = {
            "films_added": db.films.count_documents({
                "created_at": {"$gte": today_start}
            }),
            "places_added": db.places.count_documents({
                "created_at": {"$gte": today_start}
            }),
            "etl_jobs_run": db.etl_jobs.count_documents({
                "started_at": {"$gte": today_start}
            }),
            "successful_jobs": db.etl_jobs.count_documents({
                "started_at": {"$gte": today_start},
                "status": "completed"
            }),
            "failed_jobs": db.etl_jobs.count_documents({
                "started_at": {"$gte": today_start},
                "status": "failed"
            })
        }

        # Ukupna statistika
        total_stats = {
            "total_films": db.films.count_documents({}),
            "total_places": db.places.count_documents({}),
            "total_correlations": db.film_place_correlations.count_documents({}),
            "total_connections": db.film_place_connections.count_documents({})
        }

        # Skladišti izveštaj
        report_id = str(uuid.uuid4())
        report = {
            "report_id": report_id,
            "report_date": datetime.now(timezone.utc),
            "period_start": today_start,
            "period_end": datetime.now(timezone.utc),
            "today_stats": today_stats,
            "total_stats": total_stats,
            "generated_at": datetime.now(timezone.utc)
        }

        db.daily_reports.insert_one(report)

        logger.info(f"✅ Daily report generated: {report_id}")

        return {
            "status": "success",
            "message": "Daily report generated",
            "report_id": report_id,
            "stats": {
                "today": today_stats,
                "total": total_stats
            }
        }

    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return {"status": "error", "message": str(e)}