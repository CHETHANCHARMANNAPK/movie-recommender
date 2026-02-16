import pandas as pd
import json

# Load the datasets
movies = pd.read_csv('data/tmdb_5000_movies.csv')
credits = pd.read_csv('data/tmdb_5000_credits.csv')

print("="*80)
print("MOVIE RECOMMENDER DATA ANALYSIS")
print("="*80)

# Movies dataset
print("\n📊 MOVIES DATASET")
print("-"*80)
print(f"Total movies: {len(movies)}")
print(f"Columns: {list(movies.columns)}")
print(f"\nDataset shape: {movies.shape}")
print(f"Missing values:\n{movies.isnull().sum()}")

# Credits dataset
print("\n\n📊 CREDITS DATASET")
print("-"*80)
print(f"Total records: {len(credits)}")
print(f"Columns: {list(credits.columns)}")
print(f"\nDataset shape: {credits.shape}")
print(f"Missing values:\n{credits.isnull().sum()}")

# Sample movie data
print("\n\n🎬 SAMPLE MOVIE DATA")
print("-"*80)
print(movies[['title', 'genres', 'vote_average', 'popularity']].head(3))

# Check key features for recommender
print("\n\n✅ KEY FEATURES FOR RECOMMENDER SYSTEM")
print("-"*80)

features_available = {
    'Content-Based Features': [],
    'Metadata Features': [],
    'User Engagement': []
}

# Check content-based features
if 'genres' in movies.columns:
    features_available['Content-Based Features'].append('✓ Genres')
if 'keywords' in movies.columns:
    features_available['Content-Based Features'].append('✓ Keywords')
if 'overview' in movies.columns:
    features_available['Content-Based Features'].append('✓ Plot Overview')
if 'cast' in credits.columns:
    features_available['Content-Based Features'].append('✓ Cast Information')
if 'crew' in credits.columns:
    features_available['Content-Based Features'].append('✓ Crew/Director Information')

# Check metadata features
if 'budget' in movies.columns:
    features_available['Metadata Features'].append('✓ Budget')
if 'revenue' in movies.columns:
    features_available['Metadata Features'].append('✓ Revenue')
if 'runtime' in movies.columns:
    features_available['Metadata Features'].append('✓ Runtime')
if 'release_date' in movies.columns:
    features_available['Metadata Features'].append('✓ Release Date')

# Check user engagement features
if 'vote_average' in movies.columns:
    features_available['User Engagement'].append('✓ Vote Average')
if 'vote_count' in movies.columns:
    features_available['User Engagement'].append('✓ Vote Count')
if 'popularity' in movies.columns:
    features_available['User Engagement'].append('✓ Popularity Score')

for category, items in features_available.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  {item}")

# Genre distribution
print("\n\n📈 GENRE DISTRIBUTION (Sample)")
print("-"*80)
try:
    sample_genres = movies['genres'].head(5)
    for idx, genre in enumerate(sample_genres, 1):
        genre_list = json.loads(genre.replace("'", '"'))
        genre_names = [g['name'] for g in genre_list]
        print(f"{idx}. {movies.iloc[idx-1]['title']}: {', '.join(genre_names)}")
except Exception as e:
    print(f"Genre data needs parsing: {e}")

# Rating statistics
print("\n\n⭐ RATING STATISTICS")
print("-"*80)
print(f"Average rating: {movies['vote_average'].mean():.2f}")
print(f"Min rating: {movies['vote_average'].min():.2f}")
print(f"Max rating: {movies['vote_average'].max():.2f}")
print(f"Most voted movie: {movies.loc[movies['vote_count'].idxmax(), 'title']} ({movies['vote_count'].max()} votes)")

print("\n\n" + "="*80)
print("RECOMMENDATION: ✅ YES, THIS DATA IS EXCELLENT FOR A MOVIE RECOMMENDER!")
print("="*80)
print("""
You can build several types of recommenders:

1. 🎯 CONTENT-BASED RECOMMENDER
   - Use genres, keywords, overview, cast, crew
   - Recommend similar movies based on movie features
   
2. 📊 POPULARITY-BASED RECOMMENDER
   - Use vote_average, vote_count, popularity
   - Recommend top-rated or trending movies
   
3. 🔀 HYBRID RECOMMENDER
   - Combine content similarity with popularity
   - Best of both approaches
   
4. 🤖 ADVANCED NLP-BASED
   - Use movie overviews for text similarity
   - TF-IDF or word embeddings

Next steps: Choose your approach and I'll help you build it!
""")
