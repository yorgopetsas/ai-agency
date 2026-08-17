"""Client models and database."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "auth.db")


@dataclass
class Client:
    id: str
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    reseller_id: Optional[str] = None
    status: str = "pending"
    plan: str = "free"
    config: str = "{}"
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


class ClientDB:
    """Database operations for clients."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize client table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    company TEXT,
                    industry TEXT,
                    reseller_id TEXT,
                    status TEXT DEFAULT 'pending',
                    plan TEXT DEFAULT 'free',
                    config TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_clients_reseller ON clients(reseller_id);
                CREATE INDEX IF NOT EXISTS idx_clients_slug ON clients(slug);
                CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
            """)

    def create(self, client: Client) -> Client:
        """Create a new client."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO clients (id, name, slug, email, phone, company, industry,
                   reseller_id, status, plan, config, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (client.id, client.name, client.slug, client.email,
                 client.phone, client.company, client.industry,
                 client.reseller_id, client.status, client.plan,
                 client.config, client.created_at, client.updated_at)
            )
        return client

    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
            if row:
                return Client(**dict(row))
        return None

    def get_by_slug(self, slug: str) -> Optional[Client]:
        """Get client by slug."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM clients WHERE slug = ?", (slug,)).fetchone()
            if row:
                return Client(**dict(row))
        return None

    def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM clients WHERE email = ?", (email,)).fetchone()
            if row:
                return Client(**dict(row))
        return None

    def update(self, client: Client) -> Client:
        """Update client."""
        client.updated_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE clients SET name=?, slug=?, email=?, phone=?, company=?,
                   industry=?, reseller_id=?, status=?, plan=?, config=?, updated_at=?
                   WHERE id=?""",
                (client.name, client.slug, client.email, client.phone,
                 client.company, client.industry, client.reseller_id,
                 client.status, client.plan, client.config,
                 client.updated_at, client.id)
            )
        return client

    def delete(self, client_id: str) -> bool:
        """Delete client."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            return cursor.rowcount > 0

    def list_clients(self, reseller_id: str = None, status: str = None,
                     plan: str = None, limit: int = 100) -> List[Client]:
        """List clients with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM clients WHERE 1=1"
            params = []
            if reseller_id is not None:
                query += " AND reseller_id = ?"
                params.append(reseller_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            if plan:
                query += " AND plan = ?"
                params.append(plan)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [Client(**dict(row)) for row in rows]

    def count_by_reseller(self, reseller_id: str) -> int:
        """Count clients for a reseller."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM clients WHERE reseller_id = ?", (reseller_id,)
            ).fetchone()
            return row[0] if row else 0

    def count_by_plan(self, plan: str) -> int:
        """Count clients on a plan."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM clients WHERE plan = ?", (plan,)
            ).fetchone()
            return row[0] if row else 0


client_db = ClientDB()
