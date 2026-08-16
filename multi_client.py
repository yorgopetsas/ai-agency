"""
Phase 6: Multi-Client Expansion

Implements multi-tenant architecture with row-level security.
Every query MUST include client_id for data isolation.
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = "/Users/yorgopetsasedel/dev/opencode/ai_agency/data/multi_tenant.db"

class ClientIsolationError(Exception):
    """Raised when client isolation is violated"""
    pass

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def init_database():
    """Initialize database with multi-tenant schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'client',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create agents table with client_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            config TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create tasks table with client_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            title TEXT NOT NULL,
            status TEXT DEFAULT 'queued',
            priority INTEGER DEFAULT 2,
            depends_on TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create meetings table with client_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            decisions TEXT,
            participants TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create memory table with client_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            agent_id TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create knowledge table with client_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            agent_id TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create usage tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id TEXT PRIMARY KEY,
            client_id TEXT REFERENCES accounts(id),
            metric TEXT NOT NULL,
            value INTEGER,
            period TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_client ON agents(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_client ON tasks(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_client ON meetings(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_client ON memory(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_client ON knowledge(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_client ON usage(client_id)")
    
    # Check if internal account exists, if not create it
    cursor.execute("SELECT id FROM accounts WHERE id = 'internal'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO accounts (id, name, type, status) 
            VALUES ('internal', 'AI Agency Internal', 'internal', 'active')
        """)
    
    conn.commit()
    conn.close()
    print("Database initialized with multi-tenant schema")


class ClientManager:
    """Manages client accounts with mandatory client_id isolation"""
    
    def __init__(self):
        init_database()  # Ensure tables exist
        self._ensure_internal_account()
    
    def _ensure_internal_account(self):
        """Ensure internal account exists"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE id = 'internal'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO accounts (id, name, type, status) 
                VALUES ('internal', 'AI Agency Internal', 'internal', 'active')
            """)
            conn.commit()
        conn.close()
    
    def create_client(self, name: str) -> str:
        """
        Create a new client account.
        Returns client_id.
        """
        client_id = str(uuid.uuid4())
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO accounts (id, name, type, status)
            VALUES (?, ?, 'client', 'pending')
        """, [client_id, name])
        
        # Create default agents for client
        default_roles = ['RESEARCH', 'WRITER', 'DEVELOPER', 'DESIGNER', 'ANALYST', 'REVIEWER']
        for role in default_roles:
            cursor.execute("""
                INSERT INTO agents (id, client_id, name, role, config)
                VALUES (?, ?, ?, ?, '{}')
            """, [str(uuid.uuid4()), client_id, role.lower(), role])
        
        conn.commit()
        conn.close()
        
        return client_id
    
    def list_clients(self) -> List[Dict]:
        """List all clients"""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM accounts ORDER BY created_at DESC")
        clients = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return clients
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID"""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM accounts WHERE id = ?", [client_id])
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def activate_client(self, client_id: str):
        """Activate a client account"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE accounts SET status = 'active' WHERE id = ?
        """, [client_id])
        
        conn.commit()
        conn.close()
    
    def deactivate_client(self, client_id: str):
        """Deactivate a client account"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE accounts SET status = 'inactive' WHERE id = ?
        """, [client_id])
        
        conn.commit()
        conn.close()


class IsolatedQuery:
    """
    Context manager for executing queries with mandatory client_id.
    
    Usage:
        with IsolatedQuery(client_id) as q:
            results = q.execute("SELECT * FROM tasks")
    """
    
    def __init__(self, client_id: Optional[str], allow_internal: bool = True):
        self.client_id = client_id
        self.allow_internal = allow_internal
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        # Allow internal/system calls without client_id
        if self.allow_internal and (self.client_id is None or self.client_id == 'internal'):
            self.conn = get_connection()
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            return self
        
        if not self.client_id:
            raise ClientIsolationError("client_id is required for all queries")
        
        # Validate client exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM accounts WHERE id = ?", [self.client_id])
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ClientIsolationError(f"Client {self.client_id} not found")
        
        if row['status'] != 'active':
            raise ClientIsolationError(f"Client {self.client_id} is not active")
        
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        return False
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query with automatic client_id filtering"""
        # Inject client_id into WHERE clause if not present
        if self.client_id and self.client_id != 'internal':
            # Add client_id to query if not present
            if 'WHERE' not in query.upper():
                query = query + " WHERE client_id = ?"
                params = params + (self.client_id,)
            elif 'client_id' not in query:
                # Find AND/OR and inject
                query = query.replace('WHERE', 'WHERE client_id = ? AND')
                params = (self.client_id,) + params
        
        self.cursor.execute(query, params)
        self.conn.commit()
        return [dict(row) for row in self.cursor.fetchall()]
    
    def execute_single(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute query and return single result"""
        results = self.execute(query, params)
        return results[0] if results else None


class UsageTracker:
    """Track usage metrics per client"""
    
    def __init__(self):
        pass
    
    def record(self, client_id: str, metric: str, value: int):
        """Record a usage metric"""
        conn = get_connection()
        cursor = conn.cursor()
        
        period = datetime.now().strftime("%Y-%m")
        
        cursor.execute("""
            INSERT INTO usage (id, client_id, metric, value, period)
            VALUES (?, ?, ?, ?, ?)
        """, [str(uuid.uuid4()), client_id, metric, value, period])
        
        conn.commit()
        conn.close()
    
    def get_usage(self, client_id: str, period: str = None) -> List[Dict]:
        """Get usage for a client"""
        if period is None:
            period = datetime.now().strftime("%Y-%m")
        
        with IsolatedQuery(client_id) as q:
            return q.execute(
                "SELECT * FROM usage WHERE period = ?",
                (period,)
            )


# Default instances
client_manager = ClientManager()
usage_tracker = UsageTracker()


if __name__ == "__main__":
    init_database()
    client_manager = ClientManager()
    print("Multi-client database initialized!")
    
    # List clients
    clients = client_manager.list_clients()
    print(f"\nClients in system: {len(clients)}")
    for c in clients:
        print(f"  - {c['name']} ({c['status']})")
