"""
Research Service
==============
Fetches URL content and generates summaries using Ollama.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import json
from pathlib import Path
from datetime import datetime

from server.services.llm import llm_client
from server.services.storage import locked_json, read_json


class ResearchService:
    """
    Service for researching and summarizing web content.
    
    Usage:
        service = ResearchService()
        result = service.research("https://example.com/news")
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.pending_file = self.data_dir / "pending.json"

    def research(self, url: str, provider: Optional[str] = None) -> Dict:
        """
        Research a URL: fetch content and generate title + summary.
        
        Args:
            url: URL to research
            provider: Optional LLM provider name (per-article rotation)
            
        Returns:
            Dict with status, title, summary, and metadata
        """
        try:
            # Step 1: Fetch URL content
            content = self._fetch_url(url)
            if not content:
                return {
                    "success": False,
                    "error": "Failed to fetch URL content"
                }

            # Step 2: Extract text
            text = self._extract_text(content)
            if len(text) < 100:
                return {
                    "success": False,
                    "error": "Content too short to summarize"
                }

            # Step 3: Generate title + summary with the LLM router
            result = self._generate_title_and_summary(text, provider=provider)
            if not result or not result.get('summary'):
                return {
                    "success": False,
                    "error": "Failed to generate title and summary"
                }

            title = result.get('title', '')
            summary = result.get('summary', '')

            # Step 4: Save to pending
            pending_item = {
                "id": f"pending_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "research",
                "url": url,
                "title": title,
                "summary": summary,
                "content_preview": text[:1000],
                "status": "pending_approval",
                "provider": result.get("provider"),
                "created_at": datetime.now().isoformat()
            }
            self._save_pending(pending_item)

            return {
                "success": True,
                "id": pending_item["id"],
                "url": url,
                "title": title,
                "summary": summary,
                "provider": result.get("provider"),
                "status": "pending_approval"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 403:
                print(f"Access forbidden (403) for URL: {url}")
                return None
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            # Limit to 5000 chars for summary
            return text[:5000]
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def _generate_title_and_summary(self, text: str, provider: Optional[str] = None) -> Optional[Dict]:
        """Generate title and summary using the LLM router"""
        try:
            prompt = f"""Analyze the following content and provide:
1. TITLE: A catchy, informative headline (5-8 words max)
2. SUMMARY: One paragraph (3-5 sentences) summarizing the key points

Format your response exactly as:
TITLE: [your headline here]
SUMMARY: [your summary paragraph here]

Content:
{text[:3000]}

Response:"""

            result = llm_client.generate(
                prompt,
                max_tokens=400,
                temperature=0.3,
                preferred=provider
            )
            if not result.get("success"):
                print(f"LLM error: {result.get('error')}")
                return None

            response_text = result["text"]

            # Parse title and summary
            title = ''
            summary = ''

            for line in response_text.split('\n'):
                line = line.strip()
                if line.upper().startswith('TITLE:'):
                    title = line.replace('TITLE:', '', 1).strip()
                elif line.upper().startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '', 1).strip()

            # If parsing didn't work, try alternate format
            if not title and not summary:
                lines = response_text.split('\n')
                if lines:
                    title = lines[0].strip()
                    summary = ' '.join(l.strip() for l in lines[1:] if l.strip())

            return {
                'title': title or 'Untitled',
                'summary': summary or response_text,
                'provider': result.get("provider")
            }

        except Exception as e:
            print(f"Error generating title and summary: {e}")
            return None

    def _save_pending(self, item: Dict):
        """Save item to pending list"""
        with locked_json(self.pending_file, default=[]) as pending:
            pending.append(item)

    def _load_pending(self) -> list:
        """Load pending list"""
        return read_json(self.pending_file, default=[])

    def get_pending(self) -> list:
        """Get all pending research items"""
        pending = self._load_pending()
        return [p for p in pending if p.get('type') == 'research']

    def remove_pending(self, item_id: str):
        """Remove item from pending list"""
        with locked_json(self.pending_file, default=[]) as pending:
            pending[:] = [p for p in pending if p.get('id') != item_id]


# Default instance
research_service = ResearchService()


if __name__ == "__main__":
    print("=" * 50)
    print("Research Service - Test")
    print("=" * 50)
    
    # Test URL
    test_url = "https://nvidianews.nvidia.com/news/ai-agents"
    
    print(f"\nTesting URL: {test_url}")
    result = research_service.research(test_url)
    
    if result.get("success"):
        print(f"\n✅ Success!")
        print(f"Summary:\n{result['summary']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")