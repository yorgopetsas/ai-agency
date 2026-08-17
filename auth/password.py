"""Password hashing utilities."""
import bcrypt
import hashlib
import os


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except Exception:
        return False


def generate_api_key() -> str:
    """Generate a secure API key."""
    return os.urandom(32).hex()


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256 (deterministic for lookup)."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, hashed: str) -> bool:
    """Verify an API key against its SHA256 hash."""
    return hash_api_key(key) == hashed
