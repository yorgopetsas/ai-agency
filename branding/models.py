"""Branding models and database."""
import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "auth.db")


@dataclass
class ClientBranding:
    client_id: str
    logo_url: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    accent_color: str = "#F59E0B"
    font_family: str = "Inter"
    favicon_url: Optional[str] = None
    custom_domain: Optional[str] = None
    welcome_message: str = "Welcome!"
    footer_text: str = "Powered by Amanita AI"
    theme: str = "light"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class BrandingDB:
    """Database operations for branding."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize branding table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS client_branding (
                    client_id TEXT PRIMARY KEY,
                    logo_url TEXT,
                    primary_color TEXT DEFAULT '#3B82F6',
                    secondary_color TEXT DEFAULT '#10B981',
                    accent_color TEXT DEFAULT '#F59E0B',
                    font_family TEXT DEFAULT 'Inter',
                    favicon_url TEXT,
                    custom_domain TEXT,
                    welcome_message TEXT DEFAULT 'Welcome!',
                    footer_text TEXT DEFAULT 'Powered by Amanita AI',
                    theme TEXT DEFAULT 'light',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_branding_domain ON client_branding(custom_domain);
            """)

    def get(self, client_id: str) -> Optional[ClientBranding]:
        """Get branding for a client."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM client_branding WHERE client_id = ?", (client_id,)
            ).fetchone()
            if row:
                return ClientBranding(**dict(row))
        return None

    def get_by_domain(self, domain: str) -> Optional[ClientBranding]:
        """Get branding by custom domain."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM client_branding WHERE custom_domain = ?", (domain,)
            ).fetchone()
            if row:
                return ClientBranding(**dict(row))
        return None

    def create_or_update(self, branding: ClientBranding) -> ClientBranding:
        """Create or update branding (upsert)."""
        branding.updated_at = datetime.utcnow().isoformat()
        existing = self.get(branding.client_id)
        with sqlite3.connect(self.db_path) as conn:
            if existing:
                conn.execute(
                    """UPDATE client_branding SET logo_url=?, primary_color=?, secondary_color=?,
                       accent_color=?, font_family=?, favicon_url=?, custom_domain=?,
                       welcome_message=?, footer_text=?, theme=?, updated_at=?
                       WHERE client_id=?""",
                    (branding.logo_url, branding.primary_color, branding.secondary_color,
                     branding.accent_color, branding.font_family, branding.favicon_url,
                     branding.custom_domain, branding.welcome_message, branding.footer_text,
                     branding.theme, branding.updated_at, branding.client_id)
                )
            else:
                conn.execute(
                    """INSERT INTO client_branding (client_id, logo_url, primary_color,
                       secondary_color, accent_color, font_family, favicon_url, custom_domain,
                       welcome_message, footer_text, theme, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (branding.client_id, branding.logo_url, branding.primary_color,
                     branding.secondary_color, branding.accent_color, branding.font_family,
                     branding.favicon_url, branding.custom_domain, branding.welcome_message,
                     branding.footer_text, branding.theme, branding.created_at,
                     branding.updated_at)
                )
        return branding

    def delete(self, client_id: str) -> bool:
        """Delete branding."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM client_branding WHERE client_id = ?", (client_id,)
            )
            return cursor.rowcount > 0


branding_db = BrandingDB()
