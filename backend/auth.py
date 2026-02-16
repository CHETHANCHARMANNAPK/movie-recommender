"""
JWT Authentication helpers
Simple token-based auth using PyJWT
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g

SECRET_KEY = os.getenv('JWT_SECRET', 'change-me-in-production-use-a-real-secret')
TOKEN_EXPIRY_HOURS = 72


def generate_token(user_id: int, username: str) -> str:
    """Create a signed JWT for the given user."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token: str):
    """Decode and verify a JWT. Returns payload dict or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """Decorator that requires a valid JWT in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401

        g.user_id = payload['user_id']
        g.username = payload['username']
        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Decorator that attaches user info if a valid token is present, but doesn't require it."""
    @wraps(f)
    def decorated(*args, **kwargs):
        g.user_id = None
        g.username = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            payload = decode_token(auth_header[7:])
            if payload:
                g.user_id = payload['user_id']
                g.username = payload['username']
        return f(*args, **kwargs)
    return decorated
