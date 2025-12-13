import httpx
import logging
from typing import List, Dict, Optional, Any
from ...config import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class GeoapifyService:
    """Service za rad sa Geoapify Places API"""
    def __init__(self):
        self.api_key = settings.GEOAPIFY_API_KEY
        self.base_url = settings.GEOAPIFY_BASE_URL.rstrip('/')
        self.timeout = httpx.Timeout(30.0, connect=10.0)

        # Ako API key nije postavljen, pokušaj da dobiješ iz environment varijable
        if not self.api_key:
            import os
            self.api_key = os.getenv("GEOAPIFY_API_KEY", "")

        if not self.api_key:
            logger.warning("⚠️ Geoapify API key nije postavljen. API pozivi neće raditi.")

        logger.info(f"✓ GeoapifyService initialized. Key: {self.api_key[:8] if self.api_key else 'NOT_SET'}...")

    async def search_places_by_city(self, city_name: str, country_code: str = None,
                                    categories: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        Pretraga mesta u gradu po kategorijama
        categories: ["tourism", "entertainment", "catering", "commercial", "building", "natural"]
        """
        try:
            logger.info(f"🔍 Searching places in {city_name} (country: {country_code})")

            # Formiraj text query
            text_query = city_name
            if country_code:
                text_query += f", {country_code}"

            # Postavi kategorije
            filter_categories = categories or [
                "entertainment",  # Bioskopi, pozorišta
                "tourism",  # Turističke atrakcije
                "catering",  # Restorani, kafići
                "commercial",  # Trgovine, centri
                "building.historic"  # Istorijske zgrade
            ]

            url = f"{self.base_url}/geocode/search"
            params = {
                "text": text_query,
                "apiKey": self.api_key,
                "limit": limit,
                "type": "city"  # Prvo nađi grad
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 1. Nađi koordinate grada
                geo_response = await client.get(url, params=params)

                if geo_response.status_code != 200:
                    logger.error(f"❌ Geocoding failed: {geo_response.status_code}")
                    return []

                geo_data = geo_response.json()
                features = geo_data.get("features", [])

                if not features:
                    logger.warning(f"⚠️ City {city_name} not found")
                    return []

                # Uzmi prvi rezultat (najrelevantniji grad)
                city_feature = features[0]
                city_props = city_feature.get("properties", {})
                city_coords = city_feature.get("geometry", {}).get("coordinates", [])

                if not city_coords:
                    return []

                lon, lat = city_coords  # GeoJSON format: [lon, lat]

                logger.info(f"📍 Found city: {city_props.get('name')} at {lat}, {lon}")

                # 2. Sada pretraži mesta u okolini grada
                places_url = f"{self.base_url}/places"
                places_params = {
                    "categories": ",".join(filter_categories),
                    "filter": f"circle:{lon},{lat},5000",  # 5km radius oko grada
                    "limit": limit,
                    "apiKey": self.api_key,
                    "lang": "en"
                }

                places_response = await client.get(places_url, params=places_params)

                if places_response.status_code != 200:
                    logger.error(f"❌ Places search failed: {places_response.status_code}")
                    return []

                places_data = places_response.json()
                places_features = places_data.get("features", [])

                # Transformacija podataka
                places = []
                for feature in places_features:
                    props = feature.get("properties", {})
                    place_coords = feature.get("geometry", {}).get("coordinates", [])

                    place = {
                        "place_id": props.get("place_id"),
                        "name": props.get("name", "Unnamed"),
                        "address": props.get("address_line2") or props.get("formatted"),
                        "city": city_props.get("name"),
                        "country": city_props.get("country"),
                        "country_code": city_props.get("country_code"),
                        "categories": props.get("categories", []),
                        "primary_category": props.get("categories", [""])[0] if props.get("categories") else "",
                        "latitude": place_coords[1] if place_coords else lat,
                        "longitude": place_coords[0] if place_coords else lon,
                        "distance": props.get("distance", 0),  # metara od centra
                        "raw_data": props  # Čuvamo raw za detalje
                    }
                    places.append(place)

                logger.info(f"✅ Found {len(places)} places in {city_name}")
                return places

        except Exception as e:
            logger.error(f"❌ Error searching places: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    async def get_places_by_country(self, country_code: str, category: str = None,
                                    limit_per_city: int = 5) -> List[Dict]:
        """
        Dohvata mesta iz više gradova u zemlji
        """
        try:
            # Prvo nađi glavne gradove za zemlju
            cities = await self._get_major_cities(country_code, limit=5)

            all_places = []
            for city in cities:
                places = await self.search_places_by_city(
                    city_name=city["name"],
                    country_code=country_code,
                    categories=[category] if category else None,
                    limit=limit_per_city
                )
                all_places.extend(places)

                # Rate limiting: čekaj malo između gradova
                import asyncio
                await asyncio.sleep(1)

            return all_places

        except Exception as e:
            logger.error(f"Error getting places by country: {e}")
            return []

    async def _get_major_cities(self, country_code: str, limit: int = 5) -> List[Dict]:
        """Dohvata glavne gradove zemlje"""
        try:
            url = f"{self.base_url}/geocode/search"
            params = {
                "text": country_code,
                "type": "city",
                "limit": limit,
                "apiKey": self.api_key,
                "filter": f"countrycode:{country_code}"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    cities = []
                    for feature in data.get("features", []):
                        props = feature.get("properties", {})
                        cities.append({
                            "name": props.get("name"),
                            "country": props.get("country"),
                            "population": props.get("population", 0)
                        })
                    return cities
                return []
        except Exception:
            # Fallback: poznati gradovi po zemljama
            known_cities = {
                "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
                "GB": ["London", "Manchester", "Birmingham", "Liverpool", "Glasgow"],
                "FR": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
                "DE": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
                "IT": ["Rome", "Milan", "Naples", "Turin", "Palermo"]
            }

            cities = known_cities.get(country_code.upper(), ["Capital"])
            return [{"name": city, "country": country_code} for city in cities[:limit]]

    async def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Dohvata detalje o određenom mestu"""
        try:
            url = f"{self.base_url}/places/{place_id}"
            params = {"apiKey": self.api_key}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None

    async def test_connection(self) -> bool:
        """Testira konekciju sa Geoapify API"""
        try:
            url = f"{self.base_url}/geocode/search"
            params = {
                "text": "Paris",
                "apiKey": self.api_key,
                "limit": 1
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    logger.info("✅ Geoapify API connection successful")
                    return True
                else:
                    logger.error(f"❌ Geoapify API failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Geoapify connection error: {e}")
            return False


# Singleton instance
geoapify_service = GeoapifyService()