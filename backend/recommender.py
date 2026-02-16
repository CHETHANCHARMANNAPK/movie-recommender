"""
Movie Recommendation Engine
Content-Based Filtering using TF-IDF and Cosine Similarity
+ Hybrid collaborative filtering when user ratings are available
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import json
import os


class MovieRecommender:
    """
    Content-based movie recommendation engine
    Uses NLP techniques to find similar movies
    """
    
    def __init__(self):
        self.movies_df = None
        self.credits_df = None
        self.cosine_sim = None
        self.indices = None
        self.tfidf_matrix = None
        
    def load_data(self):
        """Load and preprocess movie datasets"""
        print("📁 Loading datasets...")
        
        # Get the correct path to data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        movies_path = os.path.join(base_dir, 'data', 'tmdb_5000_movies.csv')
        credits_path = os.path.join(base_dir, 'data', 'tmdb_5000_credits.csv')
        
        # Load datasets
        self.movies_df = pd.read_csv(movies_path)
        self.credits_df = pd.read_csv(credits_path)
        
        # Merge datasets on title
        # Note: Both datasets may have 'cast' and 'crew' columns, causing _x and _y suffixes
        self.movies_df = self.movies_df.merge(
            self.credits_df[['title', 'cast', 'crew']], 
            on='title',
            how='left'
        )
        
        print(f"✅ Loaded {len(self.movies_df)} movies")
        
        # Preprocess data
        self._preprocess_data()
        
        # Build recommendation model
        self._build_model()
        
    def _preprocess_data(self):
        """Extract and clean features for recommendation"""
        print("🔧 Preprocessing data...")
        
        # Create parsed columns for TF-IDF soup (space-joined for vectorization)
        self.movies_df['genres_parsed'] = self.movies_df['genres'].apply(self._parse_json_list)
        self.movies_df['keywords_parsed'] = self.movies_df['keywords'].apply(self._parse_json_list)
        self.movies_df['cast_parsed'] = self.movies_df['cast'].apply(self._parse_json_list_top_n, n=5)
        self.movies_df['director'] = self.movies_df['crew'].apply(self._get_director)
        
        # Create display columns (comma-separated, preserving multi-word names)
        self.movies_df['genres_display'] = self.movies_df['genres'].apply(self._parse_json_names)
        self.movies_df['keywords_display'] = self.movies_df['keywords'].apply(self._parse_json_names)
        self.movies_df['cast_display'] = self.movies_df['cast'].apply(lambda x: self._parse_json_names(x, limit=5))
        
        # Clean text fields
        self.movies_df['overview'] = self.movies_df['overview'].fillna('')
        
        # Create feature soup for content-based filtering
        self.movies_df['soup'] = (
            self.movies_df['genres_parsed'] + ' ' +
            self.movies_df['keywords_parsed'] + ' ' +
            self.movies_df['cast_parsed'] + ' ' +
            self.movies_df['director'] + ' ' +
            self.movies_df['overview']
        )
        
        # Clean soup
        self.movies_df['soup'] = self.movies_df['soup'].str.lower()
        
        print("✅ Preprocessing complete")
        
    def _parse_json_list(self, json_str):
        """Parse JSON list and extract names"""
        try:
            data = json.loads(json_str.replace("'", '"'))
            return ' '.join([item['name'] for item in data])
        except:
            return ''
    
    def _parse_json_list_top_n(self, json_str, n=5):
        """Parse JSON list and extract top N names"""
        try:
            data = json.loads(json_str.replace("'", '"'))
            return ' '.join([item['name'] for item in data[:n]])
        except:
            return ''
    
    def _parse_json_names(self, json_str, limit=None):
        """Parse JSON list and return comma-separated names (preserving multi-word names)"""
        try:
            data = json.loads(json_str.replace("'", '"'))
            names = [item['name'] for item in data]
            if limit:
                names = names[:limit]
            return ', '.join(names)
        except:
            return ''
    
    def _get_director(self, json_str):
        """Extract director from crew"""
        try:
            data = json.loads(json_str.replace("'", '"'))
            for person in data:
                if person.get('job') == 'Director':
                    return person.get('name', '')
            return ''
        except:
            return ''
    
    def _build_model(self):
        """Build TF-IDF matrix and compute cosine similarity"""
        print("🤖 Building recommendation model...")
        
        # Create TF-IDF Vectorizer
        tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        # Fit and transform
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df['soup'])
        
        # Compute cosine similarity matrix
        print("📊 Computing similarity matrix...")
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        # Create reverse mapping of indices
        self.indices = pd.Series(
            self.movies_df.index,
            index=self.movies_df['id']
        ).drop_duplicates()
        
        print("✅ Model ready!")
        
    def get_recommendations(self, movie_id, top_n=10):
        """Get top N similar movies"""
        try:
            # Get index from movie ID
            idx = self.indices[movie_id]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            
            # Sort by similarity (excluding itself)
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
            
            # Get movie indices
            movie_indices = [i[0] for i in sim_scores]
            
            # Return movie details with similarity scores
            recommendations = []
            for i, score in zip(movie_indices, [s[1] for s in sim_scores]):
                movie = self.movies_df.iloc[i]
                recommendations.append({
                    'id': int(movie['id']),
                    'title': movie['title'],
                    'overview': movie['overview'][:200] + '...' if len(str(movie['overview'])) > 200 else str(movie['overview']),
                    'genres': movie.get('genres_display', ''),
                    'vote_average': float(movie['vote_average']),
                    'popularity': float(movie['popularity']),
                    'release_date': str(movie['release_date']),
                    'similarity_score': round(float(score) * 100, 2)
                })
            
            return recommendations
        except KeyError:
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_popular_movies(self, limit=20, offset=0):
        """Get popular movies with pagination"""
        popular = self.movies_df.nlargest(offset + limit, 'popularity').iloc[offset:offset + limit]
        total = len(self.movies_df)
        return self._format_movies(popular), total

    def get_top_rated_movies(self, limit=20, min_votes=500, offset=0):
        """Get top rated movies with pagination"""
        qualified = self.movies_df[self.movies_df['vote_count'] >= min_votes]
        top_rated = qualified.nlargest(offset + limit, 'vote_average').iloc[offset:offset + limit]
        return self._format_movies(top_rated), len(qualified)

    def search_movies(self, query, limit=20, offset=0):
        """Search movies by title with pagination"""
        mask = self.movies_df['title'].str.contains(query, case=False, na=False)
        all_results = self.movies_df[mask]
        total = len(all_results)
        results = all_results.iloc[offset:offset + limit]
        return self._format_movies(results), total

    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        try:
            movie = self.movies_df[self.movies_df['id'] == movie_id].iloc[0]

            genres_list = []
            try:
                genres_data = json.loads(movie['genres'].replace("'", '"'))
                genres_list = [g['name'] for g in genres_data]
            except:
                pass

            return {
                'id': int(movie['id']),
                'title': movie['title'],
                'original_title': movie['original_title'],
                'overview': movie['overview'],
                'genres': ', '.join(genres_list),
                'keywords': movie.get('keywords_display', ''),
                'cast': movie.get('cast_display', ''),
                'director': movie.get('director', ''),
                'vote_average': float(movie['vote_average']),
                'vote_count': int(movie['vote_count']),
                'popularity': float(movie['popularity']),
                'budget': int(movie['budget']),
                'revenue': int(movie['revenue']),
                'runtime': int(movie['runtime']) if pd.notna(movie['runtime']) else None,
                'release_date': str(movie['release_date']),
                'tagline': movie['tagline'] if pd.notna(movie['tagline']) else '',
                'homepage': movie['homepage'] if pd.notna(movie['homepage']) else ''
            }
        except:
            return None

    def get_all_genres(self):
        """Get list of all genres"""
        all_genres = set()
        for genres_str in self.movies_df['genres']:
            try:
                genres = json.loads(genres_str.replace("'", '"'))
                for genre in genres:
                    all_genres.add(genre['name'])
            except:
                pass
        return sorted(list(all_genres))

    def filter_movies(self, genre=None, min_rating=0, max_rating=10,
                      year_from=None, year_to=None, min_runtime=None,
                      max_runtime=None, sort_by='popularity', order='desc',
                      limit=20, offset=0):
        """Advanced filtering with sorting and pagination"""
        filtered = self.movies_df.copy()

        # Rating range
        filtered = filtered[(filtered['vote_average'] >= min_rating) &
                            (filtered['vote_average'] <= max_rating)]

        # Genre
        if genre:
            filtered = filtered[filtered['genres'].str.contains(genre, case=False, na=False)]

        # Year range
        if year_from or year_to:
            filtered['_year'] = pd.to_numeric(
                filtered['release_date'].str[:4], errors='coerce'
            )
            if year_from:
                filtered = filtered[filtered['_year'] >= int(year_from)]
            if year_to:
                filtered = filtered[filtered['_year'] <= int(year_to)]

        # Runtime range
        if min_runtime:
            filtered = filtered[filtered['runtime'] >= int(min_runtime)]
        if max_runtime:
            filtered = filtered[filtered['runtime'] <= int(max_runtime)]

        total = len(filtered)

        # Sorting
        sort_col = {
            'popularity': 'popularity',
            'rating': 'vote_average',
            'release_date': 'release_date',
            'revenue': 'revenue',
            'title': 'title'
        }.get(sort_by, 'popularity')

        ascending = (order == 'asc')
        filtered = filtered.sort_values(sort_col, ascending=ascending)

        # Pagination
        page = filtered.iloc[offset:offset + limit]
        return self._format_movies(page), total

    def get_movies_by_ids(self, movie_ids):
        """Return movie dicts for a list of IDs (preserves order)"""
        id_set = set(movie_ids)
        subset = self.movies_df[self.movies_df['id'].isin(id_set)]
        movie_map = {}
        for _, movie in subset.iterrows():
            movie_map[int(movie['id'])] = self._format_single(movie)
        # Maintain requested order
        return [movie_map[mid] for mid in movie_ids if mid in movie_map]

    # ── "Because You Liked X" ─────────────────────────────────────────

    def because_you_liked(self, movie_ids, top_n=10):
        """
        Given a list of recently-viewed movie IDs, pick one at random and
        return recommendations based on it.
        """
        import random
        valid = [mid for mid in movie_ids if mid in self.indices.index]
        if not valid:
            return None, None

        source_id = random.choice(valid)
        recs = self.get_recommendations(source_id, top_n)
        source_title = self.movies_df[self.movies_df['id'] == source_id].iloc[0]['title']
        return source_title, recs

    # ── Hybrid Recommendations ────────────────────────────────────────

    def hybrid_recommendations(self, movie_id, user_ratings, top_n=10, alpha=0.7):
        """
        Combine content-based (weight=alpha) with collaborative signal
        (weight=1-alpha) from user ratings.
        user_ratings: dict {movie_id: score}
        """
        content_recs = self.get_recommendations(movie_id, top_n * 3)
        if not content_recs:
            return None

        # Build a simple user-preference vector from their ratings
        liked_ids = [mid for mid, score in user_ratings.items() if score >= 3.5]
        disliked_ids = [mid for mid, score in user_ratings.items() if score < 3.0]

        for rec in content_recs:
            collab_boost = 0.0
            rec_id = rec['id']
            # Boost movies similar to ones the user already liked
            if rec_id in self.indices.index:
                rec_idx = self.indices[rec_id]
                for lid in liked_ids:
                    if lid in self.indices.index:
                        collab_boost += float(self.cosine_sim[rec_idx][self.indices[lid]])
                for did in disliked_ids:
                    if did in self.indices.index:
                        collab_boost -= float(self.cosine_sim[rec_idx][self.indices[did]]) * 0.5

            content_score = rec['similarity_score'] / 100.0
            hybrid = alpha * content_score + (1 - alpha) * max(0, collab_boost)
            rec['hybrid_score'] = round(hybrid * 100, 2)

        # Re-rank by hybrid score
        content_recs.sort(key=lambda r: r['hybrid_score'], reverse=True)
        return content_recs[:top_n]

    # ── Helper formatters ─────────────────────────────────────────────

    def _format_single(self, movie):
        overview = str(movie['overview'])
        return {
            'id': int(movie['id']),
            'title': movie['title'],
            'overview': overview[:150] + '...' if len(overview) > 150 else overview,
            'genres': movie.get('genres_display', ''),
            'vote_average': float(movie['vote_average']),
            'vote_count': int(movie['vote_count']) if pd.notna(movie.get('vote_count')) else 0,
            'popularity': float(movie['popularity']),
            'release_date': str(movie['release_date']),
            'runtime': int(movie['runtime']) if pd.notna(movie.get('runtime')) else None
        }

    def _format_movies(self, df):
        return [self._format_single(row) for _, row in df.iterrows()]
