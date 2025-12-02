# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Postavljanje putanje za .env datoteku i ignoriranje viška varijabli
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Generalne postavke i Sigurnost (Modul B1)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Baze Podataka
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    MONGO_DB: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_INITDB_ROOT_USERNAME: Optional[str] = None
    MONGO_INITDB_ROOT_PASSWORD: Optional[str] = None

    # Celery/Redis
    CELERY_BROKER_URL: str

    # Vanjski API ključevi (Modul A1)
    TMDB_API_KEY: str
    OMDB_API_KEY: str

    # Kompletni URL-ovi kao properties
    @property
    def POSTGRES_URL(self) -> str:
        """Kreira kompletan PostgreSQL URL"""
        password = quote_plus(self.POSTGRES_PASSWORD)  # Enkodiranje specijalnih karaktera
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        """Kreira kompletan MongoDB URL"""
        if self.MONGO_INITDB_ROOT_USERNAME and self.MONGO_INITDB_ROOT_PASSWORD:
            password = quote_plus(self.MONGO_INITDB_ROOT_PASSWORD)
            return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{password}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"


# Inicijalizacija i globalna dostupnost
settings = Settings()