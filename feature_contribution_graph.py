"""
Bar Graph: Contribution of Different Movie Features in Recommendation Generation
Measures how much each feature (Genres, Overview, Keywords, Cast, Crew/Director)
contributes to the overall cosine similarity for Avatar's top 7 recommendations.
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from recommender import MovieRecommender

# ── 1. Load data using the existing recommender ──────────────────────
recommender = MovieRecommender()
recommender.load_data()

df = recommender.movies_df.copy()

# Avatar movie ID
avatar_id = 19995
avatar_idx = recommender.indices[avatar_id]

# Get top-7 recommended movie indices
sim_scores = list(enumerate(recommender.cosine_sim[avatar_idx]))
sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:8]
rec_indices = [i[0] for i in sim_scores]

# ── 2. Build per-feature TF-IDF and measure contribution ─────────────
features = {
    'Genres':   df['genres_parsed'],
    'Overview': df['overview'],
    'Keywords': df['keywords_parsed'],
    'Cast':     df['cast_parsed'],
    'Crew':     df['director'],          # Director represents the crew feature
}

feature_avg_sim = {}

for feat_name, feat_series in features.items():
    feat_series = feat_series.fillna('').str.lower()
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    matrix = tfidf.fit_transform(feat_series)

    # Cosine similarity of Avatar vs each recommended movie for THIS feature
    avatar_vec = matrix[avatar_idx]
    sims = []
    for ridx in rec_indices:
        score = cosine_similarity(avatar_vec, matrix[ridx])[0][0]
        sims.append(score)
    feature_avg_sim[feat_name] = np.mean(sims)

# ── 3. Compute relative contribution (%) ─────────────────────────────
total = sum(feature_avg_sim.values())
contributions = {k: (v / total) * 100 for k, v in feature_avg_sim.items()}

print("\n📊 Feature Contributions to Avatar Recommendations")
print("=" * 50)
for feat, pct in contributions.items():
    print(f"  {feat:<12} : {pct:6.2f}%  (avg cosine sim = {feature_avg_sim[feat]:.4f})")
print("=" * 50)

# ── 4. Plot Bar Graph ────────────────────────────────────────────────
feature_names = list(contributions.keys())
percentages = list(contributions.values())

colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(feature_names, percentages, color=colors, edgecolor='black',
              linewidth=0.8, width=0.6)

# Add value labels on bars
for bar, pct in zip(bars, percentages):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
            f'{pct:.2f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

ax.set_xlabel('Features', fontsize=14, fontweight='bold', labelpad=10)
ax.set_ylabel('Relative Contribution (%)', fontsize=14, fontweight='bold', labelpad=10)
ax.set_title('Contribution of Different Movie Features\nin Recommendation Generation (Avatar)',
             fontsize=16, fontweight='bold', pad=15)

ax.set_ylim(0, max(percentages) + 10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='both', labelsize=12)
ax.yaxis.grid(True, linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('feature_contribution_graph.png', dpi=150, bbox_inches='tight')
print("\n✅ Graph saved as feature_contribution_graph.png")
plt.show()
