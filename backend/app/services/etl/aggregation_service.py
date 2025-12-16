import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class AggregationService:
    """Service za analizu i korelaciju podataka iz TMDB i Geoapify"""

    @staticmethod
    def correlate_films_with_locations(films: List[Dict], places: List[Dict]) -> List[Dict]:
        """
        Povezuje filmove sa lokacijama na osnovu žanra i teme
        """
        correlations = []

        # Mapiranje žanrova na kategorije mesta
        genre_to_categories = {
            "action": ["entertainment.cinema", "commercial", "building"],
            "comedy": ["entertainment", "catering", "tourism"],
            "drama": ["building.historic", "tourism.museum", "tourism.sights"],
            "horror": ["building.abandoned", "tourism.sights", "natural"],
            "romance": ["tourism.sights.viewpoint", "catering.cafe", "tourism"],
            "thriller": ["commercial", "building", "tourism.sights"],
            "science fiction": ["building", "tourism.museum", "entertainment"],
            "adventure": ["natural", "tourism", "tourism.sights"],
            "fantasy": ["tourism.sights.castle", "building.historic", "natural"]
        }

        for film in films:
            film_id = film.get("film_id")
            film_title = film.get("title", "Unknown")
            film_genres = [g.lower() for g in film.get("genres", [])]

            # Odredi relevantne kategorije za film
            relevant_categories = []
            for genre in film_genres[:2]:  # Uzmi max 2 glavna žanra
                if genre in genre_to_categories:
                    relevant_categories.extend(genre_to_categories[genre])

            # Ako nema mapiranja, koristi opšte kategorije
            if not relevant_categories:
                relevant_categories = ["entertainment", "tourism", "catering"]

            # Pronađi odgovarajuća mesta
            suitable_places = []
            for place in places:
                place_categories = place.get("categories", [])
                primary_category = place.get("primary_category", "")

                # Proveri da li se kategorije poklapaju
                if any(cat in primary_category for cat in relevant_categories):
                    match_score = AggregationService._calculate_match_score(
                        film_genres, place_categories, primary_category
                    )

                    if match_score > 0.3:  # Minimalni threshold
                        suitable_places.append({
                            "place": place,
                            "match_score": match_score,
                            "reason": f"Matches {film_genres[0] if film_genres else 'general'} genre"
                        })

            # Sortiraj po match score
            suitable_places.sort(key=lambda x: x["match_score"], reverse=True)

            # Dodaj korelaciju
            if suitable_places:
                correlations.append({
                    "film_id": film_id,
                    "film_title": film_title,
                    "film_genres": film_genres,
                    "suggested_locations": suitable_places[:3],  # Top 3 lokacije
                    "total_matches": len(suitable_places),
                    "average_match_score": statistics.mean(
                        [p["match_score"] for p in suitable_places[:3]]) if suitable_places else 0
                })

        return correlations

    @staticmethod
    def _calculate_match_score(film_genres: List[str], place_categories: List[str],
                               primary_category: str) -> float:
        """Izračunava koliko se dobro film i lokacija poklapaju"""
        score = 0.0

        genre_category_map = {
            "action": ["entertainment.cinema", "commercial"],
            "comedy": ["entertainment", "catering"],
            "drama": ["building.historic", "tourism.museum"],
            "horror": ["building.abandoned", "natural.cave"],
            "romance": ["tourism.sights.viewpoint", "catering.cafe"]
        }

        # Proveri direktna poklapanja
        for genre in film_genres:
            if genre in genre_category_map:
                for cat in genre_category_map[genre]:
                    if cat in primary_category or any(cat in pc for pc in place_categories):
                        score += 0.5

        # Bonus za specifične kategorije
        if "cinema" in primary_category:
            score += 0.3
        if "museum" in primary_category:
            score += 0.2
        if "historic" in primary_category:
            score += 0.2

        return min(score, 1.0)  # Normalizuj na 0-1

    @staticmethod
    def analyze_film_success_by_location(films: List[Dict], correlations: List[Dict]) -> Dict:
        """Analizira uspešnost filmova po lokacijama"""
        if not films or not correlations:
            return {}

        # Grupiši filmove po lokacijama
        location_stats = {}

        for correlation in correlations:
            film_id = correlation["film_id"]
            film = next((f for f in films if f.get("film_id") == film_id), None)

            if not film:
                continue

            film_rating = film.get("vote_average", 0)
            film_popularity = film.get("popularity", 0)

            for suggestion in correlation.get("suggested_locations", []):
                place = suggestion.get("place", {})
                place_id = place.get("place_id")

                if place_id not in location_stats:
                    location_stats[place_id] = {
                        "place_name": place.get("name"),
                        "place_city": place.get("city"),
                        "films": [],
                        "average_rating": 0,
                        "average_popularity": 0,
                        "total_films": 0,
                        "genres": set()
                    }

                # Dodaj film u statistiku lokacije
                location_stats[place_id]["films"].append({
                    "film_id": film_id,
                    "film_title": film.get("title"),
                    "rating": film_rating,
                    "popularity": film_popularity,
                    "match_score": suggestion.get("match_score", 0)
                })

                # Dodaj žanrove
                for genre in film.get("genres", []):
                    location_stats[place_id]["genres"].add(genre)

        # Izračunaj proseke
        for place_id, stats in location_stats.items():
            films_list = stats["films"]
            if films_list:
                stats["average_rating"] = statistics.mean([f["rating"] for f in films_list])
                stats["average_popularity"] = statistics.mean([f["popularity"] for f in films_list])
                stats["total_films"] = len(films_list)
                stats["genres"] = list(stats["genres"])

        # Sortiraj po broju filmova
        sorted_stats = dict(sorted(
            location_stats.items(),
            key=lambda x: x[1]["total_films"],
            reverse=True
        ))

        return {
            "total_locations_analyzed": len(sorted_stats),
            "most_popular_location": max(
                sorted_stats.items(),
                key=lambda x: x[1]["total_films"]
            )[1] if sorted_stats else None,
            "highest_rated_location": max(
                sorted_stats.items(),
                key=lambda x: x[1]["average_rating"]
            )[1] if sorted_stats else None,
            "location_stats": sorted_stats
        }

    @staticmethod
    def generate_location_recommendations(user_preferences: Dict,
                                          places: List[Dict]) -> List[Dict]:
        """Generiše preporuke lokacija na osnovu korisničkih preferenci"""
        recommendations = []

        preferred_genres = user_preferences.get("preferred_genres", [])
        preferred_categories = user_preferences.get("preferred_categories", [])

        for place in places:
            relevance_score = 0.0

            # Proveri žanrove
            for genre in preferred_genres:
                genre_categories = AggregationService._get_categories_for_genre(genre)
                if any(cat in place.get("primary_category", "") for cat in genre_categories):
                    relevance_score += 0.4

            # Proveri direktne kategorije
            place_categories = place.get("categories", [])
            for pref_cat in preferred_categories:
                if any(pref_cat in cat for cat in place_categories):
                    relevance_score += 0.3

            # Bonus za popularne lokacije
            if place.get("distance", 0) < 2000:  # Blizu centra
                relevance_score += 0.1

            if relevance_score > 0.2:
                recommendations.append({
                    "place": place,
                    "relevance_score": round(relevance_score, 2),
                    "reasons": [
                        f"Matches {len([g for g in preferred_genres if AggregationService._get_categories_for_genre(g)])} preferred genres",
                        "Central location" if place.get("distance", 0) < 2000 else ""
                    ]
                })

        # Sortiraj po relevance
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        return recommendations[:10]  # Top 10 preporuka

    @staticmethod
    def _get_categories_for_genre(genre: str) -> List[str]:
        """Vraća kategorije mesta za dati žanr"""
        mapping = {
            "action": ["entertainment.cinema", "commercial"],
            "comedy": ["entertainment", "catering"],
            "drama": ["building.historic", "tourism.museum"],
            "horror": ["building.abandoned", "tourism.sights"],
            "romance": ["tourism.sights.viewpoint", "catering.cafe"]
        }
        return mapping.get(genre.lower(), ["tourism", "entertainment"])


# Singleton instance
aggregation_service = AggregationService()