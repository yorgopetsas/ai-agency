"""
Tests for Phase 4: MCP Servers
============================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.filesystem import FileSystemMCPServer
from mcp_servers.database import DatabaseMCPServer


class TestFileSystemMCP:
    """Test file system MCP server"""

    def test_server_exists(self):
        """Test server can be instantiated"""
        server = FileSystemMCPServer()
        assert server.name == "filesystem"

    def test_list_tools(self):
        """Test tools are listed"""
        server = FileSystemMCPServer()
        tools = server.list_tools()
        assert len(tools) >= 3
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names

    def test_file_exists(self):
        """Test file exists check"""
        server = FileSystemMCPServer()
        result = server.file_exists(".")
        assert result["success"] is True
        assert result["exists"] is True


class TestDatabaseMCP:
    """Test database MCP server"""

    def test_server_exists(self):
        """Test server can be instantiated"""
        server = DatabaseMCPServer()
        assert server.name == "database"

    def test_list_tools(self):
        """Test tools are listed"""
        server = DatabaseMCPServer()
        tools = server.list_tools()
        assert len(tools) >= 3
        tool_names = [t["name"] for t in tools]
        assert "query" in tool_names
        assert "count_records" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])