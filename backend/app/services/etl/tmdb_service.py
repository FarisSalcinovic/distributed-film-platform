import httpx
from typing import List, Dict, Any
from datetime import datetime
import logging

from sqlalchemy.util.concurrency import asyncio

from ...config import settings

logger = logging.getLogger(__name__)


class TMDBService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.access_token = settings.TMDB_ACCESS_TOKEN

        # Koristi API KEY u query parametru za v3 API
        # Koristi ACCESS TOKEN u headeru za v4 API (ako je potrebno)
        self.timeout = httpx.Timeout(30.0, connect=10.0)

        logger.info(f"TMDBService initialized with API key: {self.api_key[:10]}...")

    async def fetch_trending_movies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending movies from TMDB - ISPRAVLJENO!"""
        try:
            logger.info(f"Fetching trending movies from TMDB, limit: {limit}")

            # ISPRAVLJENO: Koristi api_key u query parametru
            url = f"{self.base_url}/trending/movie/week"
            params = {
                "api_key": self.api_key,  # OVO JE KLJUČNO - NE KORISTI Bearer token!
                "language": "en-US",
                "page": 1
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 401:
                    logger.error(f"TMDB 401 Unauthorized. API Key: {self.api_key[:10]}...")
                    logger.error("Provjeri da li je TMDB_API_KEY ispravan u .env fajlu")
                    return []

                response.raise_for_status()
                data = response.json()

                movies = data.get("results", [])[:limit]
                logger.info(f"Fetched {len(movies)} trending movies from TMDB")
                return movies

        except httpx.HTTPStatusError as e:
            logger.error(f"TMDB API error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching TMDB data: {e}")
            return []

    async def fetch_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Fetch detailed movie information including credits"""
        try:
            # Get movie details
            details_url = f"{self.base_url}/movie/{movie_id}"
            credits_url = f"{self.base_url}/movie/{movie_id}/credits"

            params = {
                "api_key": self.api_key,
                "language": "en-US"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Make parallel requests
                details_response, credits_response = await asyncio.gather(
                    client.get(details_url, params=params),
                    client.get(credits_url, params=params)
                )

                details_response.raise_for_status()
                movie_data = details_response.json()

                if credits_response.status_code == 200:
                    credits_data = credits_response.json()
                    movie_data["credits"] = credits_data
                else:
                    movie_data["credits"] = {}

                return movie_data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching movie details {movie_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching movie details {movie_id}: {e}")
            return {}

    async def extract_film_locations(self, movie_data: Dict[str, Any]) -> List[str]:
        """Extract filming locations from movie data"""
        locations = []

        # Koristi production countries iz TMDB podataka
        production_countries = movie_data.get("production_countries", [])
        for country in production_countries[:2]:
            country_name = country.get("name", "")
            if country_name:
                locations.append(f"Production in {country_name}")

        # Dodaj generic lokacije
        if movie_data.get("original_language"):
            lang = movie_data["original_language"]
            if lang == "en":
                locations.append("Hollywood studios")
            elif lang == "hi":
                locations.append("Bollywood studios")
            elif lang == "ko":
                locations.append("Korean film studios")

        if not locations:
            locations.append("Location data not available")

        return locations

    async def transform_movie_data(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw TMDB data to our schema"""
        try:
            locations = await self.extract_film_locations(movie_data)

            # Extract credits if available
            credits = movie_data.get("credits", {})
            director = self._extract_director(credits)
            cast = self._extract_cast(credits)

            # Extract genres
            genres = []
            for genre in movie_data.get("genres", []):
                if isinstance(genre, dict):
                    genres.append(genre.get("name", ""))
                else:
                    genres.append(str(genre))

            # Extract production countries
            production_countries = []
            for country in movie_data.get("production_countries", []):
                if isinstance(country, dict):
                    production_countries.append(country.get("name", ""))

            # Extract spoken languages
            spoken_languages = []
            for lang in movie_data.get("spoken_languages", []):
                if isinstance(lang, dict):
                    spoken_languages.append(lang.get("name", ""))

            return {
                "film_id": movie_data.get("id"),
                "title": movie_data.get("title"),
                "original_title": movie_data.get("original_title"),
                "release_date": movie_data.get("release_date"),
                "overview": movie_data.get("overview", "")[:500],
                "popularity": movie_data.get("popularity", 0),
                "vote_average": movie_data.get("vote_average", 0),
                "vote_count": movie_data.get("vote_count", 0),
                "genres": genres,
                "production_countries": production_countries,
                "spoken_languages": spoken_languages,
                "runtime": movie_data.get("runtime"),
                "budget": movie_data.get("budget"),
                "revenue": movie_data.get("revenue"),
                "original_language": movie_data.get("original_language"),
                "poster_path": movie_data.get("poster_path"),
                "backdrop_path": movie_data.get("backdrop_path"),
                "adult": movie_data.get("adult", False),
                "video": movie_data.get("video", False),
                "locations": locations,
                "director": director,
                "cast": cast,
                "tmdb_data": {
                    "id": movie_data.get("id"),
                    "imdb_id": movie_data.get("imdb_id"),
                    "homepage": movie_data.get("homepage"),
                    "status": movie_data.get("status"),
                    "tagline": movie_data.get("tagline")
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error transforming movie data: {e}")
            # Vrati barem osnovne podatke
            return {
                "film_id": movie_data.get("id"),
                "title": movie_data.get("title", "Unknown"),
                "release_date": movie_data.get("release_date"),
                "overview": movie_data.get("overview", "")[:500],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

    def _extract_director(self, credits_data: Dict[str, Any]) -> str:
        """Extract director from credits"""
        if not credits_data:
            return "Unknown"

        crew = credits_data.get("crew", [])
        for person in crew:
            if person.get("job") == "Director":
                return person.get("name", "Unknown")
        return "Unknown"

    def _extract_cast(self, credits_data: Dict[str, Any]) -> List[str]:
        """Extract top 5 cast members"""
        if not credits_data:
            return []

        cast = credits_data.get("cast", [])
        return [person.get("name", "") for person in cast[:5] if person.get("name")]

    async def test_connection(self) -> bool:
        """Testira konekciju sa TMDB API"""
        try:
            url = f"{self.base_url}/configuration"
            params = {"api_key": self.api_key}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    logger.info("✓ TMDB API connection successful")
                    return True
                else:
                    logger.error(f"✗ TMDB API connection failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"✗ TMDB API connection error: {e}")
            return False


# Singleton instance
tmdb_service = TMDBService()