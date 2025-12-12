# backend/app/services/etl/tmdb_service.py
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import asyncio
from ...config import settings
import logging

logger = logging.getLogger(__name__)


class TMDBServices:
    # backend/app/services/etl/tmdb_service.py - ažurirajte __init__ metodu:
    def __init__(self):
        self.base_url = "https://api.themoviedb.org/3"  # Hardkodirajte ili koristite settings
        self.api_key = settings.TMDB_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def get_trending_movies(self, time_window: str = "day", limit: int = 20) -> List[Dict]:
        """Dohvata trenutno popularne filmove"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/trending/movie/{time_window}",
                    headers=self.headers,
                    params={"language": "en-US"}
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                logger.info(f"Fetched {len(results)} trending movies")

                # Enrich with details for top movies
                enriched_movies = []
                for movie in results[:min(limit, 10)]:  # Get details for top 10
                    try:
                        details = await self.get_movie_details(movie["id"])
                        movie.update(details)
                        enriched_movies.append(movie)
                    except Exception as e:
                        logger.error(f"Error getting details for movie {movie['id']}: {e}")
                        enriched_movies.append(movie)

                return enriched_movies[:limit]

        except httpx.RequestError as e:
            logger.error(f"Request error fetching trending movies: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching trending movies: {e}")
            raise

    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Dohvata detalje o filmu"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/movie/{movie_id}",
                    headers=self.headers,
                    params={
                        "language": "en-US",
                        "append_to_response": "credits,release_dates"
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Extract relevant information
                movie_details = {
                    "tmdb_id": data.get("id"),
                    "title": data.get("title"),
                    "original_title": data.get("original_title"),
                    "overview": data.get("overview"),
                    "release_date": data.get("release_date"),
                    "runtime": data.get("runtime"),
                    "budget": data.get("budget"),
                    "revenue": data.get("revenue"),
                    "popularity": data.get("popularity"),
                    "vote_average": data.get("vote_average"),
                    "vote_count": data.get("vote_count"),
                    "status": data.get("status"),
                    "tagline": data.get("tagline"),
                    "genres": [genre["name"] for genre in data.get("genres", [])],
                    "genre_ids": [genre["id"] for genre in data.get("genres", [])],
                    "production_companies": [
                        company["name"] for company in data.get("production_companies", [])
                    ],
                    "production_countries": [
                        country["name"] for country in data.get("production_countries", [])
                    ],
                    "spoken_languages": [
                        lang["name"] for lang in data.get("spoken_languages", [])
                    ],
                    "cast": [
                        {
                            "name": cast["name"],
                            "character": cast["character"],
                            "order": cast["order"]
                        }
                        for cast in data.get("credits", {}).get("cast", [])[:5]
                    ] if data.get("credits") else [],
                    "crew": [
                        {
                            "name": crew["name"],
                            "job": crew["job"]
                        }
                        for crew in data.get("credits", {}).get("crew", [])[:3]
                        if crew["job"] in ["Director", "Producer", "Screenplay"]
                    ] if data.get("credits") else []
                }

                return movie_details

        except httpx.RequestError as e:
            logger.error(f"Request error fetching movie details {movie_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching movie details {movie_id}: {e}")
            raise

    async def search_movies(self, query: str, year: Optional[int] = None, page: int = 1) -> Dict:
        """Pretraga filmova"""
        try:
            params = {
                "query": query,
                "language": "en-US",
                "page": page,
                "include_adult": False
            }
            if year:
                params["year"] = year

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/search/movie",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()

        except httpx.RequestError as e:
            logger.error(f"Request error searching movies: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            raise

    async def get_movie_locations(self, movie_id: int) -> List[Dict]:
        """Dohvata lokacije snimanja filma (ako su dostupne)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/movie/{movie_id}/watch/providers",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                # Note: TMDB doesn't have direct location data
                # This is a placeholder for future integration
                return []

        except Exception as e:
            logger.warning(f"Could not fetch locations for movie {movie_id}: {e}")
            return []

    async def get_movie_keywords(self, movie_id: int) -> List[str]:
        """Dohvata ključne riječi za film"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/movie/{movie_id}/keywords",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                return [keyword["name"] for keyword in data.get("keywords", [])]

        except Exception as e:
            logger.warning(f"Could not fetch keywords for movie {movie_id}: {e}")
            return []

    async def get_movie_recommendations(self, movie_id: int, limit: int = 5) -> List[Dict]:
        """Dohvata preporučene filmove"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/movie/{movie_id}/recommendations",
                    headers=self.headers,
                    params={"language": "en-US", "page": 1}
                )
                response.raise_for_status()
                data = response.json()

                return data.get("results", [])[:limit]

        except Exception as e:
            logger.warning(f"Could not fetch recommendations for movie {movie_id}: {e}")
            return []