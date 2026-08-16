"""
Writer Service
=============
Takes a summary and generates a full article using the LLM router.
"""

from typing import Dict, Optional
import json
from pathlib import Path
from datetime import datetime

from server.services.llm import llm_client
from server.services.storage import locked_json, read_json


class WriterService:
    """
    Service for writing articles from summaries.
    
    Usage:
        service = WriterService()
        result = service.write(summary, url)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.pending_file = self.data_dir / "pending.json"

    def write(self, summary: str, url: str, title: str = "", provider: Optional[str] = None) -> Dict:
        """
        Write an article from a summary.
        
        Args:
            summary: Research summary to expand
            url: Source URL for citation
            title: Optional title from research (for reference)
            provider: Optional LLM provider name (per-article rotation)
            
        Returns:
            Dict with article content
        """
        try:
            # Generate article with the LLM router
            article = self._generate_article(summary, url, title, provider=provider)
            if not article:
                return {
                    "success": False,
                    "error": "Failed to generate article"
                }

            # Parse article into components
            parsed = self._parse_article(article)
            
            # Use the provided title from research if available, otherwise use parsed
            final_headline = title if title else parsed.get("headline", "Untitled")
            
            # Save to pending
            pending_item = {
                "id": f"pending_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "article",
                "url": url,
                "original_title": title,  # Title from research
                "headline": final_headline,  # Final headline for article
                "summary": summary,
                "overview": parsed.get("overview", ""),
                "paragraphs": parsed.get("paragraphs", []),
                "content": article.get("text", ""),
                "status": "pending_approval",
                "provider": article.get("provider"),
                "created_at": datetime.now().isoformat()
            }
            self._save_pending(pending_item)

            return {
                "success": True,
                "id": pending_item["id"],
                "headline": final_headline,
                "overview": parsed.get("overview"),
                "paragraphs": parsed.get("paragraphs"),
                "provider": article.get("provider"),
                "status": "pending_approval"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_article(self, summary: str, url: str, title: str = "", provider: Optional[str] = None) -> Optional[Dict]:
        """Generate article using the LLM router"""
        try:
            prompt = f"""Write a news article based on the following summary.
Focus on accuracy to the source and make it informative.

Format:
- HEADLINE: A catchy, informative headline (max 10 words)
- OVERVIEW: One paragraph summarizing the news (2-3 sentences)
- PARAGRAPH 1: First body paragraph with key details
- PARAGRAPH 2: Second body paragraph with implications or context
- PARAGRAPH 3: Third body paragraph with future outlook or call to action

Source: {url}

Summary:
{summary}

Article:"""

            result = llm_client.generate(
                prompt,
                max_tokens=800,
                temperature=0.7,
                preferred=provider
            )
            if not result.get("success"):
                print(f"LLM error: {result.get('error')}")
                return None

            return {
                "text": result["text"],
                "provider": result.get("provider")
            }

        except Exception as e:
            print(f"Error generating article: {e}")
            return None

    def _parse_article(self, article: Dict) -> Dict:
        """Parse article into components"""
        text = article["text"] if isinstance(article, dict) else article
        lines = text.strip().split('\n')
        
        headline = ""
        overview = ""
        paragraphs = []
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_upper = line.upper()
            
            if line_upper.startswith('HEADLINE:'):
                headline = line.replace('HEADLINE:', '', 1).strip()
            elif line_upper.startswith('OVERVIEW:'):
                if content_lines:
                    overview = ' '.join(content_lines)
                    content_lines = []
                current_section = 'overview'
                content_lines.append(line.replace('OVERVIEW:', '', 1).strip())
            elif 'PARAGRAPH' in line_upper and ':' in line:
                if content_lines:
                    if current_section == 'overview':
                        overview = ' '.join(content_lines)
                    else:
                        paragraphs.append(' '.join(content_lines))
                    content_lines = []
                current_section = 'paragraph'
                content_lines.append(line.split(':', 1)[1].strip())
            elif current_section:
                content_lines.append(line)
        
        # Add last content
        if content_lines:
            if current_section == 'overview':
                overview = ' '.join(content_lines)
            else:
                paragraphs.append(' '.join(content_lines))
        
        return {
            "headline": headline or "Untitled",
            "overview": overview,
            "paragraphs": paragraphs[:3]
        }

    def _save_pending(self, item: Dict):
        """Save item to pending list"""
        with locked_json(self.pending_file, default=[]) as pending:
            pending.append(item)

    def _load_pending(self) -> list:
        """Load pending list"""
        return read_json(self.pending_file, default=[])

    def get_pending(self) -> list:
        """Get all pending articles"""
        pending = self._load_pending()
        return [p for p in pending if p.get('type') == 'article']

    def remove_pending(self, item_id: str):
        """Remove item from pending list"""
        with locked_json(self.pending_file, default=[]) as pending:
            pending[:] = [p for p in pending if p.get('id') != item_id]


# Default instance
writer_service = WriterService()


if __name__ == "__main__":
    print("=" * 50)
    print("Writer Service - Test")
    print("=" * 50)
    
    # Test summary
    test_summary = "NVIDIA announces new AI Agent SDK features including autonomous task execution, improved reasoning capabilities, and integration with popular frameworks like LangChain and LlamaIndex."
    
    result = writer_service.write(test_summary, "https://example.com/news")
    
    if result.get("success"):
        print(f"\n✅ Success!")
        print(f"Headline: {result['headline']}")
        print(f"Overview: {result['overview']}")
        print(f"Paragraphs: {len(result['paragraphs'])}")
    else:
        print(f"\n❌ Error: {result.get('error')}")