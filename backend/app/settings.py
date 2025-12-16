# backend/app/settings.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "film_platform")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgresdb")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    # MongoDB
    MONGO_INITDB_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME", "mongo_admin")
    MONGO_INITDB_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "mongo_admin_password")
    MONGO_DB: str = os.getenv("MONGO_DB", "film_data")

    # Redis & Celery
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "redispass")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://:redispass@redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://:redispass@redis:6379/0")

    # API Keys
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")

    # App
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URI(self):
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/{self.MONGO_DB}?authSource=admin"


settings = Settings()