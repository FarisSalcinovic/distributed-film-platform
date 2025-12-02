from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv


# Uvozimo konekcije i modele iz internih modula
# 'create_all_tables' i konekcije na Mongo su definirane u db.py
from .db import create_all_tables, connect_to_mongo, close_mongo_connection
from .models import user

# Učitavanje varijabli okoline (važno za lokalni rad)
load_dotenv()

# Inicijalizacija FastAPI Aplikacije
app = FastAPI(
    title="Film Data Aggregation Platform",
    description="REST API for combined Film Box Office and Rating analysis.",
    version="0.1.0",
)


# ----------------------------------------------------------------------
## LIFESPAN HANDLERI (Startup i Shutdown)
# ----------------------------------------------------------------------

@app.on_event("startup")
async def startup_events():
    """Handler koji se izvršava pri pokretanju aplikacije."""

    # 1. Kreiranje SQL tablica (PostgreSQL)
    # Ovo osigurava da tablica 'users' postoji.
    print("Creating PostgreSQL tables...")
    await create_all_tables()

    # 2. Povezivanje na MongoDB
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_events():
    """Handler koji se izvršava prilikom gašenja aplikacije."""

    # Zatvaranje MongoDB konekcije
    await close_mongo_connection()


# ----------------------------------------------------------------------
## HEALTH CHECK RUTA
# ----------------------------------------------------------------------

@app.get("/", tags=["Status"])
def read_root():
    """
    Provjerava status aplikacije i uspostavljenu konekciju na baze podataka.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "online",
            "message": "Film Data Platform Running - DBs ready for connections."
        }
    )

# ----------------------------------------------------------------------
## BUDUĆI KORAK: UKLJUČIVANJE ROUTERA
# ----------------------------------------------------------------------

# Ovdje ćete u sljedećim koracima uključivati routere (module)
# nakon što ih kreirate, npr.:

# from .routers import auth, etl, analytics
# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(etl.router, prefix="/etl", tags=["Data Ingestion (ETL)"])
# app.include_router(analytics.router, prefix="/analytics", tags=["Core Analytics"])