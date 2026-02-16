"""
TMDB API Service
Fetches movie posters, trailers and additional metadata
"""

import requests
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file (check both backend/ and project root)
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class TMDBService:
    """Service to interact with TMDB API for posters and trailers"""

    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    def __init__(self):
        self.session = requests.Session()
        # Load API key at instance creation time (after load_dotenv has run)
        self.API_KEY = os.getenv('TMDB_API_KEY', 'YOUR_API_KEY_HERE')
        if self.API_KEY == 'YOUR_API_KEY_HERE':
            print("⚠️  Warning: TMDB_API_KEY not set. Posters & trailers won't work.")
        else:
            print(f"✅ TMDB API key loaded (ends with ...{self.API_KEY[-4:]})")

    @lru_cache(maxsize=1000)
    def get_poster_url(self, movie_title, movie_id=None):
        """Get poster URL for a movie (cached)"""
        try:
            search_url = f"{self.BASE_URL}/search/movie"
            params = {
                'api_key': self.API_KEY,
                'query': movie_title
            }
            response = self.session.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    poster_path = data['results'][0].get('poster_path')
                    if poster_path:
                        return f"{self.IMAGE_BASE_URL}{poster_path}"
            return self._get_placeholder_poster()
        except Exception as e:
            print(f"Error fetching poster for {movie_title}: {e}")
            return self._get_placeholder_poster()

    @lru_cache(maxsize=500)
    def get_trailer_url(self, movie_title, movie_id=None):
        """
        Get YouTube trailer URL for a movie.
        Returns a YouTube embed URL or None.
        """
        try:
            # Find the TMDB id first via search
            tmdb_id = self._resolve_tmdb_id(movie_title, movie_id)
            if not tmdb_id:
                return None
            url = f"{self.BASE_URL}/movie/{tmdb_id}/videos"
            params = {'api_key': self.API_KEY}
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                for video in data.get('results', []):
                    if video.get('site') == 'YouTube' and video.get('type') in ('Trailer', 'Teaser'):
                        return f"https://www.youtube.com/embed/{video['key']}"
            return None
        except Exception as e:
            print(f"Error fetching trailer for {movie_title}: {e}")
            return None

    def _resolve_tmdb_id(self, movie_title, movie_id=None):
        """Resolve a TMDB movie id by searching."""
        try:
            search_url = f"{self.BASE_URL}/search/movie"
            params = {'api_key': self.API_KEY, 'query': movie_title}
            response = self.session.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]['id']
        except:
            pass
        return movie_id

    def _get_placeholder_poster(self):
        """Return placeholder image URL"""
        return "https://via.placeholder.com/500x750/1a1a1a/ffffff?text=No+Poster"

    def get_movie_details_from_tmdb(self, movie_id):
        """Get additional movie details from TMDB"""
        try:
            url = f"{self.BASE_URL}/movie/{movie_id}"
            params = {'api_key': self.API_KEY}
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching details for movie {movie_id}: {e}")
            return None
