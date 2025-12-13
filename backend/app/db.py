# backend/app/db.py
import logging
from typing import Optional
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from motor.motor_asyncio import AsyncIOMotorClient

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
        # Koristimo run_in_executor za sync operaciju
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_all_tables_sync)
    except Exception as e:
        logger.error(f"Error in async table creation: {e}")
        raise


# --- MongoDB Konekcija ---
mongodb_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    """Get MongoDB client - SYNC version for Celery tasks"""
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10
        )
        logger.info(f"MongoDB client created for URL: {settings.MONGO_URL}")
        return client

    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return None


async def connect_to_mongo():
    """Establishes the connection to MongoDB upon application startup."""
    global mongodb_client
    logger.info(f"Connecting to MongoDB at {settings.MONGO_URL}...")

    try:
        mongodb_client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
        await mongodb_client.admin.command('ping')
        logger.info("✓ MongoDB connection successful!")
    except Exception as e:
        logger.error(f"✗ Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Closes the MongoDB connection upon application shutdown."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        mongodb_client = None
        logger.info("MongoDB connection closed.")


# --- Helper funkcije za testiranje ---
async def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        logger.info("✓ PostgreSQL connection test successful")
        return True
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection test failed: {e}")
        return False


async def test_mongo_connection():
    """Test MongoDB connection"""
    try:
        client = get_mongo_client()
        if client:
            await client.admin.command('ping')
            logger.info("✓ MongoDB connection test successful")
            return True
        return False
    except Exception as e:
        logger.error(f"✗ MongoDB connection test failed: {e}")
        return False


# Export za Celery taskove
def get_mongo_client_sync():
    """Sync MongoDB client for Celery tasks"""
    try:
        from pymongo import MongoClient
        import urllib.parse

        # Parse MONGO_URL za pymongo
        from .config import settings

        # Pymongo expects different URL format
        mongo_user = settings.MONGO_INITDB_ROOT_USERNAME
        mongo_pass = urllib.parse.quote_plus(settings.MONGO_INITDB_ROOT_PASSWORD)
        mongo_host = settings.MONGO_HOST
        mongo_db = settings.MONGO_DB

        mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/{mongo_db}?authSource=admin"

        client = MongoClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )

        # Test connection
        client.admin.command('ping')
        logger.info(f"✓ Sync MongoDB client created for Celery")
        return client

    except Exception as e:
        logger.error(f"✗ Sync MongoDB client error: {e}")
        return None


# Export important functions
__all__ = [
    "get_db",
    "create_all_tables",
    "get_mongo_client",
    "get_mongo_client_sync",  # Za Celery
    "connect_to_mongo",
    "close_mongo_connection",
    "Base",
    "AsyncSessionLocal",
    "logger"
]