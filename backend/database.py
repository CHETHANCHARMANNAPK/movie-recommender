"""
Database Module
Handles SQLite / PostgreSQL connections and queries
Supports Users, Watchlists, Ratings, and View Tracking
"""

import os
import hashlib
import secrets
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    watchlist = relationship('Watchlist', back_populates='user', cascade='all, delete-orphan')
    ratings = relationship('Rating', back_populates='user', cascade='all, delete-orphan')
    views = relationship('UserView', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.salt = secrets.token_hex(32)
        self.password_hash = hashlib.sha256((password + self.salt).encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return hashlib.sha256((password + self.salt).encode()).hexdigest() == self.password_hash


class Movie(Base):
    """Movie model (optional DB cache)"""
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255))
    overview = Column(Text)
    genres = Column(String(500))
    keywords = Column(Text)
    vote_average = Column(Float)
    vote_count = Column(Integer)
    popularity = Column(Float)
    budget = Column(Integer)
    revenue = Column(Integer)
    runtime = Column(Integer)
    release_date = Column(String(50))
    poster_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


class Watchlist(Base):
    """User watchlist / favourites"""
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='watchlist')

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_watchlist'),
    )


class Rating(Base):
    """User movie ratings (1-5 stars)"""
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # 1.0 – 5.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='ratings')

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_rating'),
    )


class UserView(Base):
    """Track user views for personalisation"""
    __tablename__ = 'user_views'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='views')


# ─── Database Wrapper ─────────────────────────────────────────────────

class Database:
    """Database connection and operations"""

    def __init__(self):
        db_url = os.getenv('DATABASE_URL', None)
        if db_url is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'movies.db')
            db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # ── User helpers ──────────────────────────────────────────────────

    def create_user(self, username, email, password):
        existing = self.session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            return None, 'Username or email already exists'
        user = User(username=username, email=email)
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user, None

    def authenticate_user(self, username, password):
        user = self.session.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    # ── Watchlist helpers ─────────────────────────────────────────────

    def add_to_watchlist(self, user_id, movie_id):
        existing = self.session.query(Watchlist).filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing:
            return False
        entry = Watchlist(user_id=user_id, movie_id=movie_id)
        self.session.add(entry)
        self.session.commit()
        return True

    def remove_from_watchlist(self, user_id, movie_id):
        entry = self.session.query(Watchlist).filter_by(user_id=user_id, movie_id=movie_id).first()
        if entry:
            self.session.delete(entry)
            self.session.commit()
            return True
        return False

    def get_watchlist(self, user_id):
        entries = self.session.query(Watchlist).filter_by(user_id=user_id).order_by(Watchlist.added_at.desc()).all()
        return [e.movie_id for e in entries]

    def is_in_watchlist(self, user_id, movie_id):
        return self.session.query(Watchlist).filter_by(user_id=user_id, movie_id=movie_id).first() is not None

    # ── Rating helpers ────────────────────────────────────────────────

    def rate_movie(self, user_id, movie_id, score):
        score = max(1.0, min(5.0, float(score)))
        existing = self.session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing:
            existing.score = score
            existing.updated_at = datetime.utcnow()
        else:
            existing = Rating(user_id=user_id, movie_id=movie_id, score=score)
            self.session.add(existing)
        self.session.commit()
        return existing

    def get_user_rating(self, user_id, movie_id):
        r = self.session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id).first()
        return r.score if r else None

    def get_user_ratings(self, user_id):
        ratings = self.session.query(Rating).filter_by(user_id=user_id).all()
        return {r.movie_id: r.score for r in ratings}

    def get_all_ratings(self):
        """Return all ratings as list of (user_id, movie_id, score)"""
        return [(r.user_id, r.movie_id, r.score) for r in self.session.query(Rating).all()]

    # ── View tracking helpers ─────────────────────────────────────────

    def track_view(self, user_id, movie_id):
        view = UserView(user_id=user_id, movie_id=movie_id)
        self.session.add(view)
        self.session.commit()

    def get_recent_views(self, user_id, limit=10):
        views = (self.session.query(UserView)
                 .filter_by(user_id=user_id)
                 .order_by(UserView.viewed_at.desc())
                 .limit(limit * 2)
                 .all())
        seen = set()
        result = []
        for v in views:
            if v.movie_id not in seen:
                seen.add(v.movie_id)
                result.append(v.movie_id)
            if len(result) >= limit:
                break
        return result

    # ── Generic ───────────────────────────────────────────────────────

    def close(self):
        self.session.close()
