import httpx
from typing import List, Dict, Optional, Any
import logging
import asyncio
import time
from ...config import settings

logger = logging.getLogger(__name__)


class GeoDBService:
    def __init__(self):
        self.base_url = settings.GEODB_BASE_URL.rstrip('/')
        self.api_key = settings.GEODB_API_KEY
        self.host = settings.GEODB_HOST
        self.timeout = httpx.Timeout(30.0, connect=10.0)

        # Rate limiting varijable
        self.last_request_time = 0
        self.min_request_interval = 7  # Sekundi između zahtjeva (10/min = 1/6s)

        # Headers za RapidAPI
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host,
            "Content-Type": "application/json"
        }

        logger.info(f"✓ GeoDBService initialized (Rate limit: 1 request every {self.min_request_interval}s)")

    async def _rate_limit(self):
        """Rate limiting za GeoDB API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"⏳ Rate limiting: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def get_cities_by_country(self, country_code: str, limit: int = 5) -> List[Dict]:
        """Dohvata gradove po zemlji - SA RATE LIMITING!"""
        try:
            # Primjeni rate limiting
            await self._rate_limit()

            logger.info(f"🔍 Fetching cities for: {country_code}, limit: {limit}")

            url = f"{self.base_url}/cities"
            params = {
                "countryIds": country_code,
                "limit": limit,
                "offset": 0,
                "sort": "-population"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, params=params)

                logger.info(f"📡 GeoDB Response Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    cities_data = data.get("data", [])

                    cities = []
                    for city in cities_data:
                        cities.append({
                            "city_id": city.get("id"),
                            "name": city.get("name"),
                            "country": city.get("country"),
                            "country_code": city.get("countryCode"),
                            "region": city.get("region"),
                            "population": city.get("population", 0),
                            "latitude": city.get("latitude"),
                            "longitude": city.get("longitude"),
                            "elevation_meters": city.get("elevationMeters"),
                            "timezone": city.get("timezone"),
                            "wiki_data_id": city.get("wikiDataId")
                        })

                    logger.info(f"✅ Fetched {len(cities)} cities for {country_code}")
                    return cities

                elif response.status_code == 429:
                    logger.warning(f"⚠️ Rate limit exceeded for {country_code}. Waiting 60 seconds...")
                    await asyncio.sleep(60)  # Čekaj 60 sekundi
                    return await self.get_cities_by_country(country_code, limit)  # Retry

                elif response.status_code == 404:
                    logger.warning(f"⚠️ Country {country_code} not found")
                    return []
                else:
                    logger.error(f"❌ GeoDB Error {response.status_code}: {response.text[:200]}")
                    return []

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("⚠️ Rate limit hit. Waiting 60s...")
                await asyncio.sleep(60)
                return await self.get_cities_by_country(country_code, limit)
            logger.error(f"❌ HTTP Error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return []

    async def test_connection(self) -> bool:
        """Test konekcije - sa rate limiting"""
        await self._rate_limit()

        try:
            url = f"{self.base_url}/cities"
            params = {"limit": 1, "offset": 0}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    total_cities = data.get("metadata", {}).get("totalCount", 0)
                    logger.info(f"✅ GeoDB Connection OK! Total cities in DB: {total_cities}")
                    return True
                elif response.status_code == 429:
                    logger.warning("⚠️ Rate limit during test. Try again later.")
                    return False
                else:
                    logger.error(f"❌ GeoDB Connection Failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"❌ GeoDB Connection Error: {str(e)}")
            return False


# Singleton instance
geodb_service = GeoDBService()