# backend/app/services/etl/geodb_service.py
import httpx
from typing import List, Dict, Optional, Any
import logging
from ...config import settings

logger = logging.getLogger(__name__)


class GeoDBServices:
    def __init__(self):
        self.base_url = settings.GEO_API_BASE_URL if hasattr(settings,
                                                             'GEO_API_BASE_URL') else "http://geodb-cities-api.wirefreethought.com"
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def search_cities(self, name_prefix: str, limit: int = 10, offset: int = 0) -> Dict:
        """Pretraga gradova po nazivu"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/geo/cities",
                    params={
                        "namePrefix": name_prefix,
                        "limit": limit,
                        "offset": offset,
                        "sort": "-population"
                    }
                )
                response.raise_for_status()
                data = response.json()

                logger.info(f"Found {data.get('metadata', {}).get('totalCount', 0)} cities for prefix '{name_prefix}'")
                return data

        except httpx.RequestError as e:
            logger.error(f"Request error searching cities: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            raise

    async def get_city_details(self, city_id: str) -> Dict[str, Any]:
        """Dohvata detalje o gradu"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/geo/cities/{city_id}"
                )
                response.raise_for_status()
                data = response.json()

                city_data = data.get("data", {})
                return {
                    "city_id": city_data.get("id"),
                    "name": city_data.get("name"),
                    "country": city_data.get("country"),
                    "country_code": city_data.get("countryCode"),
                    "region": city_data.get("region"),
                    "population": city_data.get("population"),
                    "latitude": city_data.get("latitude"),
                    "longitude": city_data.get("longitude"),
                    "elevation_meters": city_data.get("elevationMeters"),
                    "timezone": city_data.get("timezone")
                }

        except httpx.RequestError as e:
            logger.error(f"Request error fetching city details {city_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching city details {city_id}: {e}")
            raise

    async def get_nearby_cities(self, latitude: float, longitude: float,
                                radius_km: int = 100, limit: int = 20) -> List[Dict]:
        """Dohvata gradove u blizini lokacije"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/geo/locations/{latitude}+{longitude}/nearbyCities",
                    params={
                        "radius": radius_km,
                        "limit": limit,
                        "offset": 0,
                        "sort": "-population"
                    }
                )
                response.raise_for_status()
                data = response.json()

                cities = []
                for city in data.get("data", []):
                    cities.append({
                        "city_id": city.get("id"),
                        "name": city.get("name"),
                        "country": city.get("country"),
                        "distance_km": city.get("distance"),
                        "latitude": city.get("latitude"),
                        "longitude": city.get("longitude"),
                        "population": city.get("population")
                    })

                return cities

        except httpx.RequestError as e:
            logger.error(f"Request error fetching nearby cities: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching nearby cities: {e}")
            raise

    async def get_cities_by_country(self, country_code: str, limit: int = 50) -> List[Dict]:
        """Dohvata gradove po zemlji"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/geo/countries/{country_code}/cities",
                    params={
                        "limit": limit,
                        "offset": 0,
                        "sort": "-population"
                    }
                )
                response.raise_for_status()
                data = response.json()

                cities = []
                for city in data.get("data", []):
                    cities.append({
                        "city_id": city.get("id"),
                        "name": city.get("name"),
                        "latitude": city.get("latitude"),
                        "longitude": city.get("longitude"),
                        "population": city.get("population")
                    })

                return cities

        except httpx.RequestError as e:
            logger.error(f"Request error fetching cities by country {country_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching cities by country {country_code}: {e}")
            raise

    async def get_country_details(self, country_code: str) -> Dict[str, Any]:
        """Dohvata detalje o zemlji"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/geo/countries/{country_code}"
                )
                response.raise_for_status()
                data = response.json()

                country_data = data.get("data", {})
                return {
                    "country_code": country_data.get("code"),
                    "name": country_data.get("name"),
                    "currency_codes": country_data.get("currencyCodes", []),
                    "flag_image_uri": country_data.get("flagImageUri"),
                    "capital": country_data.get("capital"),
                    "num_regions": country_data.get("numRegions")
                }

        except httpx.RequestError as e:
            logger.error(f"Request error fetching country details {country_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching country details {country_code}: {e}")
            raise

    async def get_locations_for_film_production(self, film_data: Dict) -> List[Dict]:
        """Generira moguće lokacije za filmsku produkciju na osnovu filmskih podataka"""
        try:
            production_countries = film_data.get("production_countries", [])
            possible_locations = []

            for country in production_countries[:3]:  # Limit to top 3 countries
                try:
                    # Pretpostavljamo da je zemlja u formatu "United States"
                    # Možemo pretvoriti u country code ili pretražiti po nazivu
                    if country == "United States":
                        cities = await self.get_cities_by_country("US", limit=10)
                    elif country == "United Kingdom":
                        cities = await self.get_cities_by_country("GB", limit=10)
                    elif country == "France":
                        cities = await self.get_cities_by_country("FR", limit=10)
                    elif country == "Germany":
                        cities = await self.get_cities_by_country("DE", limit=10)
                    elif country == "Italy":
                        cities = await self.get_cities_by_country("IT", limit=10)
                    elif country == "Spain":
                        cities = await self.get_cities_by_country("ES", limit=10)
                    elif country == "Canada":
                        cities = await self.get_cities_by_country("CA", limit=10)
                    elif country == "Australia":
                        cities = await self.get_cities_by_country("AU", limit=10)
                    else:
                        # Za ostale zemlje, pretražujemo po nazivu glavnog grada
                        # Ovo je pojednostavljena verzija
                        continue

                    for city in cities:
                        possible_locations.append({
                            "city_id": city["city_id"],
                            "city_name": city["name"],
                            "country": country,
                            "latitude": city["latitude"],
                            "longitude": city["longitude"],
                            "reason": "Common film production location",
                            "confidence": 0.7  # Confidence score
                        })

                except Exception as e:
                    logger.warning(f"Could not fetch cities for country {country}: {e}")
                    continue

            return possible_locations

        except Exception as e:
            logger.error(f"Error generating film locations: {e}")
            return []