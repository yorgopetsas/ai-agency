"""
MCP (Model Context Protocol) Integration
Phase 4: RAG + MCP

Manages external tools and data sources for agents.
"""

import os
import json
from typing import Dict, List, Optional, Any, Callable
import yaml

class MCPServer:
    """Base class for MCP server"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool function"""
        self.tools[name] = func
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a registered tool"""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        return self.tools[tool_name](**kwargs)


class FileSystemServer(MCPServer):
    """File system access MCP server"""
    
    def __init__(self, base_path: str = None):
        super().__init__("file_system", enabled=True)
        self.base_path = base_path or os.getcwd()
        self._register_tools()
    
    def _register_tools(self):
        """Register file system tools"""
        self.register_tool("read_file", self.read_file)
        self.register_tool("write_file", self.write_file)
        self.register_tool("list_directory", self.list_directory)
        self.register_tool("create_directory", self.create_directory)
        self.register_tool("delete_file", self.delete_file)
    
    def read_file(self, path: str) -> Dict:
        """Read a file"""
        try:
            full_path = os.path.join(self.base_path, path)
            with open(full_path, 'r') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, path: str, content: str) -> Dict:
        """Write a file"""
        try:
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, path: str = ".") -> Dict:
        """List directory contents"""
        try:
            full_path = os.path.join(self.base_path, path)
            items = os.listdir(full_path)
            return {"success": True, "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, path: str) -> Dict:
        """Create a directory"""
        try:
            full_path = os.path.join(self.base_path, path)
            os.makedirs(full_path, exist_ok=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, path: str) -> Dict:
        """Delete a file"""
        try:
            full_path = os.path.join(self.base_path, path)
            os.remove(full_path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WebSearchServer(MCPServer):
    """Web search MCP server using DuckDuckGo (free)"""
    
    def __init__(self):
        super().__init__("web_search", enabled=True)
        self._register_tools()
    
    def _register_tools(self):
        """Register web search tools"""
        self.register_tool("search", self.search)
        self.register_tool("get_page", self.get_page)
    
    def search(self, query: str, num_results: int = 5) -> Dict:
        """Search the web using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            results = []
            for r in ddgs.text(query, max_results=num_results):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', '')
                })
            return {"success": True, "results": results}
        except ImportError:
            return {"success": False, "error": "duckduckgo-search not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_page(self, url: str) -> Dict:
        """Get page content"""
        try:
            import requests
            
            response = requests.get(url, timeout=10)
            return {
                "success": True,
                "content": response.text[:5000],  # Limit content
                "status": response.status_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class DatabaseServer(MCPServer):
    """Database query MCP server"""
    
    def __init__(self, db_path: str = None):
        super().__init__("database", enabled=True)
        self.db_path = db_path or "/Users/yorgopetsasedel/dev/opencode/ai_agency/data/multi_tenant.db"
        self._register_tools()
    
    def _register_tools(self):
        """Register database tools"""
        self.register_tool("query", self.query)
        self.register_tool("execute", self.execute)
    
    def query(self, sql: str, params: tuple = ()) -> Dict:
        """Execute a SELECT query"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute(self, sql: str, params: tuple = ()) -> Dict:
        """Execute an INSERT/UPDATE/DELETE query"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            return {"success": True, "rows_affected": rows_affected}
        except Exception as e:
            return {"success": False, "error": str(e)}


class MCPManager:
    """
    Manages all MCP servers and provides unified interface.
    """
    
    def __init__(self, config_path: str = None):
        self.servers: Dict[str, MCPServer] = {}
        
        if config_path:
            self.load_config(config_path)
        else:
            self._init_default_servers()
    
    def _init_default_servers(self):
        """Initialize default servers"""
        self.servers['file_system'] = FileSystemServer()
        self.servers['web_search'] = WebSearchServer()
        self.servers['database'] = DatabaseServer()
    
    def load_config(self, config_path: str):
        """Load MCP configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        mcp_config = config.get('mcp_servers', {})
        
        if mcp_config.get('file_system', {}).get('enabled', True):
            self.servers['file_system'] = FileSystemServer()
        
        if mcp_config.get('web_search', {}).get('enabled', True):
            self.servers['web_search'] = WebSearchServer()
        
        if mcp_config.get('database', {}).get('enabled', True):
            self.servers['database'] = DatabaseServer()
    
    def call_tool(
        self,
        server_name: str,
        tool_name: str,
        **kwargs
    ) -> Any:
        """Call a tool from a specific server"""
        server = self.servers.get(server_name)
        if not server:
            return {"error": f"Server {server_name} not found"}
        
        if not server.enabled:
            return {"error": f"Server {server_name} is disabled"}
        
        return server.call_tool(tool_name, **kwargs)
    
    def list_servers(self) -> List[str]:
        """List all available servers"""
        return [name for name, server in self.servers.items() if server.enabled]
    
    def list_tools(self, server_name: str) -> List[str]:
        """List tools for a specific server"""
        server = self.servers.get(server_name)
        if not server:
            return []
        return list(server.tools.keys())


# Default instance
mcp_manager = MCPManager()


if __name__ == "__main__":
    # Test MCP servers
    print("Available MCP servers:", mcp_manager.list_servers())
    
    # Test web search
    result = mcp_manager.call_tool('web_search', 'search', query='AI agents')
    print("\nWeb search result:", result)
