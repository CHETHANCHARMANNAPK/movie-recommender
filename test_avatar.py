
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from recommender import MovieRecommender  # type: ignore[import-not-found]

# Initialize and load data
recommender = MovieRecommender()
recommender.load_data()

# Search for Avatar
results, total = recommender.search_movies('Avatar', limit=5)
print("\n🔍 Search results for 'Avatar':")
for r in results:
    print(f"  ID: {r['id']}, Title: {r['title']}, Year: {r['release_date']}")

if not results:
    print("❌ Avatar not found in dataset!")
    sys.exit(1)

# Use the first Avatar result
avatar_id = results[0]['id']
avatar_title = results[0]['title']
print(f"\n🎬 Getting 5 recommendations for: {avatar_title} (ID: {avatar_id})")
print("=" * 70)

# Get 5 recommendations
recs = recommender.get_recommendations(avatar_id, top_n=7)

if recs:
    print(f"\n{'#':<4} {'Movie Title':<40} {'Cosine Similarity Score':<25}")
    print("-" * 70)
    for i, rec in enumerate(recs, 1):
        # similarity_score is already percentage (score * 100)
        cosine_raw = rec['similarity_score'] / 100.0
        print(f"{i:<4} {rec['title']:<40} {cosine_raw:.4f} ({rec['similarity_score']:.2f}%)")
    print("-" * 70)
else:
    print("❌ No recommendations found!")
