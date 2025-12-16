import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Postavljanje putanje za .env datoteku i ignoriranje viška varijabli
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # -------------------------------
    # JWT & SECURITY SETTINGS
    # -------------------------------
    SECRET_KEY: str = "development-secret-key-change-in-production"
    REFRESH_SECRET_KEY: str = "development-refresh-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------------
    # DATABASE SETTINGS
    # -------------------------------
    # PostgreSQL
    POSTGRES_USER: str = "user_admin"
    POSTGRES_PASSWORD: str = "user_admin_password"
    POSTGRES_DB: str = "user_admin"
    POSTGRES_HOST: str = "postgresdb"
    POSTGRES_PORT: int = 5432

    # MongoDB
    MONGO_DB: str = "film_data"
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: int = 27017
    MONGO_INITDB_ROOT_USERNAME: str = "mongo_admin"
    MONGO_INITDB_ROOT_PASSWORD: str = "mongo_admin_password"

    # Redis/Celery
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_password"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # -------------------------------
    # EXTERNAL API KEYS
    # -------------------------------
    TMDB_API_KEY: str = "ff876caeb92a702d0e364f802726ad30"
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_ACCESS_TOKEN: str = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmZjg3NmNhZWI5MmE3MDJkMGUzNjRmODAyNzI2YWQzMCIsIm5iZiI6MTc2NDYyNjQ5Ny45ODIsInN1YiI6IjY5MmUxMDQxNmY4YTZiMDgyZWRjMzM5MSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.DkZ59coDgSCIH0QMq1UMfEAlkfdHYOVnaIVe6gMHlGc"

    GEOAPIFY_API_KEY: str = "7744923d8fc4473ebda8031d3d2f69b7"
    GEOAPIFY_BASE_URL: str = "https://api.geoapify.com/v1"

    # -------------------------------
    # APPLICATION SETTINGS
    # -------------------------------
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # -------------------------------
    # COMPUTED PROPERTIES
    # -------------------------------

    @property
    def POSTGRES_URL(self) -> str:
        """Kreira kompletan PostgreSQL URL za async"""
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URL_SYNC(self) -> str:
        """Kreira kompletan PostgreSQL URL za sync operacije"""
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        """Kreira kompletan MongoDB URL s autentifikacijom"""
        password = quote_plus(self.MONGO_INITDB_ROOT_PASSWORD)
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{password}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"

    @property
    def MONGO_URL_NO_AUTH(self) -> str:
        """Kreira MongoDB URL bez autentifikacije"""
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Kreira kompletan Redis URL sa passwordom"""
        password = quote_plus(self.REDIS_PASSWORD)
        return f"redis://:{password}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def TMDB_API_BASE_URL(self) -> str:
        """Base URL za TMDB API"""
        return self.TMDB_BASE_URL

    @property
    def FRONTEND_URL(self) -> str:
        """Base URL za frontend aplikaciju"""
        if self.ENVIRONMENT == "production":
            return "https://yourdomain.com"
        return "http://localhost:3000"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Postavite CELERY_BROKER_URL i CELERY_RESULT_BACKEND na osnovu REDIS_URL
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"{self.REDIS_URL}/0"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"{self.REDIS_URL}/0"

    # -------------------------------
    # VALIDATION
    # -------------------------------
    def validate_settings(self):
        """Validira postavke prije korištenja"""
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        if len(self.REFRESH_SECRET_KEY) < 32:
            raise ValueError("REFRESH_SECRET_KEY must be at least 32 characters")

        # Provjera API ključeva
        if not self.TMDB_API_KEY or self.TMDB_API_KEY == "your_tmdb_api_key_here":
            raise ValueError("Please set a valid TMDB_API_KEY in .env file")

        # Provjera Geoapify ključa
        if not self.GEOAPIFY_API_KEY or self.GEOAPIFY_API_KEY == "your_geoapify_api_key_here":
            print("⚠️  Warning: GEOAPIFY_API_KEY not set. Geoapify ETL will not work.")

        return True


# Inicijalizacija i globalna dostupnost
try:
    settings = Settings()
    settings.validate_settings()
    print(f"✓ Settings loaded successfully for {settings.ENVIRONMENT} environment")
    print(f"✓ TMDB API Key: {settings.TMDB_API_KEY[:10]}...")
    print(f"✓ Geoapify API Key: {settings.GEOAPIFY_API_KEY[:10]}...")
    print(f"✓ Database URLs configured")
except Exception as e:
    print(f"✗ Error loading settings: {e}")
    # Bez fallback klase - Pydantic će koristiti default vrijednosti
    raise