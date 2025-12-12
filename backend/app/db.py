from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import asyncio

# --- PostgreSQL Konekcija ---

# 1. Asinkroni engine za FastAPI
async_engine = create_async_engine(settings.POSTGRES_URL, echo=True, future=True)

# 2. Sync engine samo za kreiranje tabela
sync_engine = create_engine(settings.POSTGRES_URL_SYNC)

# 3. Asinkrona Sesija
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# 4. Sync Sesija za kreiranje tabela (samo startup)
SyncSessionLocal = sessionmaker(
    sync_engine, expire_on_commit=False
)

# 5. Bazni Model
Base = declarative_base()

# 6. Async DB Dependency
async def get_db():
    """Yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 7. Funkcija za kreiranje tabela
def create_all_tables_sync():
    """Creates all tables using sync engine."""
    Base.metadata.create_all(bind=sync_engine)
    print("✓ PostgreSQL tables created successfully")

async def create_all_tables():
    """Async wrapper for table creation."""
    # Koristimo run_in_executor za sync operaciju
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, create_all_tables_sync)

# --- MongoDB Konekcija ---
mongodb_client: AsyncIOMotorClient = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Returns the global MongoDB client instance."""
    return mongodb_client

async def connect_to_mongo():
    """Establishes the connection to MongoDB upon application startup."""
    global mongodb_client
    print(f"Connecting to MongoDB at {settings.MONGO_URL}...")
    try:
        mongodb_client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000
        )
        await mongodb_client.admin.command('ping')
        print("✓ MongoDB connection successful!")
    except Exception as e:
        print(f"✗ Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Closes the MongoDB connection upon application shutdown."""
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed.")