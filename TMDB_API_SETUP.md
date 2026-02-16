# 🎬 TMDB API Setup Guide

## Why Do You Need This?

The TMDB (The Movie Database) API provides movie posters and additional metadata for your recommender system. **It's completely FREE** for non-commercial use!

## Quick Setup (5 minutes)

### 1️⃣ Register on TMDB

**Visit:** https://www.themoviedb.org/signup

- Email: Your email address
- Username: Choose a username
- Password: Choose a strong password
- Verify your email

### 2️⃣ Request API Access

**Visit:** https://www.themoviedb.org/settings/api

Or follow these steps:
1. Log in to TMDB
2. Click your profile icon (top right)
3. Go to **Settings**
4. Click **API** in the left sidebar
5. Click **"Request an API Key"**

### 3️⃣ Choose Developer Option

- Select **"Developer"** (not commercial)
- Accept the Terms of Use

### 4️⃣ Fill Application Form

```
Application Name: Movie Recommender Project
Application URL: http://localhost:5000
Application Summary: Educational movie recommendation system using machine learning
```

### 5️⃣ Copy Your API Key

You'll immediately see:
```
API Key (v3 auth): xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Copy this key! ⬆️

### 6️⃣ Add to Your Project

**Method 1: Using .env file (Recommended)**

Open `.env` file in the project root and replace the placeholder:

```env
TMDB_API_KEY=paste_your_key_here
```

**Method 2: Direct in code (Quick test)**

Open `backend/tmdb_service.py` and replace line 12:

```python
API_KEY = 'paste_your_key_here'
```

### 7️⃣ Restart Your Server

```bash
# Stop the current server (Ctrl+C)
# Start again
python backend/app.py
```

## ✅ Test if It's Working

1. Start your backend server
2. Open the frontend (`frontend/index.html`)
3. Click on any movie
4. You should see real movie posters instead of placeholders!

## 📊 TMDB API Limits (Free Tier)

- **Rate Limit**: 40 requests per 10 seconds
- **Daily Requests**: Unlimited for personal use
- **Cost**: **FREE** forever for non-commercial projects

Your project uses caching, so you won't hit the limits!

## 🔒 Security Note

**NEVER commit your API key to Git!**

The `.env` file is already in `.gitignore`, so your key is safe.

## ❌ Troubleshooting

**Problem:** Still seeing placeholder images
- ✅ Check if you copied the key correctly (no spaces)
- ✅ Restart the backend server
- ✅ Check browser console for errors

**Problem:** API key not found
- ✅ Make sure `.env` file is in the project root
- ✅ Make sure the key is on a single line
- ✅ No quotes needed around the key

**Problem:** "Invalid API key" error
- ✅ Verify you copied the **v3 API key**, not the v4 token
- ✅ Check your TMDB account is verified

## 🎉 You're All Set!

Your movie recommender now has beautiful movie posters and additional metadata!

## 📚 TMDB API Documentation

Want to add more features? Check out:
- **API Docs**: https://developers.themoviedb.org/3/
- **Image Guide**: https://developers.themoviedb.org/3/getting-started/images
- **Search Movies**: https://developers.themoviedb.org/3/search/search-movies

## 💡 What You Can Do With TMDB API

- ✅ Movie posters (already implemented)
- ✅ Backdrop images
- ✅ Actor photos
- ✅ Movie trailers
- ✅ Release dates by country
- ✅ Movie ratings
- ✅ Similar movies (different algorithm than yours)
- ✅ Trending movies
- ✅ And much more!

---

**Note:** This project works fine WITHOUT the API key too! You'll just see placeholder images instead of real posters. The recommendation engine works independently of TMDB.
