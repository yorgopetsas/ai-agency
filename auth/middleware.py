"""Flask auth middleware."""
import os
import functools
import json
from flask import request, g, jsonify
from .jwt_handler import verify_token
from .models import auth_db
from .password import hash_api_key


# Auth mode: "jwt" (default), "api_key", "both"
AUTH_MODE = os.environ.get("AUTH_MODE", "both")

# Exempt routes that don't require auth (exact match only)
AUTH_EXEMPT_ROUTES = {
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh",
    "/api/auth/me",
    "/api/news",
    "/api/health",
    "/admin",
}


def extract_token_from_header() -> str:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def extract_api_key() -> str:
    """Extract API key from X-API-Key header or query parameter."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        api_key = request.args.get("api_key")
    return api_key


def authenticate_request():
    """Authenticate the current request. Sets g.user and g.client_id."""
    g.user = None
    g.client_id = None
    g.auth_method = None

    # Try JWT first
    token = extract_token_from_header()
    if token:
        payload = verify_token(token)
        if payload:
            user = auth_db.get_user_by_id(payload["sub"])
            if user and user.status == "active":
                g.user = user
                g.client_id = user.client_id
                g.auth_method = "jwt"
                return

    # Try API key
    api_key = extract_api_key()
    if api_key:
        key_hash = hash_api_key(api_key)
        api_key_obj = auth_db.get_api_key_by_hash(key_hash)
        if api_key_obj and api_key_obj.status == "active":
            # Check expiry
            if api_key_obj.expires_at:
                from datetime import datetime
                if datetime.fromisoformat(api_key_obj.expires_at) < datetime.utcnow():
                    return

            # Update last used
            auth_db.update_api_key_last_used(api_key_obj.id)

            # Get user
            user = auth_db.get_user_by_id(api_key_obj.user_id)
            if user and user.status == "active":
                g.user = user
                g.client_id = api_key_obj.client_id or user.client_id
                g.auth_method = "api_key"
                g.api_key_scopes = json.loads(api_key_obj.scopes)
                return


def is_auth_required() -> bool:
    """Check if auth is required for current route."""
    if AUTH_MODE == "none":
        return False
    return request.path not in AUTH_EXEMPT_ROUTES


def require_auth(f):
    """Decorator: require authentication for a route."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not is_auth_required():
            return f(*args, **kwargs)
        if not g.get("user"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator: require specific role(s)."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if not is_auth_required():
                return f(*args, **kwargs)
            if not g.get("user"):
                return jsonify({"error": "Authentication required"}), 401
            if g.user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_scope(*scopes):
    """Decorator: require specific API key scopes."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if not is_auth_required():
                return f(*args, **kwargs)
            if not g.get("user"):
                return jsonify({"error": "Authentication required"}), 401
            if g.auth_method == "api_key":
                key_scopes = getattr(g, "api_key_scopes", [])
                if not any(s in key_scopes for s in scopes):
                    return jsonify({"error": "Insufficient scopes"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user():
    """Get current authenticated user (or None)."""
    return getattr(g, "user", None)


def get_current_client_id():
    """Get current client_id (or None)."""
    return getattr(g, "client_id", None)


def init_auth(app):
    """Initialize auth middleware for Flask app."""
    app.before_request(authenticate_request)

    @app.context_processor
    def inject_user():
        return {
            "current_user": g.get("user"),
            "current_client_id": g.get("client_id"),
        }
