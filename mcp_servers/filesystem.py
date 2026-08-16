#!/usr/bin/env python3
"""
MCP File System Server
====================
Provides file system access through MCP protocol.

Usage:
    from mcp_servers.filesystem import FileSystemMCPServer
    server = FileSystemMCPServer()
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class FileSystemMCPServer:
    """
    MCP server for file system operations.
    Connects to AI agents via Model Context Protocol.
    """

    def __init__(self, root_path: Optional[str] = None):
        """
        Initialize the file system MCP server.

        Args:
            root_path: Root path for file operations (None = home directory)
        """
        self.root_path = root_path or os.path.expanduser("~")
        self.name = "filesystem"
        self.description = "File system operations - read, write, list files"

    def list_tools(self) -> List[Dict]:
        """Return list of available tools"""
        return [
            {
                "name": "read_file",
                "description": "Read contents of a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to write to"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "List files in a directory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "file_exists",
                "description": "Check if a file exists",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to check"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files by pattern",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory to search"},
                        "pattern": {"type": "string", "description": "File pattern (e.g., *.py)"}
                    },
                    "required": ["directory", "pattern"]
                }
            }
        ]

    # Tool Implementations

    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read contents of a file.

        Args:
            path: Path to the file

        Returns:
            Dict with content and metadata
        """
        try:
            full_path = self._resolve_path(path)
            if not os.path.exists(full_path):
                return {"error": f"File not found: {path}"}

            if not os.path.isfile(full_path):
                return {"error": f"Not a file: {path}"}

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "success": True,
                "path": path,
                "content": content,
                "size": os.path.getsize(full_path),
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            path: Path to write to
            content: Content to write

        Returns:
            Dict with result
        """
        try:
            full_path = self._resolve_path(path)

            # Create parent directories if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "path": path,
                "bytes_written": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {"error": str(e)}

    def list_directory(self, path: str) -> Dict[str, Any]:
        """
        List files in a directory.

        Args:
            path: Directory path

        Returns:
            Dict with file list
        """
        try:
            full_path = self._resolve_path(path)
            if not os.path.exists(full_path):
                return {"error": f"Directory not found: {path}"}

            if not os.path.isdir(full_path):
                return {"error": f"Not a directory: {path}"}

            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                files.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None
                })

            return {
                "success": True,
                "path": path,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}

    def file_exists(self, path: str) -> Dict[str, Any]:
        """
        Check if a file exists.

        Args:
            path: File path to check

        Returns:
            Dict with result
        """
        try:
            full_path = self._resolve_path(path)
            exists = os.path.exists(full_path)

            return {
                "success": True,
                "path": path,
                "exists": exists,
                "is_file": os.path.isfile(full_path) if exists else None,
                "is_directory": os.path.isdir(full_path) if exists else None
            }
        except Exception as e:
            return {"error": str(e)}

    def search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """
        Search for files matching a pattern.

        Args:
            directory: Directory to search
            pattern: File pattern (e.g., *.py)

        Returns:
            Dict with matching files
        """
        try:
            full_path = self._resolve_path(directory)
            if not os.path.exists(full_path):
                return {"error": f"Directory not found: {directory}"}

            from glob import glob
            matches = glob(os.path.join(full_path, pattern), recursive=True)

            return {
                "success": True,
                "directory": directory,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"error": str(e)}

    def _resolve_path(self, path: str) -> str:
        """Resolve a relative path to full path"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.root_path, path)


# Default instance
server = FileSystemMCPServer()


# ============================================================
# Main - For Testing
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("MCP File System Server")
    print("=" * 50)

    # Test tools list
    tools = server.list_tools()
    print(f"\nAvailable tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # Test with a real file
    print("\nTest - Read current directory:")
    result = server.list_directory(".")
    if result.get("success"):
        print(f"  Files: {result['count']}")
    else:
        print(f"  Error: {result.get('error')}")