"""JWT token handler."""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict


JWT_SECRET = os.environ.get("JWT_SECRET", "ai-agency-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
JWT_REFRESH_EXPIRY_DAYS = 30


def create_token(user_id: str, email: str, role: str = "user", client_id: str = None) -> str:
    """Create a JWT access token."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    if client_id:
        payload["client_id"] = client_id
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=JWT_REFRESH_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Create a new access token from a refresh token."""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    return create_token(
        user_id=payload["sub"],
        email=payload.get("email", ""),
        role=payload.get("role", "user"),
        client_id=payload.get("client_id"),
    )


def decode_token(token: str) -> Optional[Dict]:
    """Decode a token without verification (for inspection)."""
    try:
        return jwt.decode(token, options={"verify_exp": False})
    except Exception:
        return None
