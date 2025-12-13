# backend/app/api/v1/etl.py - ISPRAVLJENO
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from typing import Dict, Any, List
import logging
from datetime import datetime

# Koristi relativne importove koji odgovaraju tvojoj strukturi
try:
    from ...tasks.etl_tasks import (
        fetch_and_store_films,
        fetch_and_store_places,
        enrich_films_with_places,
        run_combined_etl,
        test_api_connections,
        cleanup_old_data,
        generate_daily_report
    )

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Celery tasks not available, using mock functions")

# DODAJ PREFIX I TAGS OVDE!
router = APIRouter(prefix="/etl", tags=["ETL Operations"])
logger = logging.getLogger(__name__)


# Mock funkcije ako Celery nije dostupan
async def mock_etl_task(task_name: str, **kwargs):
    """Mock ETL task za test"""
    return {
        "status": "success",
        "message": f"Mock {task_name} task executed",
        "task_id": f"mock-{datetime.utcnow().timestamp()}",
        "parameters": kwargs
    }


@router.post("/run-tmdb-etl")
async def run_tmdb_etl(
        pages: int = 3,
        movies_per_page: int = 20,
        background_tasks: BackgroundTasks = None
):
    """
    Pokreće ETL proces za TMDB (filmovi)

    Parameters:
    - pages: Broj stranica za fetch (svaka ima 20 filmova)
    - movies_per_page: Broj filmova po stranici
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                # Asinhrono izvršavanje
                background_tasks.add_task(fetch_and_store_films.delay, pages, movies_per_page)
                return {
                    "message": f"TMDB ETL pokrenut asinhrono",
                    "status": "processing",
                    "parameters": {
                        "pages": pages,
                        "movies_per_page": movies_per_page
                    }
                }
            else:
                # Sinhrono izvršavanje
                result = fetch_and_store_films.delay(pages, movies_per_page)
                return {
                    "message": "TMDB ETL zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id,
                    "parameters": {
                        "pages": pages,
                        "movies_per_page": movies_per_page
                    }
                }
        else:
            # Mock response ako Celery nije dostupan
            mock_result = await mock_etl_task("TMDB", pages=pages, movies_per_page=movies_per_page)
            return {
                "message": "TMDB ETL (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"],
                "parameters": mock_result["parameters"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju TMDB ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-places-etl")
async def run_places_etl(
        country_codes: List[str] = Body(["US", "GB", "FR"], description="Country codes to fetch"),
        limit_per_country: int = Body(20, description="Places per country"),
        background_tasks: BackgroundTasks = None
):
    """
    Pokreće ETL proces za Geoapify (mesta/places)

    Parameters:
    - country_codes: Lista kodova zemalja (npr. ["US", "GB", "FR"])
    - limit_per_country: Broj mesta po zemlji
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(fetch_and_store_places.delay, country_codes, limit_per_country)
                return {
                    "message": f"Geoapify Places ETL pokrenut asinhrono",
                    "status": "processing",
                    "parameters": {
                        "country_codes": country_codes,
                        "limit_per_country": limit_per_country
                    }
                }
            else:
                result = fetch_and_store_places.delay(country_codes, limit_per_country)
                return {
                    "message": "Geoapify Places ETL zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id,
                    "parameters": {
                        "country_codes": country_codes,
                        "limit_per_country": limit_per_country
                    }
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("Geoapify Places",
                                              country_codes=country_codes,
                                              limit_per_country=limit_per_country)
            return {
                "message": "Geoapify Places ETL (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"],
                "parameters": mock_result["parameters"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju Geoapify Places ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-enrichment")
async def run_enrichment_etl(
        background_tasks: BackgroundTasks = None
):
    """
    Pokreće enrichment proces za povezivanje filmova i mesta
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(enrich_films_with_places.delay)
                return {
                    "message": "Enrichment ETL pokrenut asinhrono",
                    "status": "processing"
                }
            else:
                result = enrich_films_with_places.delay()
                return {
                    "message": "Enrichment ETL zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("Enrichment")
            return {
                "message": "Enrichment ETL (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju enrichment ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-full-etl")
async def run_full_etl(
        background_tasks: BackgroundTasks = None
):
    """
    Pokreće kompletan ETL proces (TMDB + Geoapify + Enrichment)
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(run_combined_etl.delay)
                return {
                    "message": "Kompletan ETL pokrenut asinhrono",
                    "status": "processing"
                }
            else:
                result = run_combined_etl.delay()
                return {
                    "message": "Kompletan ETL zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("Full ETL")
            return {
                "message": "Full ETL (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju kompletnog ETL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-api-connections")
async def trigger_api_test(
        background_tasks: BackgroundTasks = None
):
    """
    Testira konekcije sa svim API-jevima
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(test_api_connections.delay)
                return {
                    "message": "API test pokrenut asinhrono",
                    "status": "processing"
                }
            else:
                result = test_api_connections.delay()
                return {
                    "message": "API test zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("API Test")
            return {
                "message": "API Test (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju API testa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup-old-data")
async def trigger_cleanup(
        days_old: int = 30,
        background_tasks: BackgroundTasks = None
):
    """
    Čisti stare podatke iz baze

    Parameters:
    - days_old: Broj dana nakon kojih se podaci smatraju starim
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(cleanup_old_data.delay, days_old)
                return {
                    "message": f"Cleanup pokrenut asinhrono (starije od {days_old} dana)",
                    "status": "processing",
                    "parameters": {"days_old": days_old}
                }
            else:
                result = cleanup_old_data.delay(days_old)
                return {
                    "message": "Cleanup zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id,
                    "parameters": {"days_old": days_old}
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("Cleanup", days_old=days_old)
            return {
                "message": "Cleanup (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"],
                "parameters": mock_result["parameters"]
            }

    except Exception as e:
        logger.error(f"Greška pri pokretanju cleanup-a: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def trigger_report_generation(
        background_tasks: BackgroundTasks = None
):
    """
    Generiše dnevni izveštaj o ETL aktivnostima
    """
    try:
        if CELERY_AVAILABLE:
            if background_tasks:
                background_tasks.add_task(generate_daily_report.delay)
                return {
                    "message": "Report generation pokrenut asinhrono",
                    "status": "processing"
                }
            else:
                result = generate_daily_report.delay()
                return {
                    "message": "Report generation zadatak pokrenut",
                    "status": "queued",
                    "task_id": result.id
                }
        else:
            # Mock response
            mock_result = await mock_etl_task("Report Generation")
            return {
                "message": "Report Generation (mock) pokrenut",
                "status": "completed",
                "task_id": mock_result["task_id"]
            }

    except Exception as e:
        logger.error(f"Greška pri generisanju izveštaja: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Proverava status Celery task-a
    """
    try:
        if CELERY_AVAILABLE:
            from ...tasks.celery_app import celery_app

            task_result = celery_app.AsyncResult(task_id)

            response = {
                "task_id": task_id,
                "status": task_result.status,
                "ready": task_result.ready()
            }

            if task_result.ready():
                if task_result.successful():
                    response["result"] = task_result.result
                else:
                    response["error"] = str(task_result.result)

            return response
        else:
            # Mock response za test taskove
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "ready": True,
                "result": {"message": "Mock task completed successfully"}
            }

    except Exception as e:
        logger.error(f"Greška pri proveri statusa task-a: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/latest")
async def get_latest_jobs(limit: int = 10):
    """
    Vraća poslednje ETL job-ove iz baze
    """
    try:
        from ...db import get_mongo_client
        from ...config import settings

        client = get_mongo_client()
        if not client:
            # Ako MongoDB nije dostupan, vrati mock podatke
            return {
                "total_jobs": 0,
                "jobs": [
                    {
                        "job_id": "mock-job-1",
                        "job_type": "tmdb",
                        "status": "completed",
                        "started_at": datetime.utcnow().isoformat(),
                        "completed_at": datetime.utcnow().isoformat(),
                        "results": {"total_fetched": 10, "processed": 10}
                    },
                    {
                        "job_id": "mock-job-2",
                        "job_type": "geoapify_places",
                        "status": "completed",
                        "started_at": datetime.utcnow().isoformat(),
                        "completed_at": datetime.utcnow().isoformat(),
                        "results": {"total_processed": 15, "countries_processed": 3}
                    }
                ]
            }

        db = client[settings.MONGO_DB]
        etl_jobs = db["etl_jobs"]

        jobs = list(etl_jobs.find(
            {},
            {"_id": 0}
        ).sort("started_at", -1).limit(limit))

        return {
            "total_jobs": etl_jobs.count_documents({}),
            "jobs": jobs
        }

    except Exception as e:
        logger.error(f"Greška pri dohvatanju job-ova: {str(e)}")
        return {
            "total_jobs": 0,
            "jobs": [],
            "error": str(e)
        }


@router.get("/collections/stats")
async def get_collections_stats():
    """
    Vraća statistiku svih kolekcija u bazi
    """
    try:
        from ...db import get_mongo_client
        from ...config import settings

        client = get_mongo_client()
        if not client:
            return {
                "status": "error",
                "message": "MongoDB not available",
                "collections": {}
            }

        db = client[settings.MONGO_DB]
        collection_names = db.list_collection_names()

        stats = {}
        for collection_name in collection_names:
            try:
                count = db[collection_name].count_documents({})
                stats[collection_name] = {
                    "count": count,
                    "estimated_size_mb": 0
                }
            except Exception as e:
                stats[collection_name] = {
                    "count": 0,
                    "error": str(e)
                }

        return {
            "status": "success",
            "total_collections": len(collection_names),
            "total_documents": sum(s.get("count", 0) for s in stats.values() if isinstance(s, dict)),
            "collections": stats
        }

    except Exception as e:
        logger.error(f"Greška pri dohvatanju statistike kolekcija: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_etl_endpoint():
    """Test endpoint za ETL - ne zahtijeva admin"""
    return {
        "message": "ETL endpoints are working!",
        "timestamp": datetime.utcnow().isoformat(),
        "available_endpoints": [
            "POST /api/v1/etl/run-tmdb-etl",
            "POST /api/v1/etl/run-places-etl",
            "POST /api/v1/etl/run-enrichment",
            "POST /api/v1/etl/run-full-etl",
            "POST /api/v1/etl/test-api-connections",
            "POST /api/v1/etl/cleanup-old-data",
            "POST /api/v1/etl/generate-report",
            "GET /api/v1/etl/task-status/{task_id}",
            "GET /api/v1/etl/jobs/latest",
            "GET /api/v1/etl/collections/stats"
        ],
        "current_apis": [
            "TMDB (Movies)",
            "Geoapify (Places)"
        ],
        "authentication_required": False
    }


@router.get("/status")
async def get_etl_system_status():
    """Vraća status ETL sistema"""
    try:
        from ...services.etl.tmdb_service import tmdb_service
        from ...services.etl.geoapify_service import geoapify_service

        tmdb_configured = bool(tmdb_service.api_key)
        geoapify_configured = bool(geoapify_service.api_key)

        return {
            "system": "ETL Processing System",
            "status": "active",
            "celery_available": CELERY_AVAILABLE,
            "apis_configured": {
                "tmdb": tmdb_configured,
                "geoapify": geoapify_configured
            },
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "test": "/api/v1/etl/test",
                "tmdb_etl": "/api/v1/etl/run-tmdb-etl",
                "places_etl": "/api/v1/etl/run-places-etl",
                "jobs": "/api/v1/etl/jobs/latest",
                "stats": "/api/v1/etl/collections/stats"
            }
        }
    except Exception as e:
        return {
            "system": "ETL Processing System",
            "status": "partially_available",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/correlation-stats")
async def get_correlation_stats():
    """
    Vraća statistiku korelacija između filmova i mesta
    """
    try:
        from ...db import get_mongo_client
        from ...config import settings

        client = get_mongo_client()
        if not client:
            return {
                "status": "no_data",
                "message": "MongoDB not available",
                "total_correlations": 0,
                "sample_correlations": []
            }

        db = client[settings.MONGO_DB]

        # Proveri da li postoji kolekcija
        if "film_place_correlations" not in db.list_collection_names():
            return {
                "status": "no_data",
                "message": "No correlation data yet",
                "total_correlations": 0,
                "sample_correlations": []
            }

        correlations_collection = db["film_place_correlations"]

        # Broj ukupnih korelacija
        total_correlations = correlations_collection.count_documents({})

        # Uzmi uzorak za prikaz
        sample_correlations = list(correlations_collection.find(
            {},
            {"_id": 0, "film_title": 1, "place_city": 1, "place_country": 1, "match_score": 1}
        ).limit(5))

        return {
            "status": "success",
            "total_correlations": total_correlations,
            "sample_correlations": sample_correlations,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Greška pri dohvatanju statistike korelacija: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "total_correlations": 0,
            "sample_correlations": []
        }