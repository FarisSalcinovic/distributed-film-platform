# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Postavljanje putanje za .env datoteku i ignoriranje viška varijabli
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # -------------------------------
    # JWT & SECURITY SETTINGS
    # -------------------------------
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str  # NEW: Added for refresh tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Changed from 30 to 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------------
    # DATABASE SETTINGS
    # -------------------------------
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # MongoDB
    MONGO_DB: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_INITDB_ROOT_USERNAME: str  # Changed from Optional to required
    MONGO_INITDB_ROOT_PASSWORD: str  # Changed from Optional to required

    # Redis/Celery
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: str

    # -------------------------------
    # EXTERNAL API KEYS
    # -------------------------------
    TMDB_API_KEY: str
    OMDB_API_KEY: str

    # -------------------------------
    # APPLICATION SETTINGS
    # -------------------------------
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # "development" | "production"

    # -------------------------------
    # COMPUTED PROPERTIES
    # -------------------------------

    @property
    def POSTGRES_URL(self) -> str:
        """Kreira kompletan PostgreSQL URL"""
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URL_SYNC(self) -> str:
        """Kreira kompletan PostgreSQL URL za sync operacije (potrebno za auth)"""
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        """Kreira kompletan MongoDB URL s autentifikacijom"""
        password = quote_plus(self.MONGO_INITDB_ROOT_PASSWORD)
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{password}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"

    @property
    def MONGO_URL_NO_AUTH(self) -> str:
        """Kreira MongoDB URL bez autentifikacije (za inicijalne setup operacije)"""
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Kreira kompletan Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def TMDB_API_BASE_URL(self) -> str:
        """Base URL za TMDB API"""
        return "https://api.themoviedb.org/3"

    @property
    def OMDB_API_BASE_URL(self) -> str:
        """Base URL za OMDB API"""
        return "http://www.omdbapi.com"

    @property
    def FRONTEND_URL(self) -> str:
        """Base URL za frontend aplikaciju"""
        if self.ENVIRONMENT == "production":
            return "https://yourdomain.com"
        return "http://localhost:3000"

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
        if not self.OMDB_API_KEY or self.OMDB_API_KEY == "your_omdb_api_key_here":
            raise ValueError("Please set a valid OMDB_API_KEY in .env file")

        return True


# Inicijalizacija i globalna dostupnost
try:
    settings = Settings()
    settings.validate_settings()
    print(f"✓ Settings loaded successfully for {settings.ENVIRONMENT} environment")
except Exception as e:
    print(f"✗ Error loading settings: {e}")


    # Fallback settings za development
    class FallbackSettings:
        ENVIRONMENT = "development"
        DEBUG = True
        SECRET_KEY = "development-secret-key-change-in-production"
        REFRESH_SECRET_KEY = "development-refresh-key-change-in-production"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60
        REFRESH_TOKEN_EXPIRE_DAYS = 7

        @property
        def POSTGRES_URL_SYNC(self):
            return "postgresql://user_admin:user_admin_password@postgresdb:5432/user_admin"

        @property
        def MONGO_URL(self):
            return "mongodb://mongo_admin:mongo_admin_password@mongodb:27017/film_data?authSource=admin"


    settings = FallbackSettings()
    print("⚠️  Using fallback settings for development")