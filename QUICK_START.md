# 🚀 Quick Start Guide

## Your Movie Recommender Project is Ready!

### 📦 What's Been Implemented

✅ **Backend (Flask REST API)**
- Content-based recommendation engine
- TF-IDF vectorization + Cosine similarity
- 4,800+ movies from TMDB dataset
- Search, filter, and recommendation endpoints

✅ **Frontend (HTML/CSS/JS)**
- Modern, responsive UI
- Movie search and browsing
- Genre filtering
- Movie details with recommendations
- Beautiful poster displays

✅ **API Integration**
- TMDB API for movie posters
- Environment variable configuration
- Caching for performance

## 🏃‍♂️ How to Run

### 1. Start the Backend

```bash
cd backend
python app.py
```

Server runs at: **http://localhost:5000**

### 2. Open the Frontend

**Option A: Double-click**
- Open `frontend/index.html` in your browser

**Option B: Local server**
```bash
cd frontend
python -m http.server 5500
```
Then visit: **http://localhost:5500**

## 🎨 Get Movie Posters (Optional)

For real movie posters instead of placeholders:

1. **Read the guide:** [TMDB_API_SETUP.md](TMDB_API_SETUP.md)

2. **Quick steps:**
   - Sign up at https://www.themoviedb.org/signup
   - Get API key at https://www.themoviedb.org/settings/api
   - Add to `.env` file: `TMDB_API_KEY=your_key_here`
   - Restart backend server

**Takes 5 minutes, completely FREE! ✨**

## 🎯 Features You Can Try

### Home Page
- Browse popular movies
- Quick search bar

### Search Page
- Search by movie title
- View results with ratings

### Genres Page
- Filter by genre (Action, Comedy, Drama, etc.)
- Discover movies by category

### Movie Details
- Click any movie card
- See full details, cast, crew
- Get 12 similar movie recommendations
- Similarity scores shown

## 🧪 Test the API

```bash
# Health check
curl http://localhost:5000/

# Popular movies
curl http://localhost:5000/api/movies/popular?limit=10

# Search movies
curl http://localhost:5000/api/movies/search?q=inception

# Get movie details
curl http://localhost:5000/api/movies/19995

# Get recommendations
curl http://localhost:5000/api/movies/19995/recommendations?limit=10

# Get genres
curl http://localhost:5000/api/genres
```

## 📱 Usage Examples

### Example 1: Find Similar Movies
1. Go to **Home** page
2. Click on "The Dark Knight"
3. View recommendations like "Batman Begins", "Inception"

### Example 2: Search for a Movie
1. Go to **Search** page
2. Type "Matrix"
3. Click on "The Matrix"
4. See similar sci-fi recommendations

### Example 3: Browse by Genre
1. Go to **Genres** page
2. Click "Action"
3. Browse action movies sorted by popularity

## 🎓 How the Recommendation Engine Works

1. **Feature Extraction**: Combines genres, keywords, cast, director, plot
2. **TF-IDF Vectorization**: Converts text to numerical vectors
3. **Cosine Similarity**: Measures similarity between movies (0-100%)
4. **Ranking**: Returns top N most similar movies

Example:
- Movie: "The Dark Knight"
- Features: "Action, Crime, Drama, superhero, vigilante, Christian Bale, Christopher Nolan..."
- Similar: "Batman Begins" (85%), "Inception" (72%), etc.

## 📊 Project Statistics

- **Movies**: 4,809
- **Model Build Time**: ~5-10 seconds
- **Recommendation Speed**: <100ms
- **API Endpoints**: 7
- **Frontend Pages**: 3

## 🔧 Troubleshooting

### Backend won't start
```bash
pip install -r backend/requirements.txt
```

### Table already exists error (SQLite)
If you see an error like `table users already exists` when starting the backend, you can reset the database by setting the environment variable `RESET_DB=1` before running the server. This will delete the existing `movies.db` file and create a fresh database (for development only).

**Windows:**
```cmd
set RESET_DB=1
python backend\app.py
```
**Unix/macOS:**
```bash
export RESET_DB=1
python backend/app.py
```

### Frontend can't connect
- Make sure backend is running at http://localhost:5000
- Check browser console (F12) for errors

### No posters showing
- Add TMDB API key to `.env` (see TMDB_API_SETUP.md)
- Placeholders work fine without API key

## 📚 Files Overview

```
movie__recommender/
├── backend/
│   ├── app.py              - Flask API server
│   ├── recommender.py      - ML recommendation engine
│   ├── database.py         - Database models
│   └── tmdb_service.py     - TMDB API integration
├── frontend/
│   ├── index.html          - Main page
│   ├── styles.css          - Styling
│   └── app.js              - JavaScript logic
├── data/
│   ├── tmdb_5000_movies.csv
│   └── tmdb_5000_credits.csv
├── .env                    - Configuration (add your API key here)
├── README.md               - Full documentation
└── TMDB_API_SETUP.md       - API key setup guide
```

## 🎉 Next Steps

1. **Get TMDB API key** - Follow TMDB_API_SETUP.md
2. **Try the features** - Search, browse, get recommendations
3. **Customize** - Modify UI colors, add features
4. **Deploy** - Host on Heroku, Vercel, or AWS

## 💡 Pro Tips

- The recommendation engine works **without** internet once loaded
- API key is only for posters (optional)
- First load takes ~10 seconds to build the model
- Subsequent recommendations are instant (cached)

## 🌟 Have Fun!

Your movie recommendation system is ready to go! Start discovering movies! 🎬

---

**Need help?** Check README.md or TMDB_API_SETUP.md
