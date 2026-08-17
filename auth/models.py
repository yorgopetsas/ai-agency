"""User and API Key models."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "auth.db")


@dataclass
class User:
    id: str
    email: str
    name: str
    password_hash: str
    role: str = "user"
    client_id: Optional[str] = None
    reseller_id: Optional[str] = None
    status: str = "active"
    last_login_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self, include_hash: bool = False) -> Dict:
        """Convert to dictionary, optionally excluding password hash."""
        data = asdict(self)
        if not include_hash:
            data.pop("password_hash", None)
        return data


@dataclass
class APIKey:
    id: str
    user_id: str
    client_id: Optional[str]
    name: str
    key_hash: str
    key_prefix: str
    scopes: str = '["read", "write"]'
    rate_limit: int = 1000
    status: str = "active"
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class AuthDB:
    """Database operations for authentication."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    client_id TEXT,
                    reseller_id TEXT,
                    status TEXT DEFAULT 'active',
                    last_login_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES users(id),
                    client_id TEXT,
                    name TEXT NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    key_prefix TEXT NOT NULL,
                    scopes TEXT DEFAULT '["read", "write"]',
                    rate_limit INTEGER DEFAULT 1000,
                    status TEXT DEFAULT 'active',
                    expires_at TEXT,
                    last_used_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
                CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
            """)

    def create_user(self, user: User) -> User:
        """Create a new user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO users (id, email, name, password_hash, role, client_id, reseller_id, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user.id, user.email, user.name, user.password_hash, user.role,
                 user.client_id, user.reseller_id, user.status, user.created_at, user.updated_at)
            )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                return User(**dict(row))
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if row:
                return User(**dict(row))
        return None

    def update_user(self, user: User) -> User:
        """Update user."""
        user.updated_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE users SET name=?, role=?, status=?, last_login_at=?, updated_at=?
                   WHERE id=?""",
                (user.name, user.role, user.status, user.last_login_at, user.updated_at, user.id)
            )
        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0

    def list_users(self, client_id: str = None, limit: int = 100) -> List[User]:
        """List users, optionally filtered by client_id."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if client_id:
                rows = conn.execute(
                    "SELECT * FROM users WHERE client_id = ? LIMIT ?",
                    (client_id, limit)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM users LIMIT ?", (limit,)).fetchall()
            return [User(**dict(row)) for row in rows]

    def create_api_key(self, api_key: APIKey) -> APIKey:
        """Create a new API key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO api_keys (id, user_id, client_id, name, key_hash, key_prefix, scopes, rate_limit, status, expires_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (api_key.id, api_key.user_id, api_key.client_id, api_key.name,
                 api_key.key_hash, api_key.key_prefix, api_key.scopes,
                 api_key.rate_limit, api_key.status, api_key.expires_at, api_key.created_at)
            )
        return api_key

    def get_api_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Get API key by hash."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM api_keys WHERE key_hash = ?", (key_hash,)).fetchone()
            if row:
                return APIKey(**dict(row))
        return None

    def update_api_key_last_used(self, key_id: str):
        """Update API key last used timestamp."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE api_keys SET last_used_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), key_id)
            )

    def delete_api_key(self, key_id: str) -> bool:
        """Delete API key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
            return cursor.rowcount > 0

    def list_api_keys(self, user_id: str = None, client_id: str = None) -> List[APIKey]:
        """List API keys."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if user_id:
                rows = conn.execute("SELECT * FROM api_keys WHERE user_id = ?", (user_id,)).fetchall()
            elif client_id:
                rows = conn.execute("SELECT * FROM api_keys WHERE client_id = ?", (client_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM api_keys").fetchall()
            return [APIKey(**dict(row)) for row in rows]


# Singleton
auth_db = AuthDB()
