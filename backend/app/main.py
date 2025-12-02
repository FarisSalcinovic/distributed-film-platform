# backend/app/main.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import logging

# Uvozimo konekcije i modele iz internih modula
from .db import create_all_tables, connect_to_mongo, close_mongo_connection, Base, engine

try:
    from .api.v1 import auth

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("Auth router not available yet - will be added later")

# Učitavanje varijabli okoline
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicijalizacija FastAPI Aplikacije
app = FastAPI(
    title="Distributed Film Platform API",
    description="REST API for film data aggregation and analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ----------------------------------------------------------------------
## CORS MIDDLEWARE
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI itself
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
## LIFESPAN HANDLERI (Startup i Shutdown)
# ----------------------------------------------------------------------

@app.on_event("startup")
async def startup_events():
    """Handler koji se izvršava pri pokretanju aplikacije."""
    logger.info("Starting up Film Data Platform...")

    # 1. Kreiranje SQL tablica (PostgreSQL)
    logger.info("Creating PostgreSQL tables...")
    try:
        await create_all_tables()
        logger.info("PostgreSQL tables created successfully")
    except Exception as e:
        logger.error(f"Error creating PostgreSQL tables: {e}")

    # 2. Povezivanje na MongoDB
    try:
        await connect_to_mongo()
        logger.info("MongoDB connection established")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")


@app.on_event("shutdown")
async def shutdown_events():
    """Handler koji se izvršava prilikom gašenja aplikacije."""
    logger.info("Shutting down Film Data Platform...")

    # Zatvaranje MongoDB konekcije
    try:
        await close_mongo_connection()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")


# ----------------------------------------------------------------------
## ROUTERS
# ----------------------------------------------------------------------

# Include auth router if available
if AUTH_AVAILABLE:
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    logger.info("Auth router included")


# ----------------------------------------------------------------------
## STATUS RUTE
# ----------------------------------------------------------------------

@app.get("/", tags=["Status"])
def read_root():
    """Osnovni status aplikacije."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "online",
            "service": "Distributed Film Platform API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "authentication": AUTH_AVAILABLE,
                "database": "PostgreSQL + MongoDB",
                "broker": "Redis (Celery)",
                "apis": ["TMDB", "OMDB"]
            }
        }
    )


@app.get("/health", tags=["Status"])
async def health_check():
    """Detaljna provjera zdravlja aplikacije."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            # Ovdje kasnije dodati provjere za DB, Redis, itd.
        }
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )


@app.get("/api/status", tags=["Status"])
def api_status():
    """Status API endpointova."""
    endpoints = [
        {"path": "/api/v1/auth/register", "method": "POST", "description": "User registration"},
        {"path": "/api/v1/auth/login", "method": "POST", "description": "User login"},
        {"path": "/api/v1/auth/refresh", "method": "POST", "description": "Refresh token"},
        {"path": "/api/v1/auth/logout", "method": "POST", "description": "User logout"},
        {"path": "/api/health", "method": "GET", "description": "Health check"},
    ]

    return {
        "api": "Distributed Film Platform API v1",
        "endpoints": endpoints,
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }