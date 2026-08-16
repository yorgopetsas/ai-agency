#!/usr/bin/env python3
"""
MCP Web Search Server
==================
Provides web search through MCP protocol using DuckDuckGo.
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timedelta


class WebSearchMCPServer:
    """
    MCP server for web search operations.
    Uses DuckDuckGo (free, no API key needed).
    """

    def __init__(self):
        self.name = "web_search"
        self.description = "Web search using DuckDuckGo"
        self.provider = "duckduckgo"

    def list_tools(self) -> List[Dict]:
        """Return list of available tools"""
        return [
            {
                "name": "search",
                "description": "Search the web",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "description": "Max results (default 5)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_news",
                "description": "Search for recent news",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "News query"},
                        "days": {"type": "integer", "description": "Days back (default 1)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_trending",
                "description": "Get trending topics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Category (tech, business, etc.)"}
                    }
                }
            }
        ]

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web.

        Args:
            query: Search query
            max_results: Max number of results

        Returns:
            List of search results
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.search(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "body": r.get("body", "")[:200]
                    })

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except ImportError:
            return {
                "success": False,
                "error": "duckduckgo-search not installed. Run: pip install duckduckgo-search",
                "query": query
            }
        except Exception as e:
            return {"success": False, "error": str(e), "query": query}

    def search_news(self, query: str, days: int = 1) -> Dict[str, Any]:
        """
        Search for recent news.

        Args:
            query: News query
            days: Days back to search

        Returns:
            List of news articles
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.news(query, max_results=5):
                    date_str = r.get("date", "")
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "source": r.get("source", ""),
                        "date": date_str,
                        "summary": r.get("body", "")[:300]
                    })

            return {
                "success": True,
                "query": query,
                "days": days,
                "articles": results,
                "count": len(results)
            }
        except ImportError:
            return {
                "success": False,
                "error": "duckduckgo-search not installed",
                "query": query
            }
        except Exception as e:
            return {"success": False, "error": str(e), "query": query}

    def get_trending(self, category: str = "ai") -> Dict[str, Any]:
        """
        Get trending topics.

        Args:
            category: Topic category

        Returns:
            List of trending topics
        """
        return {
            "success": True,
            "category": category,
            "topics": ["AI Agents", "Claude", "OpenAI", "LLM"],
            "note": "Trending API requires paid key"
        }


# Default instance
server = WebSearchMCPServer()


if __name__ == "__main__":
    print("=" * 50)
    print("MCP Web Search Server")
    print("=" * 50)

    tools = server.list_tools()
    print(f"\nAvailable tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}")

    print("\nTest - Search for AI news:")
    result = server.search_news("AI agents", days=1)
    if result.get("success"):
        print(f"  Found {result['count']} articles")
        for article in result.get("articles", [])[:3]:
            print(f"    - {article['title'][:50]}...")
    else:
        print(f"  {result.get('error')}")