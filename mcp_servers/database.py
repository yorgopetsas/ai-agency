#!/usr/bin/env python3
"""
MCP Database Server
================
Provides SQLite database access through MCP protocol.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseMCPServer:
    """
    MCP server for SQLite database operations.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database MCP server.

        Args:
            db_path: Path to SQLite database
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.db_path = db_path or os.path.join(base_path, "..", "data", "multi_tenant.db")
        self.name = "database"
        self.description = "SQLite database operations"

    def list_tools(self) -> List[Dict]:
        """Return list of available tools"""
        return [
            {
                "name": "query",
                "description": "Execute a SQL query",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "SQL query"},
                        "client_id": {"type": "string", "description": "Client ID for isolation"}
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "get_table_info",
                "description": "Get information about a table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"}
                    },
                    "required": ["table"]
                }
            },
            {
                "name": "get_usage_stats",
                "description": "Get usage statistics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client ID"}
                    }
                }
            },
            {
                "name": "count_records",
                "description": "Count records in a table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "client_id": {"type": "string", "description": "Client ID for isolation"}
                    },
                    "required": ["table"]
                }
            }
        ]

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a SQL query.

        Args:
            sql: SQL query
            client_id: Client ID for isolation

        Returns:
            Query results
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Inject client_id if needed
            if client_id and "SELECT" in sql.upper() and "WHERE" not in sql.upper():
                sql = sql + " WHERE client_id = ?"
                cursor.execute(sql, (client_id,))
            elif client_id and "WHERE" not in sql.upper():
                sql = sql + " WHERE client_id = ?"
                cursor.execute(sql, (client_id,))
            else:
                cursor.execute(sql)

            rows = cursor.fetchall()
            columns = cursor.description

            results = []
            for row in rows:
                results.append(dict(row))

            conn.close()

            return {
                "success": True,
                "sql": sql,
                "rows": results,
                "count": len(results),
                "columns": [col[0] for col in columns] if columns else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_table_info(self, table: str) -> Dict[str, Any]:
        """
        Get table schema information.

        Args:
            table: Table name

        Returns:
            Table schema
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            conn.close()

            return {
                "success": True,
                "table": table,
                "columns": [{"name": col[1], "type": col[2]} for col in columns],
                "count": len(columns)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_usage_stats(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics.

        Args:
            client_id: Client ID

        Returns:
            Usage statistics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if client_id:
                cursor.execute("SELECT * FROM usage WHERE client_id = ?", (client_id,))
            else:
                cursor.execute("SELECT * FROM usage")

            rows = cursor.fetchall()
            conn.close()

            return {
                "success": True,
                "stats": [dict(row) for row in rows],
                "total": len(rows)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def count_records(self, table: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Count records in a table.

        Args:
            table: Table name
            client_id: Client ID for isolation

        Returns:
            Record count
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if client_id:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table} WHERE client_id = ?", (client_id,))
            else:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")

            count = cursor.fetchone()[0]
            conn.close()

            return {
                "success": True,
                "table": table,
                "count": count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Default instance
server = DatabaseMCPServer()


if __name__ == "__main__":
    print("=" * 50)
    print("MCP Database Server")
    print("=" * 50)

    tools = server.list_tools()
    print(f"\nAvailable tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}")

    print("\nTest - List tables:")
    try:
        conn = sqlite3.connect(server.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  Tables: {[t[0] for t in tables]}")
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")