import httpx
from typing import List, Dict, Any
from datetime import datetime
import logging

from celery.backends import mongodb
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

    async def fetch_popular_movies_by_region(
            self,
            region: str,
            limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Dohvata trenutno najpopularnije filmove za zadanu drzavu (ISO code),
        koristeci TMDB Discover API filtrirano po production country.
        """

        try:
            logger.info(f"Fetching top {limit} popular movies for region: {region}")

            # Discover endpoint - filter by production country
            url = f"{self.base_url}/discover/movie"
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "with_origin_country": region.upper(),  # TMDB production country filter
                "vote_count.gte": 20,  # minimum glasova da izbjegnemo nepotpune podatke
                "page": 1
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    logger.error(f"TMDB discover error {response.status_code}: {response.text}")
                    return []

                data = response.json()
                movies = data.get("results", [])[:limit]

                # Ako dodje 0 filmova iz regiona, moze fallback na trending
                if not movies:
                    logger.warning(f"No regional movies for {region}, falling back to trending")
                    movies = await self.fetch_trending_movies(limit=limit)

                logger.info(f"Found {len(movies)} movies for region {region}")
                return movies

        except Exception as e:
            logger.error(f"Error fetching popular for region {region}: {e}")
            # Fallback na trending
            return await self.fetch_trending_movies(limit=limit)

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

    async def save_films_to_mongodb(self, films_data: List[Dict[str, Any]]):
        """
        Snima filmove u MongoDB
        """
        try:
            if not mongodb.db:
                await mongodb.connect()

            films_collection = mongodb.db["films"]
            saved_count = 0
            updated_count = 0

            for film_data in films_data:
                # Transformuj podatke u naš format
                film = await self.transform_movie_data(film_data)

                # Dodaj timestamp
                film["fetched_at"] = datetime.utcnow()
                film["data_source"] = "tmdb_api"

                # Provjeri da li film već postoji
                existing = await films_collection.find_one({"film_id": film["film_id"]})

                if existing:
                    # Update postojećeg filma
                    await films_collection.update_one(
                        {"film_id": film["film_id"]},
                        {"$set": {**film, "updated_at": datetime.utcnow()}}
                    )
                    updated_count += 1
                else:
                    # Insert novi film
                    await films_collection.insert_one(film)
                    saved_count += 1

            logger.info(f"✅ Saved {saved_count} new films, updated {updated_count} existing films")
            return {"saved": saved_count, "updated": updated_count, "total": len(films_data)}

        except Exception as e:
            logger.error(f"❌ Error saving films to MongoDB: {e}")
            raise

    async def save_regional_films_to_mongodb(self, region: str, films_data: List[Dict[str, Any]]):
        """
        Snima regionalne filmove sa dodatnim metadata
        """
        try:
            if not mongodb.db:
                await mongodb.connect()

            regional_collection = mongodb.db["regional_films"]

            # Kreiraj regionalni dokument
            regional_doc = {
                "region": region.upper(),
                "fetch_date": datetime.utcnow(),
                "total_films": len(films_data),
                "films": [],
                "stats": {
                    "avg_vote": sum(f.get("vote_average", 0) for f in films_data) / len(
                        films_data) if films_data else 0,
                    "avg_popularity": sum(f.get("popularity", 0) for f in films_data) / len(
                        films_data) if films_data else 0,
                    "latest_release": max(
                        [f.get("release_date", "1900-01-01") for f in films_data]) if films_data else None
                }
            }

            # Dodaj filmove
            for film in films_data[:10]:  # Snimi samo top 10
                film_doc = {
                    "film_id": film.get("id"),
                    "title": film.get("title"),
                    "vote_average": film.get("vote_average"),
                    "popularity": film.get("popularity"),
                    "poster_path": film.get("poster_path"),
                    "release_date": film.get("release_date")
                }
                regional_doc["films"].append(film_doc)

            # Snimi u MongoDB
            await regional_collection.update_one(
                {"region": region.upper()},
                {"$set": regional_doc},
                upsert=True
            )

            logger.info(f"✅ Saved regional films for {region} to MongoDB")
            return regional_doc

        except Exception as e:
            logger.error(f"❌ Error saving regional films: {e}")
            raise

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

    # DODAJTE OVO U TMDBService KLASU (iznad linije "Singleton instance"):
    # U tmdb_service.py, zamijenite fetch_popular_movies_by_region:

    # DODAJTE OVE METODE U TMDBService KLASU:

    async def fetch_regional_popular_movies(self, region: str = "US", limit: int = 3) -> List[Dict[str, Any]]:
        """
        Vraća stvarno regionalno popularne filmove
        Kombinacija: discover API + trending + production countries
        """
        try:
            logger.info(f"Fetching truly regional movies for: {region}, limit: {limit}")

            all_movies = []

            # STRATEGIJA 1: Discover sa original_language
            language_movies = await self._fetch_by_original_language(region, limit)
            all_movies.extend(language_movies)

            # STRATEGIJA 2: Ako nema dovoljno, probaj sa production_countries
            if len(all_movies) < limit:
                country_movies = await self._fetch_by_production_country(region, limit - len(all_movies))
                all_movies.extend(country_movies)

            # STRATEGIJA 3: Ako i dalje nema dovoljno, koristi trending ali označi
            if len(all_movies) < limit:
                trending_movies = await self.fetch_trending_movies(limit - len(all_movies))
                for movie in trending_movies:
                    movie["region_source"] = "global_fallback"
                all_movies.extend(trending_movies)

            # Ukloni duplikate i označi region
            seen_ids = set()
            regional_movies = []

            for movie in all_movies:
                if movie.get("id") and movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    movie["region"] = region
                    regional_movies.append(movie)

            logger.info(f"✓ Regional strategy found {len(regional_movies)} movies for {region}")
            return regional_movies[:limit]

        except Exception as e:
            logger.error(f"Error in regional fetch for {region}: {e}")
            # Fallback na trending
            return await self.fetch_trending_movies(limit)

    async def _fetch_by_original_language(self, region: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch movies by original language of the region"""
        language_map = {
            "US": "en", "GB": "en", "AU": "en", "CA": "en", "IE": "en",
            "FR": "fr", "BE": "fr", "CH": "fr", "LU": "fr",
            "DE": "de", "AT": "de", "CH": "de", "LU": "de",
            "ES": "es", "MX": "es", "AR": "es", "CO": "es", "PE": "es",
            "IT": "it", "CH": "it",
            "JP": "ja",
            "KR": "ko",
            "CN": "zh", "TW": "zh", "HK": "zh", "SG": "zh",
            "RU": "ru", "BY": "ru", "KZ": "ru", "UA": "ru",
            "BR": "pt", "PT": "pt",
            "IN": "hi", "PK": "ur",
            "TR": "tr",
            "AR": "ar", "EG": "ar", "SA": "ar"
        }

        language = language_map.get(region.upper(), "en")

        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": 1,
                "with_original_language": language,
                "vote_count.gte": 50,  # Minimalno glasova
                "vote_average.gte": 6.0  # Minimalna ocjena
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    movies = data.get("results", [])[:limit]
                    logger.info(f"Found {len(movies)} movies with language {language} for {region}")
                    return movies
        except Exception as e:
            logger.error(f"Error fetching by language {language}: {e}")

        return []

    async def _fetch_by_production_country(self, region: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch movies by production country"""
        try:
            # TMDB koristi ISO 3166-1 alpha-2 kodove
            url = f"{self.base_url}/discover/movie"
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": 1,
                "with_origin_country": region.upper(),
                "vote_count.gte": 30,
                "vote_average.gte": 5.0
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    movies = data.get("results", [])[:limit]
                    logger.info(f"Found {len(movies)} movies from production country {region}")
                    return movies
        except Exception as e:
            logger.error(f"Error fetching by country {region}: {e}")

        return []

    def get_region_specific_fallback(self, region: str) -> List[Dict[str, Any]]:
        """Hardcoded fallback filmovi po regiji - ako API ne radi dobro"""
        fallback_data = {
            "US": [
                {"id": 278, "title": "The Shawshank Redemption", "vote_average": 8.7,
                 "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "overview": "Two imprisoned men bond..."},
                {"id": 238, "title": "The Godfather", "vote_average": 8.7,
                 "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "overview": "The aging patriarch..."},
                {"id": 155, "title": "The Dark Knight", "vote_average": 8.5,
                 "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "overview": "Batman faces the Joker..."}
            ],
            "GB": [
                {"id": 672, "title": "Harry Potter and the Philosopher's Stone", "vote_average": 7.9,
                 "poster_path": "/wuMc08IPKEatf9rnMNXvIDxqP4W.jpg", "overview": "A young wizard..."},
                {"id": 37724, "title": "Skyfall", "vote_average": 7.2,
                 "poster_path": "/9tJx2fG9eR79kK6OXE2xELrE0Es.jpg", "overview": "James Bond's loyalty..."},
                {"id": 453, "title": "A Beautiful Mind", "vote_average": 8.2,
                 "poster_path": "/npp5eBtq3QmInp8IFxku1hONxpT.jpg", "overview": "A mathematician..."}
            ],
            "FR": [
                {"id": 194, "title": "Amélie", "vote_average": 7.8, "poster_path": "/7sv2B1vC05M92hOILKj3eC8T0vx.jpg",
                 "overview": "A young woman..."},
                {"id": 509, "title": "Notting Hill", "vote_average": 7.2,
                 "poster_path": "/f1gMw3PVicfdq9thlvUIjJ5UdvS.jpg", "overview": "A bookseller..."},
                {"id": 73, "title": "American History X", "vote_average": 8.5,
                 "poster_path": "/c2gsmSQ2Cqv8zosqKOCwRS0GFBS.jpg", "overview": "A former neo-nazi..."}
            ],
            "DE": [
                {"id": 550, "title": "Fight Club", "vote_average": 8.4,
                 "poster_path": "/bptfVGEQuv6vDTIMVCHjJ9Dz8PX.jpg", "overview": "An insomniac..."},
                {"id": 27205, "title": "Inception", "vote_average": 8.4,
                 "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", "overview": "A thief who steals..."},
                {"id": 157336, "title": "Interstellar", "vote_average": 8.4,
                 "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "overview": "A team of explorers..."}
            ],
            "JP": [
                {"id": 129, "title": "Spirited Away", "vote_average": 8.6,
                 "poster_path": "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", "overview": "A young girl..."},
                {"id": 12477, "title": "Howl's Moving Castle", "vote_average": 8.4,
                 "poster_path": "/6pZgH10jhpLp4NQOZuLJhC7vWjF.jpg", "overview": "A young woman..."},
                {"id": 372058, "title": "Your Name", "vote_average": 8.4,
                 "poster_path": "/q719jXXEzOoYaps6babgKnONONX.jpg", "overview": "Two teenagers..."}
            ],
            "IT": [
                {"id": 424, "title": "Schindler's List", "vote_average": 8.6,
                 "poster_path": "/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", "overview": "A businessman..."},
                {"id": 510, "title": "One Flew Over the Cuckoo's Nest", "vote_average": 8.4,
                 "poster_path": "/3jcbDmRFiQ83drXNOvRDeKHxS0C.jpg", "overview": "A criminal..."},
                {"id": 13, "title": "Forrest Gump", "vote_average": 8.5,
                 "poster_path": "/h5J4W4veyxMXDMjeNxZI46TsHOb.jpg", "overview": "A man with low IQ..."}
            ]
        }

        return fallback_data.get(region.upper(), fallback_data["US"])[:3]


# Singleton instance
tmdb_service = TMDBService()