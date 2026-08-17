"""Billing models and database."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "auth.db")


@dataclass
class Plan:
    id: str
    name: str
    display_name: str
    description: str = ""
    price_monthly: float = 0.0
    price_yearly: float = 0.0
    quotas: str = "{}"
    features: str = "[]"
    is_active: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["quotas"] = json.loads(self.quotas) if isinstance(self.quotas, str) else self.quotas
        data["features"] = json.loads(self.features) if isinstance(self.features, str) else self.features
        return data


@dataclass
class ClientPlan:
    client_id: str
    plan_id: str
    billing_cycle: str = "monthly"
    started_at: str = ""
    expires_at: Optional[str] = None
    status: str = "active"

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UsageRecord:
    id: str
    client_id: str
    metric: str
    quantity: int = 1
    period: str = ""
    metadata: str = "{}"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.period:
            self.period = datetime.utcnow().strftime("%Y-%m")

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["metadata"] = json.loads(self.metadata) if isinstance(self.metadata, str) else self.metadata
        return data


class BillingDB:
    """Database operations for billing."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize billing tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS plans (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    price_monthly REAL DEFAULT 0,
                    price_yearly REAL DEFAULT 0,
                    quotas TEXT DEFAULT '{}',
                    features TEXT DEFAULT '[]',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS client_plans (
                    client_id TEXT PRIMARY KEY,
                    plan_id TEXT REFERENCES plans(id),
                    billing_cycle TEXT DEFAULT 'monthly',
                    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    status TEXT DEFAULT 'active'
                );

                CREATE TABLE IF NOT EXISTS usage_records (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    period TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_usage_client_period ON usage_records(client_id, period);
                CREATE INDEX IF NOT EXISTS idx_usage_metric ON usage_records(metric);
            """)

    def seed_plans(self):
        """Seed default plans if none exist."""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
            if count > 0:
                return

            plans = [
                ("free", "Free", "Free tier", "Perfect for trying out", 0, 0,
                 json.dumps({"tasks_per_month": 50, "storage_mb": 100, "users": 2, "api_calls": 1000}),
                 json.dumps(["basic_agents", "email_support"])),
                ("starter", "Starter", "Starter plan", "For small teams", 29, 290,
                 json.dumps({"tasks_per_month": 500, "storage_mb": 1000, "users": 5, "api_calls": 10000}),
                 json.dumps(["basic_agents", "priority_support", "custom_branding"])),
                ("pro", "Pro", "Professional", "For growing businesses", 99, 990,
                 json.dumps({"tasks_per_month": 5000, "storage_mb": 10000, "users": 25, "api_calls": 100000}),
                 json.dumps(["all_agents", "priority_support", "custom_branding", "analytics", "api_access"])),
                ("enterprise", "Enterprise", "Enterprise", "For large organizations", 499, 4990,
                 json.dumps({"tasks_per_month": -1, "storage_mb": -1, "users": -1, "api_calls": -1}),
                 json.dumps(["all_agents", "dedicated_support", "custom_branding", "analytics", "api_access", "sla", "custom_integrations"])),
            ]
            for plan in plans:
                conn.execute(
                    """INSERT INTO plans (id, name, display_name, description,
                       price_monthly, price_yearly, quotas, features, is_active, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
                    (*plan, datetime.utcnow().isoformat())
                )

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
            if row:
                return Plan(**dict(row))
        return None

    def list_plans(self, active_only: bool = True) -> List[Plan]:
        """List all plans."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if active_only:
                rows = conn.execute("SELECT * FROM plans WHERE is_active = 1 ORDER BY price_monthly").fetchall()
            else:
                rows = conn.execute("SELECT * FROM plans ORDER BY price_monthly").fetchall()
            return [Plan(**dict(row)) for row in rows]

    def get_client_plan(self, client_id: str) -> Optional[ClientPlan]:
        """Get current plan for a client."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM client_plans WHERE client_id = ? AND status = 'active'",
                (client_id,)
            ).fetchone()
            if row:
                return ClientPlan(**dict(row))
        return None

    def assign_plan(self, client_plan: ClientPlan) -> ClientPlan:
        """Assign a plan to a client."""
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT * FROM client_plans WHERE client_id = ?", (client_plan.client_id,)
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE client_plans SET plan_id=?, billing_cycle=?,
                       started_at=?, expires_at=?, status=?
                       WHERE client_id=?""",
                    (client_plan.plan_id, client_plan.billing_cycle,
                     client_plan.started_at, client_plan.expires_at,
                     client_plan.status, client_plan.client_id)
                )
            else:
                conn.execute(
                    """INSERT INTO client_plans (client_id, plan_id, billing_cycle,
                       started_at, expires_at, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (client_plan.client_id, client_plan.plan_id,
                     client_plan.billing_cycle, client_plan.started_at,
                     client_plan.expires_at, client_plan.status)
                )
        return client_plan

    def record_usage(self, record: UsageRecord) -> UsageRecord:
        """Record a usage event."""
        metadata_str = json.dumps(record.metadata) if isinstance(record.metadata, dict) else record.metadata
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO usage_records (id, client_id, metric, quantity, period, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (record.id, record.client_id, record.metric, record.quantity,
                 record.period, metadata_str, record.created_at)
            )
        return record

    def get_usage(self, client_id: str, metric: str = None, period: str = None) -> List[UsageRecord]:
        """Get usage records for a client."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM usage_records WHERE client_id = ?"
            params = [client_id]
            if metric:
                query += " AND metric = ?"
                params.append(metric)
            if period:
                query += " AND period = ?"
                params.append(period)
            else:
                # Default to current period
                current_period = datetime.utcnow().strftime("%Y-%m")
                query += " AND period = ?"
                params.append(current_period)
            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [UsageRecord(**dict(row)) for row in rows]

    def sum_usage(self, client_id: str, metric: str, period: str = None) -> int:
        """Sum usage for a metric in a period."""
        if not period:
            period = datetime.utcnow().strftime("%Y-%m")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT COALESCE(SUM(quantity), 0) FROM usage_records
                   WHERE client_id = ? AND metric = ? AND period = ?""",
                (client_id, metric, period)
            ).fetchone()
            return row[0] if row else 0

    def delete_usage(self, record_id: str) -> bool:
        """Delete a usage record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM usage_records WHERE id = ?", (record_id,)
            )
            return cursor.rowcount > 0


billing_db = BillingDB()
