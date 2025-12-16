# backend/app/db.py
import logging
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, text
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from .config import settings

# Setup logging
logger = logging.getLogger(__name__)

# --- PostgreSQL Konekcija ---

# 1. Asinkroni engine za FastAPI
async_engine = create_async_engine(
    settings.POSTGRES_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 2. Sync engine samo za kreiranje tabela
sync_engine = create_engine(
    settings.POSTGRES_URL_SYNC,
    echo=False
)

# 3. Asinkrona Sesija
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 4. Sync Sesija za kreiranje tabela (samo startup)
SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

# 5. Bazni Model
Base = declarative_base()


# 6. Async DB Dependency
async def get_db():
    """Yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 7. Funkcija za kreiranje tabela
def create_all_tables_sync():
    """Creates all tables using sync engine."""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("✓ PostgreSQL tables created successfully")
    except Exception as e:
        logger.error(f"✗ Error creating PostgreSQL tables: {e}")
        raise


async def create_all_tables():
    """Async wrapper for table creation."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_all_tables_sync)
    except Exception as e:
        logger.error(f"Error in async table creation: {e}")
        raise


# --- MongoDB Konekcija ---

class MongoDBManager:
    """Centralized MongoDB manager for all database operations"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.initialized = False

    async def connect(self):
        """Establish MongoDB connection"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGO_URL}...")

            self.client = AsyncIOMotorClient(
                settings.MONGO_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                maxPoolSize=100,
                minPoolSize=10,
                retryWrites=True,
                appname="film_platform"
            )

            # Test connection
            await self.client.admin.command('ping')

            # Get database
            self.db = self.client[settings.MONGO_DB]
            logger.info(f"✓ MongoDB connected to database: {settings.MONGO_DB}")

            # Create indexes
            await self._create_indexes()

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            self.initialized = False
            raise

    async def _create_indexes(self):
        """Create all necessary indexes for optimal performance"""
        try:
            logger.info("Creating MongoDB indexes...")

            # Films collection
            await self.db.films.create_index("film_id", unique=True)
            await self.db.films.create_index("title")
            await self.db.films.create_index([("popularity", -1)])
            await self.db.films.create_index([("vote_average", -1)])
            await self.db.films.create_index("release_date")
            await self.db.films.create_index("genres")
            await self.db.films.create_index("production_countries")
            await self.db.films.create_index([("fetched_at", -1)])

            # Cities collection
            await self.db.cities.create_index("city_id", unique=True)
            await self.db.cities.create_index("name")
            await self.db.cities.create_index([("population", -1)])
            await self.db.cities.create_index("country_code")
            await self.db.cities.create_index([("latitude", 1), ("longitude", 1)])

            # Film locations collection
            await self.db.film_locations.create_index(
                [("film_id", 1), ("city_id", 1)],
                unique=True
            )
            await self.db.film_locations.create_index("film_id")
            await self.db.film_locations.create_index("city_id")
            await self.db.film_locations.create_index([("film_title", "text")])

            # Regional films collection
            await self.db.regional_films.create_index(
                [("region", 1), ("fetch_date", -1)],
                unique=True
            )
            await self.db.regional_films.create_index("region")

            # ETL jobs collection
            await self.db.etl_jobs.create_index([("job_type", 1), ("started_at", -1)])
            await self.db.etl_jobs.create_index("status")
            await self.db.etl_jobs.create_index([("started_at", 1)],
                                                expireAfterSeconds=30 * 24 * 60 * 60)  # 30 days TTL

            # Analytics cache collection
            await self.db.analytics_cache.create_index([("cache_key", 1), ("expires_at", 1)])
            await self.db.analytics_cache.create_index("expires_at", expireAfterSeconds=0)

            logger.info("✓ MongoDB indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")

    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.initialized = False
            logger.info("MongoDB connection closed")

    # --- CRUD Operations for Films ---

    async def save_film(self, film_data: Dict[str, Any]) -> bool:
        """Save or update a film in MongoDB"""
        try:
            if not self.initialized:
                await self.connect()

            film_data["updated_at"] = datetime.utcnow()

            result = await self.db.films.update_one(
                {"film_id": film_data["film_id"]},
                {"$set": film_data},
                upsert=True
            )

            if result.upserted_id:
                logger.debug(f"Inserted film: {film_data['title']} (ID: {film_data['film_id']})")
                return True
            elif result.modified_count > 0:
                logger.debug(f"Updated film: {film_data['title']}")
                return True

            return True  # Document already exists with same data

        except Exception as e:
            logger.error(f"Error saving film {film_data.get('film_id')}: {e}")
            return False

    async def save_films_batch(self, films_data: list) -> Dict[str, Any]:
        """Save multiple films in batch"""
        try:
            if not self.initialized:
                await self.connect()

            inserted = 0
            updated = 0
            errors = 0

            for film_data in films_data:
                try:
                    film_data["updated_at"] = datetime.utcnow()
                    film_data["fetched_at"] = datetime.utcnow()

                    result = await self.db.films.update_one(
                        {"film_id": film_data["film_id"]},
                        {"$set": film_data},
                        upsert=True
                    )

                    if result.upserted_id:
                        inserted += 1
                    elif result.modified_count > 0:
                        updated += 1

                except Exception as e:
                    logger.error(f"Error processing film {film_data.get('film_id')}: {e}")
                    errors += 1

            logger.info(f"Batch save: {inserted} inserted, {updated} updated, {errors} errors")
            return {
                "inserted": inserted,
                "updated": updated,
                "errors": errors,
                "total": len(films_data)
            }

        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            return {"inserted": 0, "updated": 0, "errors": len(films_data), "total": len(films_data)}

    async def get_film(self, film_id: int) -> Optional[Dict[str, Any]]:
        """Get film by ID"""
        try:
            if not self.initialized:
                await self.connect()

            film = await self.db.films.find_one({"film_id": film_id})
            return film

        except Exception as e:
            logger.error(f"Error getting film {film_id}: {e}")
            return None

    async def search_films(self, query: str, limit: int = 20) -> list:
        """Search films by title"""
        try:
            if not self.initialized:
                await self.connect()

            cursor = self.db.films.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)

            films = await cursor.to_list(length=limit)
            return films

        except Exception as e:
            logger.error(f"Error searching films: {e}")
            return []

    # --- CRUD Operations for Regional Films ---

    async def save_regional_films(self, region: str, films_data: list) -> Dict[str, Any]:
        """Save regional films data"""
        try:
            if not self.initialized:
                await self.connect()

            regional_doc = {
                "region": region.upper(),
                "fetch_date": datetime.utcnow(),
                "total_films": len(films_data),
                "films": [],
                "stats": {
                    "avg_vote": round(sum(f.get("vote_average", 0) for f in films_data) / len(films_data),
                                      2) if films_data else 0,
                    "avg_popularity": round(sum(f.get("popularity", 0) for f in films_data) / len(films_data),
                                            2) if films_data else 0,
                    "latest_release": max(
                        [f.get("release_date", "1900-01-01") for f in films_data]) if films_data else None
                }
            }

            # Add films (limit to top 10)
            for film in films_data[:10]:
                film_doc = {
                    "film_id": film.get("id"),
                    "title": film.get("title"),
                    "vote_average": film.get("vote_average"),
                    "popularity": film.get("popularity"),
                    "poster_path": film.get("poster_path"),
                    "release_date": film.get("release_date"),
                    "overview": film.get("overview", "")[:200] + "..." if film.get("overview") else ""
                }
                regional_doc["films"].append(film_doc)

            # Save to MongoDB
            result = await self.db.regional_films.update_one(
                {"region": region.upper(),
                 "fetch_date": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}},
                {"$set": regional_doc},
                upsert=True
            )

            logger.info(f"✅ Saved regional films for {region}: {len(films_data)} films")
            return {
                "region": region,
                "saved": True,
                "films_count": len(films_data),
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }

        except Exception as e:
            logger.error(f"Error saving regional films for {region}: {e}")
            return {"region": region, "saved": False, "error": str(e)}

    async def get_regional_films(self, region: str, limit: int = 3) -> Optional[Dict[str, Any]]:
        """Get latest regional films for a region"""
        try:
            if not self.initialized:
                await self.connect()

            regional_data = await self.db.regional_films.find_one(
                {"region": region.upper()},
                sort=[("fetch_date", -1)]
            )

            if regional_data:
                # Convert ObjectId to string for JSON serialization
                regional_data["_id"] = str(regional_data["_id"])
                # Limit films if needed
                if limit and "films" in regional_data:
                    regional_data["films"] = regional_data["films"][:limit]

            return regional_data

        except Exception as e:
            logger.error(f"Error getting regional films for {region}: {e}")
            return None

    # --- CRUD Operations for Cities ---

    async def save_city(self, city_data: Dict[str, Any]) -> bool:
        """Save or update a city"""
        try:
            if not self.initialized:
                await self.connect()

            city_data["updated_at"] = datetime.utcnow()

            result = await self.db.cities.update_one(
                {"city_id": city_data["city_id"]},
                {"$set": city_data},
                upsert=True
            )

            return result.acknowledged

        except Exception as e:
            logger.error(f"Error saving city {city_data.get('city_id')}: {e}")
            return False

    async def get_cities_by_country(self, country_code: str, limit: int = 20) -> list:
        """Get cities by country code"""
        try:
            if not self.initialized:
                await self.connect()

            cursor = self.db.cities.find(
                {"country_code": country_code.upper()}
            ).sort("population", -1).limit(limit)

            cities = await cursor.to_list(length=limit)
            return cities

        except Exception as e:
            logger.error(f"Error getting cities for {country_code}: {e}")
            return []

    # --- ETL Jobs Management ---

    async def save_etl_job(self, job_data: Dict[str, Any]) -> str:
        """Save ETL job record"""
        try:
            if not self.initialized:
                await self.connect()

            job_data["created_at"] = datetime.utcnow()
            job_data["updated_at"] = datetime.utcnow()

            result = await self.db.etl_jobs.insert_one(job_data)
            job_id = str(result.inserted_id)

            logger.info(f"ETL job saved: {job_data.get('job_type')} - ID: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Error saving ETL job: {e}")
            return ""

    async def update_etl_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update ETL job status"""
        try:
            if not self.initialized:
                await self.connect()

            update_data["updated_at"] = datetime.utcnow()

            result = await self.db.etl_jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_data}
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error updating ETL job {job_id}: {e}")
            return False

    async def get_latest_etl_jobs(self, limit: int = 10) -> list:
        """Get latest ETL jobs"""
        try:
            if not self.initialized:
                await self.connect()

            cursor = self.db.etl_jobs.find(
                {},
                {"_id": 0, "id": {"$toString": "$_id"}, "job_type": 1, "status": 1,
                 "started_at": 1, "completed_at": 1, "records_processed": 1, "error": 1}
            ).sort("started_at", -1).limit(limit)

            jobs = await cursor.to_list(length=limit)
            return jobs

        except Exception as e:
            logger.error(f"Error getting ETL jobs: {e}")
            return []

    # --- Analytics Operations ---

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            if not self.initialized:
                await self.connect()

            stats = {}

            # Film count
            film_count = await self.db.films.count_documents({})
            stats["films"] = film_count

            # City count
            city_count = await self.db.cities.count_documents({})
            stats["cities"] = city_count

            # Film locations count
            location_count = await self.db.film_locations.count_documents({})
            stats["film_locations"] = location_count

            # ETL jobs count
            etl_job_count = await self.db.etl_jobs.count_documents({})
            stats["etl_jobs"] = etl_job_count

            # Regional films count
            regional_films = await self.db.regional_films.count_documents({})
            stats["regional_films"] = regional_films

            # Latest film
            latest_film = await self.db.films.find_one(
                {},
                sort=[("fetched_at", -1)],
                projection={"title": 1, "release_date": 1, "fetched_at": 1}
            )

            if latest_film:
                stats["latest_film"] = {
                    "title": latest_film.get("title"),
                    "release_date": latest_film.get("release_date"),
                    "fetched_at": latest_film.get("fetched_at")
                }

            # ETL stats by type
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
                }},
                {"$project": {
                    "_id": 0,
                    "job_type": "$_id",
                    "count": 1,
                    "last_run": 1,
                    "success_rate": {"$round": ["$success_rate", 2]}
                }}
            ]

            etl_stats_cursor = self.db.etl_jobs.aggregate(pipeline)
            etl_stats = await etl_stats_cursor.to_list(length=None)
            stats["etl_stats"] = etl_stats

            logger.info(f"Collection stats retrieved: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    async def get_films_by_country_analysis(self, limit: int = 20) -> list:
        """Analyze films by production country"""
        try:
            if not self.initialized:
                await self.connect()

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
                {"$limit": limit},
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

            cursor = self.db.films.aggregate(pipeline)
            results = await cursor.to_list(length=limit)

            return results

        except Exception as e:
            logger.error(f"Error analyzing films by country: {e}")
            return []

    # --- Cache Operations ---

    async def set_analytics_cache(self, cache_key: str, data: Any, ttl_minutes: int = 60):
        """Cache analytics data"""
        try:
            if not self.initialized:
                await self.connect()

            expires_at = datetime.utcnow().timestamp() + (ttl_minutes * 60)

            cache_doc = {
                "cache_key": cache_key,
                "data": data,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at
            }

            await self.db.analytics_cache.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )

        except Exception as e:
            logger.error(f"Error setting cache {cache_key}: {e}")

    async def get_analytics_cache(self, cache_key: str) -> Optional[Any]:
        """Get cached analytics data"""
        try:
            if not self.initialized:
                await self.connect()

            cache_doc = await self.db.analytics_cache.find_one(
                {"cache_key": cache_key, "expires_at": {"$gt": datetime.utcnow().timestamp()}}
            )

            return cache_doc["data"] if cache_doc else None

        except Exception as e:
            logger.error(f"Error getting cache {cache_key}: {e}")
            return None

    async def clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            if not self.initialized:
                await self.connect()

            result = await self.db.analytics_cache.delete_many(
                {"expires_at": {"$lt": datetime.utcnow().timestamp()}}
            )

            if result.deleted_count > 0:
                logger.info(f"Cleared {result.deleted_count} expired cache entries")

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")


# Create global MongoDB manager instance
mongo_manager = MongoDBManager()


# --- Helper Functions ---

async def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    """Get MongoDB client - compatible with existing code"""
    if not mongo_manager.initialized:
        await mongo_manager.connect()
    return mongo_manager.client


async def connect_to_mongo():
    """Connect to MongoDB - startup function"""
    await mongo_manager.connect()


async def close_mongo_connection():
    """Close MongoDB connection - shutdown function"""
    await mongo_manager.close()


def get_mongo_client_sync():
    """Sync MongoDB client for Celery tasks"""
    try:
        from pymongo import MongoClient
        import urllib.parse

        # Parse MONGO_URL for pymongo
        mongo_user = settings.MONGO_INITDB_ROOT_USERNAME
        mongo_pass = urllib.parse.quote_plus(settings.MONGO_INITDB_ROOT_PASSWORD)
        mongo_host = settings.MONGO_HOST
        mongo_db = settings.MONGO_DB

        mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/{mongo_db}?authSource=admin"

        client = MongoClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10
        )

        # Test connection
        client.admin.command('ping')
        logger.info(f"✓ Sync MongoDB client created for Celery")
        return client

    except Exception as e:
        logger.error(f"✗ Sync MongoDB client error: {e}")
        return None


# --- Connection Testing ---

async def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✓ PostgreSQL connection test successful")
        return True
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection test failed: {e}")
        return False


async def test_mongo_connection():
    """Test MongoDB connection"""
    try:
        await mongo_manager.connect()
        logger.info("✓ MongoDB connection test successful")
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection test failed: {e}")
        return False


# Export
__all__ = [
    "get_db",
    "create_all_tables",
    "get_mongo_client",
    "get_mongo_client_sync",
    "connect_to_mongo",
    "close_mongo_connection",
    "mongo_manager",  # NEW: MongoDB manager instance
    "Base",
    "AsyncSessionLocal",
    "logger",
    "test_postgres_connection",
    "test_mongo_connection"
]