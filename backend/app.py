"""
Movie Recommendation Website - Backend API
Flask-based REST API with recommendation engine,
JWT authentication, watchlist, ratings, trailers,
hybrid recommendations, and advanced filtering.
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from recommender import MovieRecommender
from database import Database
from tmdb_service import TMDBService
from auth import generate_token, login_required, optional_auth

app = Flask(__name__)
CORS(app)

# Initialize services
recommender = MovieRecommender()
db = Database()
tmdb = TMDBService()

print("🎬 Loading movie data and building recommendation engine...")
recommender.load_data()
print("✅ Recommendation engine ready!")


# ─── Helpers ──────────────────────────────────────────────────────────

def _enrich_posters(movies):
    """Attach poster_url to a list of movie dicts."""
    for m in movies:
        m['poster_url'] = tmdb.get_poster_url(m.get('title', ''), m.get('id'))
    return movies


# ─── Health Check ─────────────────────────────────────────────────────

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'Movie Recommendation API is running'
    })


# ─── Auth Endpoints ──────────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    if len(password) < 4:
        return jsonify({'success': False, 'error': 'Password must be at least 4 characters'}), 400

    user, err = db.create_user(username, email, password)
    if err:
        return jsonify({'success': False, 'error': err}), 409

    token = generate_token(user.id, user.username)
    return jsonify({
        'success': True,
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = db.authenticate_user(username, password)
    if not user:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    token = generate_token(user.id, user.username)
    return jsonify({
        'success': True,
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    })


@app.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    user = db.get_user_by_id(g.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    return jsonify({
        'success': True,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    })


# ─── Movie Endpoints (with pagination) ───────────────────────────────

@app.route('/api/movies/popular', methods=['GET'])
def get_popular_movies():
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        movies, total = recommender.get_popular_movies(limit, offset)
        _enrich_posters(movies)
        return jsonify({'success': True, 'count': len(movies), 'total': total, 'movies': movies})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter required'}), 400
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        movies, total = recommender.search_movies(query, limit, offset)
        _enrich_posters(movies)
        return jsonify({'success': True, 'query': query, 'count': len(movies), 'total': total, 'movies': movies})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
@optional_auth
def get_movie_details(movie_id):
    try:
        movie = recommender.get_movie_details(movie_id)
        if not movie:
            return jsonify({'success': False, 'error': 'Movie not found'}), 404
        movie['poster_url'] = tmdb.get_poster_url(movie.get('title', ''), movie_id)
        movie['trailer_url'] = tmdb.get_trailer_url(movie.get('title', ''), movie_id)

        # If authenticated, include user-specific data
        if g.user_id:
            movie['in_watchlist'] = db.is_in_watchlist(g.user_id, movie_id)
            movie['user_rating'] = db.get_user_rating(g.user_id, movie_id)
            db.track_view(g.user_id, movie_id)

        return jsonify({'success': True, 'movie': movie})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movies/<int:movie_id>/recommendations', methods=['GET'])
@optional_auth
def get_recommendations(movie_id):
    try:
        top_n = int(request.args.get('limit', 10))

        # Use hybrid if user is logged in and has ratings
        recs = None
        if g.user_id:
            user_ratings = db.get_user_ratings(g.user_id)
            if user_ratings:
                recs = recommender.hybrid_recommendations(movie_id, user_ratings, top_n)

        if recs is None:
            recs = recommender.get_recommendations(movie_id, top_n)

        if recs is None:
            return jsonify({'success': False, 'error': 'Movie not found'}), 404

        _enrich_posters(recs)
        return jsonify({'success': True, 'movie_id': movie_id, 'count': len(recs), 'recommendations': recs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movies/top-rated', methods=['GET'])
def get_top_rated_movies():
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        min_votes = int(request.args.get('min_votes', 500))
        movies, total = recommender.get_top_rated_movies(limit, min_votes, offset)
        _enrich_posters(movies)
        return jsonify({'success': True, 'count': len(movies), 'total': total, 'movies': movies})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movies/filter', methods=['GET'])
def filter_movies():
    """Advanced filtering endpoint."""
    try:
        genre = request.args.get('genre')
        min_rating = float(request.args.get('min_rating', 0))
        max_rating = float(request.args.get('max_rating', 10))
        year_from = request.args.get('year_from')
        year_to = request.args.get('year_to')
        min_runtime = request.args.get('min_runtime')
        max_runtime = request.args.get('max_runtime')
        sort_by = request.args.get('sort_by', 'popularity')
        order = request.args.get('order', 'desc')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))

        movies, total = recommender.filter_movies(
            genre=genre, min_rating=min_rating, max_rating=max_rating,
            year_from=year_from, year_to=year_to,
            min_runtime=min_runtime, max_runtime=max_runtime,
            sort_by=sort_by, order=order, limit=limit, offset=offset
        )
        _enrich_posters(movies)
        return jsonify({'success': True, 'count': len(movies), 'total': total, 'movies': movies})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        genres = recommender.get_all_genres()
        return jsonify({'success': True, 'genres': genres})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Trailer Endpoint ────────────────────────────────────────────────

@app.route('/api/movies/<int:movie_id>/trailer', methods=['GET'])
def get_trailer(movie_id):
    movie = recommender.get_movie_details(movie_id)
    if not movie:
        return jsonify({'success': False, 'error': 'Movie not found'}), 404
    trailer_url = tmdb.get_trailer_url(movie['title'], movie_id)
    return jsonify({'success': True, 'trailer_url': trailer_url})


# ─── Watchlist Endpoints ─────────────────────────────────────────────

@app.route('/api/watchlist', methods=['GET'])
@login_required
def get_watchlist():
    movie_ids = db.get_watchlist(g.user_id)
    movies = recommender.get_movies_by_ids(movie_ids)
    _enrich_posters(movies)
    return jsonify({'success': True, 'count': len(movies), 'movies': movies})


@app.route('/api/watchlist/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    added = db.add_to_watchlist(g.user_id, movie_id)
    return jsonify({'success': True, 'added': added})


@app.route('/api/watchlist/<int:movie_id>', methods=['DELETE'])
@login_required
def remove_from_watchlist(movie_id):
    removed = db.remove_from_watchlist(g.user_id, movie_id)
    return jsonify({'success': True, 'removed': removed})


# ─── Rating Endpoints ────────────────────────────────────────────────

@app.route('/api/ratings/<int:movie_id>', methods=['POST'])
@login_required
def rate_movie(movie_id):
    data = request.get_json() or {}
    score = data.get('score')
    if score is None:
        return jsonify({'success': False, 'error': 'Score is required'}), 400
    db.rate_movie(g.user_id, movie_id, score)
    return jsonify({'success': True, 'movie_id': movie_id, 'score': float(score)})


@app.route('/api/ratings', methods=['GET'])
@login_required
def get_my_ratings():
    ratings = db.get_user_ratings(g.user_id)
    return jsonify({'success': True, 'ratings': ratings})


# ─── "Because You Liked" Endpoint ────────────────────────────────────

@app.route('/api/movies/because-you-liked', methods=['GET'])
@login_required
def because_you_liked():
    recent_ids = db.get_recent_views(g.user_id, limit=5)
    if not recent_ids:
        return jsonify({'success': True, 'source_title': None, 'movies': []})
    source_title, recs = recommender.because_you_liked(recent_ids, top_n=10)
    if recs:
        _enrich_posters(recs)
    return jsonify({
        'success': True,
        'source_title': source_title,
        'movies': recs or []
    })


# ─── Run ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Movie Recommendation API Server")
    print("=" * 60)
    print("📊 Dataset: TMDB 5000 Movies")
    print("🤖 Engine: Content-Based + Hybrid Collaborative Filtering")
    print("🔐 Auth:   JWT Token Authentication")
    print("🌐 Access: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
