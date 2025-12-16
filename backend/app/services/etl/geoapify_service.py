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

    async def get_featured_cities(self, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Dohvata izabrane gradove za filmsku produkciju
        """
        try:
            logger.info(f"🔍 Getting {limit} featured cities from Geoapify")

            # Lista poznatih filmskih gradova
            featured_cities = [
                {"name": "Los Angeles", "country_code": "US"},
                {"name": "London", "country_code": "GB"},
                {"name": "Paris", "country_code": "FR"},
                {"name": "Tokyo", "country_code": "JP"},
                {"name": "Vancouver", "country_code": "CA"},
                {"name": "Sydney", "country_code": "AU"},
                {"name": "Berlin", "country_code": "DE"},
                {"name": "Rome", "country_code": "IT"}
            ]

            cities_data = []

            for city_info in featured_cities[:limit]:
                try:
                    city_name = city_info["name"]
                    country_code = city_info["country_code"]

                    logger.info(f"  • Fetching {city_name}, {country_code}")

                    # Dohvati grad iz Geoapify API-ja
                    url = f"{self.base_url}/geocode/search"
                    params = {
                        "text": f"{city_name}, {country_code}",
                        "type": "city",
                        "limit": 1,
                        "apiKey": self.api_key,
                        "format": "json"
                    }

                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.get(url, params=params)

                        if response.status_code == 200:
                            data = response.json()
                            features = data.get("features", [])

                            if features:
                                feature = features[0]
                                props = feature.get("properties", {})
                                geometry = feature.get("geometry", {})
                                coordinates = geometry.get("coordinates", [])

                                # Kreiraj grad objekat
                                city_data = {
                                    "city_id": f"geoapify_{props.get('place_id', city_name.lower().replace(' ', '_'))}",
                                    "name": props.get("name", city_name),
                                    "country": props.get("country", country_code),
                                    "country_code": country_code,
                                    "latitude": coordinates[1] if len(coordinates) > 1 else 0,
                                    "longitude": coordinates[0] if coordinates else 0,
                                    "population": props.get("population", 0),
                                    "film_importance": self._get_film_importance(city_name),
                                    "description": self._get_city_description(city_name),
                                    "sample_films": self._get_sample_films(city_name),
                                    "source": "geoapify_api",
                                    "fetched_at": datetime.utcnow().isoformat()
                                }
                                cities_data.append(city_data)
                                logger.info(f"    ✓ Successfully fetched {city_name}")
                            else:
                                logger.warning(f"    ✗ No data for {city_name}, using fallback")
                                cities_data.append(self._create_fallback_city(city_name, country_code))
                        else:
                            logger.warning(f"    ✗ API error for {city_name}: {response.status_code}")
                            cities_data.append(self._create_fallback_city(city_name, country_code))

                    # Rate limiting
                    import asyncio
                    await asyncio.sleep(0.3)

                except Exception as city_error:
                    logger.error(f"    ✗ Error for {city_info['name']}: {city_error}")
                    cities_data.append(self._create_fallback_city(city_info["name"], city_info["country_code"]))

            logger.info(f"✅ Successfully fetched {len(cities_data)} featured cities")
            return cities_data

        except Exception as e:
            logger.error(f"❌ Error in get_featured_cities: {e}")
            # Vrati barem fallback gradove
            return self._get_fallback_cities()[:limit]

    def _get_film_importance(self, city_name: str) -> str:
        """Vraća filmski značaj grada"""
        importance = {
            "Los Angeles": "Hollywood - glavni filmski centar svijeta",
            "London": "Glavni evropski filmski centar",
            "Paris": "Centar evropske kinematografije",
            "Tokyo": "Važan azijski filmski centar",
            "Vancouver": "Hollywood North - popularna lokacija",
            "Sydney": "Glavni filmski centar Australije",
            "Berlin": "Važan evropski filmski centar",
            "Rome": "Historijska lokacija za filmsko snimanje"
        }
        return importance.get(city_name, f"Važna filmska lokacija")

    def _get_city_description(self, city_name: str) -> str:
        """Vraća opis grada"""
        description = {
            "Los Angeles": "Dom Hollywooda i najveća filmska industrija na svijetu.",
            "London": "Bogata filmska historija sa globalnim uticajem.",
            "Paris": "Grad ljubavi i svjetla, inspirativna filmska lokacija.",
            "Tokyo": "Dinamičan grad sa jedinstvenom kinematografijom.",
            "Vancouver": "Popularna lokacija zbog raznovrsnih scenerija.",
            "Sydney": "Spektakularne luke i plaže za filmsku produkciju.",
            "Berlin": "Živa nezavisna filmska scena i bogata historija.",
            "Rome": "Drevni grad sa beskonačnom filmskom inspiracijom."
        }
        return description.get(city_name, f"{city_name} je važna filmska lokacija.")

    def _get_sample_films(self, city_name: str) -> List[str]:
        """Vraća primjere filmova"""
        films = {
            "Los Angeles": ["Titanic", "Avatar", "Star Wars", "The Godfather"],
            "London": ["Harry Potter", "James Bond", "Sherlock Holmes"],
            "Paris": ["Amélie", "The Da Vinci Code", "Midnight in Paris"],
            "Tokyo": ["Godzilla", "Lost in Translation", "The Wolverine"],
            "Vancouver": ["Deadpool", "Twilight", "The X-Files"],
            "Sydney": ["Mad Max", "The Matrix", "Mission: Impossible 2"],
            "Berlin": ["Inglourious Basterds", "The Bourne Supremacy", "Bridge of Spies"],
            "Rome": ["Roman Holiday", "Gladiator", "The Great Beauty"]
        }
        return films.get(city_name, ["Various film productions"])

    def _create_fallback_city(self, city_name: str, country_code: str) -> Dict[str, Any]:
        """Kreira fallback grad"""
        return {
            "city_id": f"fallback_{city_name.lower().replace(' ', '_')}",
            "name": city_name,
            "country": country_code,
            "country_code": country_code,
            "latitude": 0,
            "longitude": 0,
            "population": 0,
            "film_importance": self._get_film_importance(city_name),
            "description": self._get_city_description(city_name),
            "sample_films": self._get_sample_films(city_name),
            "source": "fallback_data",
            "raw_data": {}
        }

    def _get_fallback_cities(self) -> List[Dict[str, Any]]:
        """Vraća listu fallback gradova"""
        fallback_configs = [
            {"name": "Los Angeles", "country_code": "US"},
            {"name": "London", "country_code": "GB"},
            {"name": "Paris", "country_code": "FR"},
            {"name": "Tokyo", "country_code": "JP"},
            {"name": "Vancouver", "country_code": "CA"},
            {"name": "Sydney", "country_code": "AU"},
            {"name": "Berlin", "country_code": "DE"},
            {"name": "Rome", "country_code": "IT"}
        ]

        return [self._create_fallback_city(city["name"], city["country_code"]) for city in fallback_configs]

    async def _get_city_population(self, city_name: str, country_code: str) -> int:
        """Pokušaj dohvatiti populaciju grada"""
        try:
            url = f"{self.base_url}/geocode/search"
            params = {
                "text": f"{city_name}, {country_code}",
                "type": "city",
                "limit": 1,
                "apiKey": self.api_key,
                "filter": f"countrycode:{country_code}"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        props = features[0].get("properties", {})
                        return props.get("population", 0)
        except Exception:
            pass
        return 0


# Singleton instance
geoapify_service = GeoapifyService()