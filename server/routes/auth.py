"""Authentication API routes."""
import uuid
import json
from flask import Blueprint, request, jsonify, g
from auth.password import hash_password, verify_password, generate_api_key, hash_api_key
from auth.jwt_handler import create_token, create_refresh_token, verify_token, refresh_access_token
from auth.models import auth_db, User, APIKey
from auth.middleware import require_auth, get_current_user, get_current_client_id

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()
    role = data.get("role", "user")
    client_id = data.get("client_id")
    reseller_id = data.get("reseller_id")

    if not email or not password or not name:
        return jsonify({"error": "email, password, and name are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    # Check if user exists
    existing = auth_db.get_user_by_email(email)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
        client_id=client_id,
        reseller_id=reseller_id,
    )
    auth_db.create_user(user)

    # Generate tokens
    access_token = create_token(user.id, user.email, user.role, user.client_id)
    refresh_token = create_refresh_token(user.id)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with email/password."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = auth_db.get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.status != "active":
        return jsonify({"error": "Account is not active"}), 403

    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow().isoformat()
    auth_db.update_user(user)

    # Generate tokens
    access_token = create_token(user.id, user.email, user.role, user.client_id)
    refresh_token = create_refresh_token(user.id)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """Refresh access token."""
    data = request.get_json()
    if not data or not data.get("refresh_token"):
        return jsonify({"error": "refresh_token required"}), 400

    new_token = refresh_access_token(data["refresh_token"])
    if not new_token:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    return jsonify({"access_token": new_token})


@auth_bp.route("/me", methods=["GET"])
def me():
    """Get current user info."""
    user = get_current_user()
    if not user:
        return jsonify({"user": None, "authenticated": False})
    return jsonify({"user": user.to_dict(), "authenticated": True})


@auth_bp.route("/password", methods=["PUT"])
@require_auth
def change_password():
    """Change password."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({"error": "current_password and new_password are required"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    user = get_current_user()
    if not verify_password(current_password, user.password_hash):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.password_hash = hash_password(new_password)
    auth_db.update_user(user)

    return jsonify({"message": "Password updated"})


@auth_bp.route("/api-keys", methods=["POST"])
@require_auth
def create_api_key():
    """Create a new API key."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    scopes = data.get("scopes", ["read", "write"])
    rate_limit = data.get("rate_limit", 1000)
    expires_at = data.get("expires_at")

    if not name:
        return jsonify({"error": "name is required"}), 400

    user = get_current_user()
    raw_key = generate_api_key()
    key_prefix = raw_key[:8]

    api_key = APIKey(
        id=str(uuid.uuid4()),
        user_id=user.id,
        client_id=user.client_id,
        name=name,
        key_hash=hash_api_key(raw_key),
        key_prefix=key_prefix,
        scopes=json.dumps(scopes),
        rate_limit=rate_limit,
        expires_at=expires_at,
    )
    auth_db.create_api_key(api_key)

    return jsonify({
        "id": api_key.id,
        "name": api_key.name,
        "key": raw_key,
        "key_prefix": key_prefix,
        "scopes": scopes,
        "rate_limit": api_key.rate_limit,
        "message": "Save this key - it won't be shown again",
    }), 201


@auth_bp.route("/api-keys", methods=["GET"])
@require_auth
def list_api_keys():
    """List API keys for current user."""
    user = get_current_user()
    keys = auth_db.list_api_keys(user_id=user.id)
    return jsonify({
        "keys": [
            {
                "id": k.id,
                "name": k.name,
                "key_prefix": k.key_prefix,
                "scopes": json.loads(k.scopes),
                "rate_limit": k.rate_limit,
                "status": k.status,
                "expires_at": k.expires_at,
                "last_used_at": k.last_used_at,
                "created_at": k.created_at,
            }
            for k in keys
        ]
    })


@auth_bp.route("/api-keys/<key_id>", methods=["DELETE"])
@require_auth
def delete_api_key(key_id):
    """Delete an API key."""
    user = get_current_user()
    keys = auth_db.list_api_keys(user_id=user.id)
    key = next((k for k in keys if k.id == key_id), None)
    if not key:
        return jsonify({"error": "API key not found"}), 404

    auth_db.delete_api_key(key_id)
    return jsonify({"message": "API key deleted"})


# ============================================================
# Admin-only user management
# ============================================================

@auth_bp.route("/users", methods=["GET"])
@require_auth
def list_users():
    """List users (admin only)."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        return jsonify({"error": "Admin access required"}), 403

    client_id = request.args.get("client_id")
    users = auth_db.list_users(client_id=client_id)
    return jsonify({
        "users": [u.to_dict() for u in users]
    })


@auth_bp.route("/users/<user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    """Get user by ID (admin only)."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        return jsonify({"error": "Admin access required"}), 403

    target = auth_db.get_user_by_id(user_id)
    if not target:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": target.to_dict()})


@auth_bp.route("/users/<user_id>", methods=["PUT"])
@require_auth
def update_user(user_id):
    """Update user (admin only)."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        return jsonify({"error": "Admin access required"}), 403

    target = auth_db.get_user_by_id(user_id)
    if not target:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if "role" in data:
        target.role = data["role"]
    if "status" in data:
        target.status = data["status"]
    if "name" in data:
        target.name = data["name"]
    if "client_id" in data:
        target.client_id = data["client_id"]

    auth_db.update_user(target)
    return jsonify({"user": target.to_dict()})


@auth_bp.route("/users/<user_id>", methods=["DELETE"])
@require_auth
def delete_user(user_id):
    """Delete user (admin only)."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        return jsonify({"error": "Admin access required"}), 403

    target = auth_db.get_user_by_id(user_id)
    if not target:
        return jsonify({"error": "User not found"}), 404

    auth_db.delete_user(user_id)
    return jsonify({"message": "User deleted"})
