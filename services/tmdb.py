import os
import requests
from typing import Dict, List, Optional, Any

# Use environment variable or fallback to provided key
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "3a08a646f83edac9a48438ac670a78b2")
BASE_URL = "https://api.themoviedb.org/3"

class TMDBService:
    @staticmethod
    def search_movie(title: str) -> Optional[Dict[str, Any]]:
        """Search for a movie by title and return the first result"""
        url = f"{BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "include_adult": "false",
            "language": "en-US",
            "page": 1
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("results") and len(data["results"]) > 0:
                return data["results"][0]
            return None
        except Exception as e:
            print(f"Error searching for movie '{title}': {str(e)}")
            return None

    @staticmethod
    def get_movie_details(movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a movie by its ID"""
        url = f"{BASE_URL}/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "append_to_response": "credits,images"
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting movie details for ID {movie_id}: {str(e)}")
            return None

    @staticmethod
    def enrich_movie_data(movie_basic: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich basic movie data with TMDB details"""
        title = movie_basic.get("title", "")
        
        # Search for the movie in TMDB
        tmdb_basic = TMDBService.search_movie(title)
        if not tmdb_basic:
            # Return original data if no TMDB match found
            return movie_basic
        
        movie_id = tmdb_basic.get("id")
        tmdb_details = TMDBService.get_movie_details(movie_id) if movie_id else None
        
        if not tmdb_details:
            # Just add the basic TMDB data if detailed info is not available
            poster_path = tmdb_basic.get("poster_path")
            if poster_path:
                movie_basic["poster"] = f"https://image.tmdb.org/t/p/w500{poster_path}"
            movie_basic["tmdb_id"] = tmdb_basic.get("id")
            movie_basic["tmdb_rating"] = tmdb_basic.get("vote_average")
            return movie_basic
        
        # Extract and add cast information
        cast = []
        if tmdb_details.get("credits") and tmdb_details["credits"].get("cast"):
            for actor in tmdb_details["credits"]["cast"][:5]:  # Limit to top 5 actors
                cast_member = {
                    "name": actor.get("name"),
                    "character": actor.get("character"),
                }
                if actor.get("profile_path"):
                    cast_member["profile_image"] = f"https://image.tmdb.org/t/p/w200{actor['profile_path']}"
                cast.append(cast_member)
        
        # Create enriched movie data
        enriched_data = {
            **movie_basic,
            "tmdb_id": tmdb_details.get("id"),
            "tmdb_title": tmdb_details.get("title"),
            "overview": tmdb_details.get("overview"),
            "release_date": tmdb_details.get("release_date"),
            "runtime": tmdb_details.get("runtime"),
            "genres": [genre.get("name") for genre in tmdb_details.get("genres", [])],
            "rating": tmdb_details.get("vote_average"),
            "cast": cast,
        }
        
        # Add poster and backdrop if available
        if tmdb_details.get("poster_path"):
            enriched_data["poster"] = f"https://image.tmdb.org/t/p/w500{tmdb_details['poster_path']}"
        
        if tmdb_details.get("backdrop_path"):
            enriched_data["backdrop"] = f"https://image.tmdb.org/t/p/original{tmdb_details['backdrop_path']}"
            
        return enriched_data
