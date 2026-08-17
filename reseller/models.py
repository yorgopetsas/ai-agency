"""Reseller models and database."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "auth.db")


@dataclass
class Reseller:
    id: str
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    parent_id: Optional[str] = None
    status: str = "pending"
    tier: str = "standard"
    config: str = "{}"
    max_clients: int = 10
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["config"] = json.loads(self.config) if isinstance(self.config, str) else self.config
        return data


class ResellerDB:
    """Database operations for resellers."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize reseller tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS resellers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    company TEXT,
                    parent_id TEXT REFERENCES resellers(id),
                    status TEXT DEFAULT 'pending',
                    tier TEXT DEFAULT 'standard',
                    config TEXT DEFAULT '{}',
                    max_clients INTEGER DEFAULT 10,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_resellers_parent ON resellers(parent_id);
                CREATE INDEX IF NOT EXISTS idx_resellers_slug ON resellers(slug);
                CREATE INDEX IF NOT EXISTS idx_resellers_email ON resellers(email);
            """)

    def create(self, reseller: Reseller) -> Reseller:
        """Create a new reseller."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO resellers (id, name, slug, email, phone, company, parent_id, status, tier, config, max_clients, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (reseller.id, reseller.name, reseller.slug, reseller.email,
                 reseller.phone, reseller.company, reseller.parent_id,
                 reseller.status, reseller.tier, reseller.config,
                 reseller.max_clients, reseller.created_at, reseller.updated_at)
            )
        return reseller

    def get_by_id(self, reseller_id: str) -> Optional[Reseller]:
        """Get reseller by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM resellers WHERE id = ?", (reseller_id,)).fetchone()
            if row:
                return Reseller(**dict(row))
        return None

    def get_by_slug(self, slug: str) -> Optional[Reseller]:
        """Get reseller by slug."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM resellers WHERE slug = ?", (slug,)).fetchone()
            if row:
                return Reseller(**dict(row))
        return None

    def get_by_email(self, email: str) -> Optional[Reseller]:
        """Get reseller by email."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM resellers WHERE email = ?", (email,)).fetchone()
            if row:
                return Reseller(**dict(row))
        return None

    def update(self, reseller: Reseller) -> Reseller:
        """Update reseller."""
        reseller.updated_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE resellers SET name=?, slug=?, email=?, phone=?, company=?,
                   parent_id=?, status=?, tier=?, config=?, max_clients=?, updated_at=?
                   WHERE id=?""",
                (reseller.name, reseller.slug, reseller.email, reseller.phone,
                 reseller.company, reseller.parent_id, reseller.status,
                 reseller.tier, reseller.config, reseller.max_clients,
                 reseller.updated_at, reseller.id)
            )
        return reseller

    def delete(self, reseller_id: str) -> bool:
        """Delete reseller (only if no children)."""
        with sqlite3.connect(self.db_path) as conn:
            # Check for children
            children = conn.execute(
                "SELECT COUNT(*) FROM resellers WHERE parent_id = ?", (reseller_id,)
            ).fetchone()[0]
            if children > 0:
                return False
            cursor = conn.execute("DELETE FROM resellers WHERE id = ?", (reseller_id,))
            return cursor.rowcount > 0

    def list_resellers(self, parent_id: str = None, status: str = None, limit: int = 100) -> List[Reseller]:
        """List resellers with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM resellers WHERE 1=1"
            params = []
            if parent_id is not None:
                query += " AND parent_id = ?"
                params.append(parent_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [Reseller(**dict(row)) for row in rows]

    def get_children(self, reseller_id: str) -> List[Reseller]:
        """Get direct children of a reseller."""
        return self.list_resellers(parent_id=reseller_id)

    def get_all_descendants(self, reseller_id: str) -> List[Reseller]:
        """Get all descendants (recursive)."""
        result = []
        children = self.get_children(reseller_id)
        for child in children:
            result.append(child)
            result.extend(self.get_all_descendants(child.id))
        return result

    def count_clients(self, reseller_id: str) -> int:
        """Count clients belonging to this reseller."""
        with sqlite3.connect(self.db_path) as conn:
            try:
                row = conn.execute(
                    "SELECT COUNT(*) FROM clients WHERE reseller_id = ?", (reseller_id,)
                ).fetchone()
                return row[0] if row else 0
            except sqlite3.OperationalError:
                return 0

    def can_add_client(self, reseller_id: str) -> bool:
        """Check if reseller can add more clients."""
        reseller = self.get_by_id(reseller_id)
        if not reseller or reseller.status != "active":
            return False
        current = self.count_clients(reseller_id)
        return current < reseller.max_clients


reseller_db = ResellerDB()
