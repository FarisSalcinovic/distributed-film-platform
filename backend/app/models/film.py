# backend/app/models/film.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import uuid


class FilmLocation(BaseModel):
    id: str
    film_id: int  # TMDB ID
    location_name: str
    city_id: str  # GeoDB city ID
    country_code: str
    latitude: float
    longitude: float
    scene_description: Optional[str] = None


class FilmData(BaseModel):
    id: str = str(uuid.uuid4())
    tmdb_id: int
    title: str
    original_title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    popularity: float
    vote_average: float
    vote_count: int
    genres: List[str] = []
    production_countries: List[str] = []
    spoken_languages: List[str] = []
    locations: List[FilmLocation] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()