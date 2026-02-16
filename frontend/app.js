// ==================== CONFIGURATION ====================
const API_BASE_URL = 'http://localhost:5000/api';

const GENRE_ICONS = {
    'Action': '💥', 'Adventure': '🏴‍☠️', 'Animation': '🎬', 'Comedy': '😂',
    'Crime': '🔫', 'Documentary': '🎥', 'Drama': '🎭', 'Family': '👨‍👩‍👧‍👦',
    'Fantasy': '🧙', 'History': '🏰', 'Horror': '👻', 'Music': '🎵',
    'Mystery': '🔍', 'Romance': '❤️', 'Science Fiction': '🚀', 'TV Movie': '📺',
    'Thriller': '😨', 'War': '⚔️', 'Western': '🤠', 'Foreign': '🌍'
};

// ==================== STATE MANAGEMENT ====================
const state = {
    currentPage: 'home',
    popularMovies: [],
    searchResults: [],
    genres: [],
    selectedGenre: null,
    currentMovie: null,
    // Auth
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    // Pagination offsets
    popularOffset: 0,
    topRatedOffset: 0,
    searchOffset: 0,
    searchQuery: '',
    genreOffset: 0
};

// ==================== AUTH HELPERS ====================
function authHeaders() {
    const h = { 'Content-Type': 'application/json' };
    if (state.token) h['Authorization'] = `Bearer ${state.token}`;
    return h;
}

function setAuth(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    updateAuthUI();
}

function clearAuth() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
}

function updateAuthUI() {
    const authArea = document.getElementById('auth-area');
    const userArea = document.getElementById('user-area');
    const navWatchlist = document.getElementById('nav-watchlist');
    if (state.user) {
        authArea.style.display = 'none';
        userArea.style.display = 'flex';
        document.getElementById('user-greeting').textContent = `Hi, ${state.user.username}`;
        navWatchlist.style.display = 'inline-block';
        loadBecauseYouLiked();
    } else {
        authArea.style.display = 'block';
        userArea.style.display = 'none';
        navWatchlist.style.display = 'none';
        document.getElementById('because-you-liked-section').style.display = 'none';
    }
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    console.log('🎬 Initializing Movie Recommender App...');
    setupNavigation();
    setupSearch();
    setupModal();
    setupAuthModal();
    setupScrollToTop();
    setupAdvancedFilters();
    updateAuthUI();

    loadPopularMovies();
    loadTopRatedMovies();
    loadGenres();
    console.log('✅ App initialized!');
}

// ==================== NAVIGATION ====================
function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => navigateToPage(btn.getAttribute('data-page')));
    });
    document.querySelector('.logo').addEventListener('click', () => navigateToPage('home'));
}

function navigateToPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`${pageName}-page`).classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`[data-page="${pageName}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    state.currentPage = pageName;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (pageName === 'watchlist') loadWatchlist();
}

// ==================== SEARCH ====================
function setupSearch() {
    const quickBtn = document.getElementById('quick-search-btn');
    const quickInput = document.getElementById('quick-search-input');
    quickBtn.addEventListener('click', () => {
        const q = quickInput.value.trim();
        if (q) { navigateToPage('search'); document.getElementById('search-input').value = q; state.searchOffset = 0; state.searchQuery = q; performSearch(q); }
    });
    quickInput.addEventListener('keypress', e => { if (e.key === 'Enter') quickBtn.click(); });

    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');
    searchBtn.addEventListener('click', () => { const q = searchInput.value.trim(); if (q) { state.searchOffset = 0; state.searchQuery = q; performSearch(q); } });
    searchInput.addEventListener('keypress', e => { if (e.key === 'Enter') searchBtn.click(); });

    let t;
    searchInput.addEventListener('input', () => { clearTimeout(t); const q = searchInput.value.trim(); if (q.length >= 3) { t = setTimeout(() => { state.searchOffset = 0; state.searchQuery = q; performSearch(q); }, 400); } });

    document.getElementById('load-more-search').addEventListener('click', () => {
        state.searchOffset += 20;
        performSearch(state.searchQuery, true);
    });
}

async function performSearch(query, append = false) {
    const container = document.getElementById('search-results');
    const resultCount = document.getElementById('search-result-count');
    const loadMore = document.getElementById('load-more-search');

    if (!append) container.innerHTML = '<div class="loading"><div class="spinner"></div>Searching...</div>';
    resultCount.textContent = '';

    try {
        const res = await fetch(`${API_BASE_URL}/movies/search?q=${encodeURIComponent(query)}&limit=20&offset=${state.searchOffset}`);
        const data = await res.json();
        if (data.success && data.movies.length > 0) {
            resultCount.textContent = `Found ${data.total} movie${data.total !== 1 ? 's' : ''} for "${query}"`;
            if (append) appendMovies(data.movies, container);
            else displayMovies(data.movies, container);
            loadMore.style.display = (state.searchOffset + 20 < data.total) ? 'block' : 'none';
        } else if (!append) {
            container.innerHTML = `<div class="empty-state">🎬 No movies found for "${query}"</div>`;
            loadMore.style.display = 'none';
        }
    } catch (err) {
        console.error(err);
        if (!append) container.innerHTML = '<div class="error">⚠️ Failed to search. Is the backend running?</div>';
    }
}

// ==================== POPULAR MOVIES ====================
async function loadPopularMovies(append = false) {
    const container = document.getElementById('popular-movies');
    const loadMore = document.getElementById('load-more-popular');
    const limit = append ? 10 : 20;
    try {
        const res = await fetch(`${API_BASE_URL}/movies/popular?limit=${limit}&offset=${state.popularOffset}`);
        const data = await res.json();
        if (data.success) {
            if (append) appendMovies(data.movies, container); else displayMovies(data.movies, container);
            loadMore.style.display = (state.popularOffset + limit < data.total) ? 'block' : 'none';
        }
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="error">Failed to load popular movies.</div>';
    }
}

// ==================== TOP RATED ====================
async function loadTopRatedMovies(append = false) {
    const container = document.getElementById('top-rated-movies');
    const loadMore = document.getElementById('load-more-top-rated');
    const limit = append ? 10 : 20;
    try {
        const res = await fetch(`${API_BASE_URL}/movies/top-rated?limit=${limit}&offset=${state.topRatedOffset}&min_votes=500`);
        const data = await res.json();
        if (data.success) {
            if (append) appendMovies(data.movies, container); else displayMovies(data.movies, container);
            loadMore.style.display = (state.topRatedOffset + limit < data.total) ? 'block' : 'none';
        }
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="error">Failed to load top rated movies.</div>';
    }
}

// Load-more button handlers
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('load-more-popular').addEventListener('click', () => { state.popularOffset += 10; loadPopularMovies(true); });
    document.getElementById('load-more-top-rated').addEventListener('click', () => { state.topRatedOffset += 10; loadTopRatedMovies(true); });
    document.getElementById('load-more-genre').addEventListener('click', () => { state.genreOffset += 20; loadGenreMovies(true); });
});

// ==================== GENRES ====================
async function loadGenres() {
    const container = document.getElementById('genre-list');
    try {
        const res = await fetch(`${API_BASE_URL}/genres`);
        const data = await res.json();
        if (data.success) { state.genres = data.genres; displayGenres(data.genres, container); }
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="error">Failed to load genres</div>';
    }
}

function displayGenres(genres, container) {
    container.innerHTML = genres.map(g => {
        const icon = GENRE_ICONS[g] || '🎬';
        return `<div class="genre-chip" data-genre="${g}"><span class="genre-icon">${icon}</span> ${g}</div>`;
    }).join('');
    container.querySelectorAll('.genre-chip').forEach(chip => {
        chip.addEventListener('click', () => selectGenre(chip.getAttribute('data-genre'), chip));
    });
}

async function selectGenre(genre, chipElement) {
    document.querySelectorAll('.genre-chip').forEach(c => c.classList.remove('active'));
    if (chipElement) chipElement.classList.add('active');
    state.selectedGenre = genre;
    state.genreOffset = 0;
    const title = document.getElementById('genre-section-title');
    const icon = GENRE_ICONS[genre] || '🎬';
    title.innerHTML = `<h3>${icon} ${genre} Movies</h3>`;
    await loadGenreMovies();
}

async function loadGenreMovies(append = false) {
    const container = document.getElementById('genre-movies');
    const loadMore = document.getElementById('load-more-genre');
    if (!append) container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';

    const params = new URLSearchParams();
    if (state.selectedGenre) params.set('genre', state.selectedGenre);
    params.set('limit', '20');
    params.set('offset', state.genreOffset.toString());

    // Advanced filters
    const minR = document.getElementById('filter-min-rating').value;
    const maxR = document.getElementById('filter-max-rating').value;
    if (minR && parseFloat(minR) > 0) params.set('min_rating', minR);
    if (maxR && parseFloat(maxR) < 10) params.set('max_rating', maxR);
    const yf = document.getElementById('filter-year-from').value;
    const yt = document.getElementById('filter-year-to').value;
    if (yf) params.set('year_from', yf);
    if (yt) params.set('year_to', yt);
    const mnr = document.getElementById('filter-min-runtime').value;
    const mxr = document.getElementById('filter-max-runtime').value;
    if (mnr) params.set('min_runtime', mnr);
    if (mxr) params.set('max_runtime', mxr);
    params.set('sort_by', document.getElementById('filter-sort-by').value);
    params.set('order', document.getElementById('filter-order').value);

    try {
        const res = await fetch(`${API_BASE_URL}/movies/filter?${params}`);
        const data = await res.json();
        if (data.success) {
            if (append) appendMovies(data.movies, container); else displayMovies(data.movies, container);
            loadMore.style.display = (state.genreOffset + 20 < data.total) ? 'block' : 'none';
        }
    } catch (err) {
        console.error(err);
        if (!append) container.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

// ==================== ADVANCED FILTERS ====================
function setupAdvancedFilters() {
    // Toggle filter panel open/close
    const filterToggle = document.getElementById('filter-toggle');
    const filterBody = document.getElementById('filter-body');
    const filterChevron = document.getElementById('filter-chevron');

    filterToggle.addEventListener('click', () => {
        filterBody.classList.toggle('open');
        filterChevron.classList.toggle('open');
    });

    // Apply filters
    document.getElementById('apply-filters-btn').addEventListener('click', () => {
        state.genreOffset = 0;
        loadGenreMovies();
    });

    // Reset filters
    document.getElementById('reset-filters-btn').addEventListener('click', () => {
        document.getElementById('filter-min-rating').value = '0';
        document.getElementById('filter-max-rating').value = '10';
        document.getElementById('filter-year-from').value = '';
        document.getElementById('filter-year-to').value = '';
        document.getElementById('filter-min-runtime').value = '';
        document.getElementById('filter-max-runtime').value = '';
        document.getElementById('filter-sort-by').value = 'popularity';
        document.getElementById('filter-order').value = 'desc';
        state.genreOffset = 0;
        if (state.selectedGenre) loadGenreMovies();
    });
}

// ==================== DISPLAY MOVIES ====================
function displayMovies(movies, container) {
    if (!movies || movies.length === 0) { container.innerHTML = '<div class="empty-state">No movies found</div>'; return; }
    container.innerHTML = movies.map(m => createMovieCard(m)).join('');
    attachCardListeners(container);
}

function appendMovies(movies, container) {
    if (!movies || movies.length === 0) return;
    const temp = document.createElement('div');
    temp.innerHTML = movies.map(m => createMovieCard(m)).join('');
    while (temp.firstChild) container.appendChild(temp.firstChild);
    attachCardListeners(container);
}

function attachCardListeners(container) {
    container.querySelectorAll('.movie-card').forEach(card => {
        card.removeEventListener('click', cardClickHandler);
        card.addEventListener('click', cardClickHandler);
    });
}

function cardClickHandler(e) {
    // Don't open modal if clicking watchlist/rating buttons
    if (e.target.closest('.card-action-btn')) return;
    const id = parseInt(this.getAttribute('data-movie-id'));
    showMovieDetails(id);
}

function createMovieCard(movie) {
    const poster = movie.poster_url || 'https://via.placeholder.com/200x300/1a1a1a/ffffff?text=No+Poster';
    const rating = movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A';
    const genres = movie.genres ? (typeof movie.genres === 'string' ? movie.genres.split(',').slice(0, 2).map(g => g.trim()).join(', ') : '') : '';
    const similarity = movie.similarity_score ? `<div class="similarity-badge">${movie.similarity_score}% Match</div>` : '';
    const hybrid = movie.hybrid_score ? `<div class="similarity-badge hybrid">${movie.hybrid_score}% Hybrid</div>` : '';
    const year = movie.release_date ? movie.release_date.substring(0, 4) : '';

    return `
        <div class="movie-card" data-movie-id="${movie.id}">
            <img src="${poster}" alt="${movie.title}" class="movie-poster" loading="lazy"
                 onerror="this.src='https://via.placeholder.com/200x300/1a1a1a/ffffff?text=No+Poster'">
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <div class="movie-meta">
                    <span class="movie-rating">⭐ ${rating}</span>
                    <span class="movie-year">${year}</span>
                </div>
                ${genres ? `<div class="movie-genres">${genres}</div>` : ''}
                ${similarity}${hybrid}
            </div>
        </div>
    `;
}

// ==================== MOVIE DETAILS ====================
async function showMovieDetails(movieId) {
    const modal = document.getElementById('movie-modal');
    const details = document.getElementById('movie-details');
    const recs = document.getElementById('recommendations-grid');
    const trailerSection = document.getElementById('trailer-section');

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    details.innerHTML = '<div class="loading">Loading movie details...</div>';
    recs.innerHTML = '<div class="loading">Loading recommendations...</div>';
    trailerSection.style.display = 'none';

    try {
        const detRes = await fetch(`${API_BASE_URL}/movies/${movieId}`, { headers: authHeaders() });
        const detData = await detRes.json();
        if (detData.success) {
            displayMovieDetails(detData.movie, details);
            // Show trailer if available
            if (detData.movie.trailer_url) {
                document.getElementById('trailer-iframe').src = detData.movie.trailer_url;
                trailerSection.style.display = 'block';
            }
        }

        const recRes = await fetch(`${API_BASE_URL}/movies/${movieId}/recommendations?limit=12`, { headers: authHeaders() });
        const recData = await recRes.json();
        if (recData.success) displayMovies(recData.recommendations, recs);
    } catch (err) {
        console.error(err);
        details.innerHTML = '<div class="error">Failed to load movie details</div>';
    }
}

function displayMovieDetails(movie, container) {
    const poster = movie.poster_url || 'https://via.placeholder.com/300x450/1a1a1a/ffffff?text=No+Poster';
    const rating = movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A';
    const runtime = movie.runtime ? `${movie.runtime} min` : 'N/A';
    const budget = movie.budget ? `$${(movie.budget / 1000000).toFixed(1)}M` : 'N/A';
    const revenue = movie.revenue ? `$${(movie.revenue / 1000000).toFixed(1)}M` : 'N/A';

    const genres = movie.genres ? movie.genres.split(',').filter(g => g.trim()).map(g => `<span class="tag">${g.trim()}</span>`).join('') : '';
    const cast = movie.cast ? movie.cast.split(',').filter(c => c.trim()).map(c => `<span class="tag">${c.trim()}</span>`).join('') : '';
    const keywords = movie.keywords ? movie.keywords.split(',').slice(0, 10).filter(k => k.trim()).map(k => `<span class="tag">${k.trim()}</span>`).join('') : '';

    // Watchlist & Rating (only for logged-in users)
    let userActions = '';
    if (state.user) {
        const inWL = movie.in_watchlist;
        const userRating = movie.user_rating;
        userActions = `
            <div class="user-actions">
                <button class="btn btn-sm ${inWL ? 'btn-danger' : 'btn-secondary'} card-action-btn" id="detail-wl-btn"
                        onclick="toggleDetailWatchlist(${movie.id}, ${inWL})">
                    ${inWL ? '❤️ In Watchlist' : '🤍 Add to Watchlist'}
                </button>
                <div class="star-rating" id="detail-star-rating">
                    ${[1,2,3,4,5].map(s => `<span class="star ${userRating && userRating >= s ? 'filled' : ''}" data-score="${s}" onclick="rateFromDetail(${movie.id}, ${s})">★</span>`).join('')}
                    <span class="rating-label">${userRating ? userRating + '/5' : 'Rate'}</span>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <img src="${poster}" alt="${movie.title}" class="details-poster">
        <div class="details-info">
            <h2>${movie.title}</h2>
            ${movie.tagline ? `<p class="details-tagline">"${movie.tagline}"</p>` : ''}
            ${userActions}
            <div class="details-meta">
                <div class="meta-item"><span class="meta-label">⭐ Rating:</span><span class="meta-value">${rating}/10 (${movie.vote_count} votes)</span></div>
                <div class="meta-item"><span class="meta-label">⏱️ Runtime:</span><span class="meta-value">${runtime}</span></div>
                <div class="meta-item"><span class="meta-label">📅 Release:</span><span class="meta-value">${movie.release_date}</span></div>
            </div>
            <div class="details-meta">
                <div class="meta-item"><span class="meta-label">💰 Budget:</span><span class="meta-value">${budget}</span></div>
                <div class="meta-item"><span class="meta-label">💵 Revenue:</span><span class="meta-value">${revenue}</span></div>
                <div class="meta-item"><span class="meta-label">📊 Popularity:</span><span class="meta-value">${movie.popularity.toFixed(1)}</span></div>
            </div>
            <div class="details-overview"><h3>Overview</h3><p>${movie.overview || 'No overview available'}</p></div>
            ${genres ? `<div class="details-genres"><h4>🎭 Genres</h4><div class="tag-list">${genres}</div></div>` : ''}
            ${cast ? `<div class="details-cast"><h4>🎬 Cast</h4><div class="tag-list">${cast}</div></div>` : ''}
            ${movie.director ? `<div class="details-director"><h4>🎥 Director</h4><p>${movie.director}</p></div>` : ''}
            ${keywords ? `<div class="details-keywords"><h4>🏷️ Keywords</h4><div class="tag-list">${keywords}</div></div>` : ''}
            ${movie.homepage ? `<div class="details-homepage"><a href="${movie.homepage}" target="_blank" class="btn btn-secondary">🌐 Visit Official Website</a></div>` : ''}
        </div>
    `;
}

// ==================== WATCHLIST ACTIONS ====================
async function toggleDetailWatchlist(movieId, currentlyIn) {
    if (!state.token) return;
    const method = currentlyIn ? 'DELETE' : 'POST';
    await fetch(`${API_BASE_URL}/watchlist/${movieId}`, { method, headers: authHeaders() });
    // Refresh the detail view
    showMovieDetails(movieId);
}

async function loadWatchlist() {
    if (!state.token) return;
    const container = document.getElementById('watchlist-movies');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading watchlist...</div>';
    try {
        const res = await fetch(`${API_BASE_URL}/watchlist`, { headers: authHeaders() });
        const data = await res.json();
        if (data.success && data.movies.length > 0) displayMovies(data.movies, container);
        else container.innerHTML = '<p class="empty-state">Your watchlist is empty. Click ❤️ on a movie to save it!</p>';
    } catch (err) {
        container.innerHTML = '<div class="error">Failed to load watchlist</div>';
    }
}

// ==================== RATING ====================
async function rateFromDetail(movieId, score) {
    if (!state.token) return;
    await fetch(`${API_BASE_URL}/ratings/${movieId}`, {
        method: 'POST', headers: authHeaders(), body: JSON.stringify({ score })
    });
    showMovieDetails(movieId);
}

// ==================== BECAUSE YOU LIKED ====================
async function loadBecauseYouLiked() {
    if (!state.token) return;
    const section = document.getElementById('because-you-liked-section');
    try {
        const res = await fetch(`${API_BASE_URL}/movies/because-you-liked`, { headers: authHeaders() });
        const data = await res.json();
        if (data.success && data.source_title && data.movies.length > 0) {
            document.getElementById('because-you-liked-title').textContent = `✨ Because You Liked "${data.source_title}"`;
            displayMovies(data.movies, document.getElementById('because-you-liked-movies'));
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    } catch {
        section.style.display = 'none';
    }
}

// ==================== AUTH MODAL ====================
function setupAuthModal() {
    const authModal = document.getElementById('auth-modal');
    document.getElementById('login-btn').addEventListener('click', () => { authModal.classList.add('active'); document.body.style.overflow = 'hidden'; });
    document.getElementById('logout-btn').addEventListener('click', () => { clearAuth(); navigateToPage('home'); });

    document.getElementById('auth-close-btn').addEventListener('click', closeAuthModal);
    authModal.querySelector('.auth-overlay').addEventListener('click', closeAuthModal);

    // Prevent clicks inside the modal content from closing it
    authModal.querySelector('.auth-modal-content').addEventListener('click', e => e.stopPropagation());

    // Tabs
    authModal.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            authModal.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('login-form').style.display = tab.dataset.tab === 'login' ? 'flex' : 'none';
            document.getElementById('register-form').style.display = tab.dataset.tab === 'register' ? 'flex' : 'none';
        });
    });

    // Login
    document.getElementById('login-form').addEventListener('submit', async e => {
        e.preventDefault();
        const errEl = document.getElementById('login-error');
        errEl.textContent = '';
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: document.getElementById('login-username').value, password: document.getElementById('login-password').value })
            });
            const data = await res.json();
            if (data.success) { setAuth(data.token, data.user); closeAuthModal(); } else { errEl.textContent = data.error; }
        } catch { errEl.textContent = 'Network error'; }
    });

    // Register
    document.getElementById('register-form').addEventListener('submit', async e => {
        e.preventDefault();
        const errEl = document.getElementById('reg-error');
        errEl.textContent = '';
        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: document.getElementById('reg-username').value, email: document.getElementById('reg-email').value, password: document.getElementById('reg-password').value })
            });
            const data = await res.json();
            if (data.success) { setAuth(data.token, data.user); closeAuthModal(); } else { errEl.textContent = data.error; }
        } catch { errEl.textContent = 'Network error'; }
    });
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('active');
    document.body.style.overflow = 'auto';
}

// ==================== MODAL ====================
function setupModal() {
    const modal = document.getElementById('movie-modal');
    const close = () => { modal.classList.remove('active'); document.body.style.overflow = 'auto'; document.getElementById('trailer-iframe').src = ''; };
    modal.querySelector('.modal-close').addEventListener('click', close);
    modal.querySelector('.modal-overlay').addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { close(); closeAuthModal(); } });
}

// ==================== SCROLL TO TOP ====================
function setupScrollToTop() {
    const btn = document.getElementById('scroll-top-btn');
    window.addEventListener('scroll', () => btn.classList.toggle('visible', window.scrollY > 400));
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// ==================== ERROR HANDLING ====================
window.addEventListener('error', e => console.error('Global error:', e.error));
window.addEventListener('unhandledrejection', e => console.error('Unhandled rejection:', e.reason));

console.log('🎬 Movie Recommender App Loaded!');
