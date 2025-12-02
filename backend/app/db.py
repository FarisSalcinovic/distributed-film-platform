# backend/app/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import asyncio

# --- PostgreSQL Konekcija (Za Korisnike/Logove) ---

async def create_all_tables(max_tries: int = 10, delay: float = 3):
    """Creates all tables defined by SQLAlchemy models with a retry mechanism."""
    for attempt in range(max_tries):
        try:
            async with engine.begin() as conn:
                print(f"Attempt {attempt + 1}: Creating/checking PostgreSQL tables...")
                # Potrebno je osigurati da su svi modeli (npr. User) importani!
                await conn.run_sync(Base.metadata.create_all)
                print("PostgreSQL tables successfully created/checked.")
                return # Uspjeh, izlazak iz funkcije
        except Exception as e:
            print(f"PostgreSQL connection failed on attempt {attempt + 1}: {e}")
            if attempt < max_tries - 1:
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                # Nismo uspjeli nakon svih pokušaja, bacamo grešku.
                raise ConnectionError("Failed to connect to PostgreSQL after multiple retries.") from e

# 1. Kreiranje Asinkronog Engine-a
engine = create_async_engine(settings.POSTGRES_URL, echo=False) # echo=True za debug

# 2. Asinkrona Sesija (Ključno za FastAPI)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 3. Bazni Model za Tablice
Base = declarative_base()

# Funkcija za dobivanje sesije (Dependency Injection)
async def get_db():
    """Yields a database session that closes automatically."""
    async with AsyncSessionLocal() as session:
        yield session

# Funkcija za kreiranje svih tablica (poziva se pri pokretanju aplikacije)
async def create_all_tables():
    """Creates all tables defined by SQLAlchemy models in the database."""
    async with engine.begin() as conn:
        # Potrebno je osigurati da su svi modeli (npr. User) importani prije ovog poziva!
        await conn.run_sync(Base.metadata.create_all)


# --- MongoDB Konekcija (Za Filmske Podatke) ---

mongodb_client: AsyncIOMotorClient = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Returns the global MongoDB client instance."""
    return mongodb_client


# backend/app/db.py (dio za MongoDB konekciju)
async def connect_to_mongo():
    """Establishes the connection to MongoDB upon application startup."""
    global mongodb_client
    print(f"Connecting to MongoDB at {settings.MONGO_URL}...")
    try:
        # Postavljanje klijenta - koristimo MONGO_URL property
        mongodb_client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000
        )

        # Provjera konekcije
        await mongodb_client.admin.command('ping')
        print("MongoDB connection successful!")

    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        # U produkcijskom okruženju ovdje bi trebala biti fatalna greška

async def close_mongo_connection():
    """Closes the MongoDB connection upon application shutdown."""
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed.")