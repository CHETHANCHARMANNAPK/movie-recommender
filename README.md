# 🎬 Movie Recommender System

A full-stack movie recommendation website powered by content-based filtering using machine learning. The system analyzes movie features (genres, keywords, cast, crew, plot) to recommend similar films using TF-IDF vectorization and cosine similarity.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3.2-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🎯 Core Functionality
- **Smart Recommendations**: Content-based filtering using TF-IDF and cosine similarity
- **Movie Search**: Fast search across 5,000+ movies
- **Genre Filtering**: Browse movies by genre with advanced filters
- **Detailed Information**: Complete movie details including cast, crew, ratings, and budget
- **Beautiful UI**: Modern, responsive design with smooth animations

### 🤖 Technology Stack
- **Backend**: Flask REST API with CORS support
- **Machine Learning**: scikit-learn (TF-IDF, Cosine Similarity)
- **Data Processing**: pandas, numpy
- **Database**: SQLAlchemy (SQLite default, PostgreSQL ready)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **API Integration**: TMDB API for movie posters

## 📊 Dataset

Using the **TMDB 5000 Movies Dataset** containing:
- 5,000 movies with metadata
- Genres, keywords, cast, crew information
- User ratings and popularity scores
- Revenue and budget information

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Installation

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd movie__recommender
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Set up environment variables (Optional)**
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your TMDB API key (optional - placeholder will work)
# Get a free API key from: https://www.themoviedb.org/settings/api
```

4. **Start the backend server**
```bash
python app.py
```

The server will start at `http://localhost:5000`

You should see:
```
🎬 Loading movie data and building recommendation engine...
📁 Loading datasets...
✅ Loaded 4803 movies
🔧 Preprocessing data...
✅ Preprocessing complete
🤖 Building recommendation model...
📊 Computing similarity matrix...
✅ Model ready!
✅ Recommendation engine ready!

============================================================
🚀 Movie Recommendation API Server
============================================================
📊 Dataset: TMDB 5000 Movies
🤖 Engine: Content-Based Filtering (TF-IDF + Cosine Similarity)
🌐 Access: http://localhost:5000
============================================================
```

5. **Open the frontend**

Simply open `frontend/index.html` in your web browser, or use a local server:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500` in your browser.

## 📁 Project Structure

```
movie__recommender/
│
├── backend/
│   ├── app.py                 # Flask REST API server
│   ├── recommender.py         # ML recommendation engine
│   ├── database.py            # Database models & operations
│   ├── tmdb_service.py        # TMDB API integration
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── styles.css            # CSS styling
│   └── app.js                # JavaScript logic
│
├── data/
│   ├── tmdb_5000_movies.csv  # Movies dataset
│   └── tmdb_5000_credits.csv # Credits dataset
│
├── analyze_data.py           # Data analysis script
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🔌 API Endpoints

### Health Check
```http
GET /
```

### Get Popular Movies
```http
GET /api/movies/popular?limit=20
```

### Search Movies
```http
GET /api/movies/search?q=inception
```

### Get Movie Details
```http
GET /api/movies/{movie_id}
```

### Get Recommendations
```http
GET /api/movies/{movie_id}/recommendations?limit=10
```

### Get All Genres
```http
GET /api/genres
```

### Filter Movies
```http
GET /api/movies/filter?genre=Action&min_rating=7&limit=20
```

## 🧠 How It Works

### Content-Based Filtering Algorithm

1. **Feature Extraction**: Combines multiple movie features into a "soup":
   - Genres (e.g., "Action", "Thriller")
   - Keywords (e.g., "superhero", "revenge")
   - Cast (top 5 actors)
   - Director
   - Plot overview

2. **TF-IDF Vectorization**: Converts text features into numerical vectors
   - Reduces importance of common words
   - Emphasizes unique characteristics
   - Uses n-grams (1-2 words) for better context

3. **Cosine Similarity**: Measures similarity between movies
   - Computes similarity matrix (5000 x 5000)
   - Ranges from 0 (completely different) to 1 (identical)
   - Fast lookup for recommendations

4. **Ranking**: Returns top N most similar movies sorted by similarity score

### Example

When you select "The Dark Knight":
- System analyzes: `["Action", "Crime", "Drama", "superhero", "vigilante", "Christian Bale", "Heath Ledger", "Christopher Nolan", ...]`
- Compares with all other movies
- Returns similar films like "Batman Begins", "Inception", etc.

## 🎨 Frontend Features

### Home Page
- Popular movies grid with posters
- Quick search functionality
- Responsive design

### Search Page
- Real-time movie search
- Results with ratings and genres
- Click to view details

### Genres Page
- Browse by genre categories
- Filter movies by genre
- Sorted by popularity

### Movie Details Modal
- Full movie information
- Cast and crew
- Budget and revenue stats
- 12 similar movie recommendations
- Similarity percentage scores

## 🛠️ Configuration

### TMDB API (Optional)
To get real movie posters:
1. Sign up at [TMDB](https://www.themoviedb.org/)
2. Get an API key from [API Settings](https://www.themoviedb.org/settings/api)
3. Add to `.env` file:
```env
TMDB_API_KEY=your_actual_key_here
```

Without an API key, placeholder images will be used.

### Database Configuration
By default, SQLite is used. To switch to PostgreSQL:

1. Update `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/moviedb
```

2. Update `database.py` line 52

## 🧪 Testing

### Test the Data Analysis
```bash
python analyze_data.py
```

### Test the Backend API
```bash
# Start the server
cd backend
python app.py

# In another terminal, test endpoints:
curl http://localhost:5000/
curl http://localhost:5000/api/movies/popular
curl http://localhost:5000/api/movies/search?q=inception
curl http://localhost:5000/api/movies/19995/recommendations
```

### Test the Frontend
1. Start the backend server
2. Open `frontend/index.html` in a browser
3. Try searching for movies
4. Click on a movie to see details and recommendations

## 📈 Performance

- **Dataset**: 4,803 movies
- **Model Building**: ~5-10 seconds on first load
- **Recommendation Query**: < 100ms
- **Memory Usage**: ~200MB (similarity matrix)
- **API Response Time**: < 200ms average

## 🔮 Future Enhancements

### Planned Features
- [ ] User authentication and profiles
- [ ] Personalized recommendations based on viewing history
- [ ] Collaborative filtering (user-to-user recommendations)
- [ ] Movie ratings and reviews
- [ ] Watchlist functionality
- [ ] Advanced filters (year, rating, runtime)
- [ ] Hybrid recommendation system
- [ ] Social features (share recommendations)

### Technical Improvements
- [ ] Caching layer (Redis)
- [ ] Batch processing for recommendations
- [ ] WebSocket for real-time updates
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Unit and integration tests
- [ ] Performance monitoring

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Dataset**: [TMDB 5000 Movie Dataset](https://www.kaggle.com/tmdb/tmdb-movie-metadata) on Kaggle
- **Movie Data**: [The Movie Database (TMDB)](https://www.themoviedb.org/)
- **Icons**: Emoji icons from Unicode
- **Fonts**: Inter font from Google Fonts

## 📧 Contact

For questions or feedback:
- Open an issue on GitHub
- Submit a pull request
- Email: your-email@example.com

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r backend/requirements.txt`
- Check if port 5000 is available

### Frontend can't connect to backend
- Verify backend is running at `http://localhost:5000`
- Check browser console for CORS errors
- Ensure CORS is enabled in `app.py`

### No movie posters showing
- Add TMDB API key to `.env` file
- Check API key is valid
- Placeholder images will show if API key is missing

### Recommendations are slow
- First-time model building takes 5-10 seconds
- Subsequent queries are cached and fast
- Consider using a smaller dataset for testing

## 🎓 Learning Resources

Want to learn more about recommendation systems?

- [Content-Based Filtering](https://developers.google.com/machine-learning/recommendation/content-based/basics)
- [TF-IDF Explanation](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [scikit-learn Guide](https://scikit-learn.org/stable/user_guide.html)

---

Made with ❤️ and 🎬 | Powered by Machine Learning
