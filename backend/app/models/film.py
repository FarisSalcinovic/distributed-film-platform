# backend/app/models/film.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import uuid


class FilmLocation(BaseModel):
    """Film location data from TMDB API"""
    film_id: int
    title: str
    release_date: Optional[str]
    locations: List[str]  # List of filming locations
    popularity: float
    vote_average: float
    genres: List[str]
    tmdb_data: dict  # Raw TMDB data
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()


class FilmData(BaseModel):
    """City data from GEO API"""
    city_id: int
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    population: Optional[int]
    elevation: Optional[int]
    timezone: str
    geo_data: dict  # Raw GEO data
    created_at: datetime = datetime.utcnow()