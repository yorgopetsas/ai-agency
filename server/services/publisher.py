"""
Publisher Service
=============
Publishes approved articles to the website.
"""

from typing import Dict, Optional
from pathlib import Path
import logging
from datetime import datetime
from server.services.research import ResearchService
from server.services.writer import WriterService
from server.services.images import ImageService
from server.services.storage import ArticleStore, locked_json

logger = logging.getLogger(__name__)


class PublisherService:
    """
    Service for publishing articles to the website.
    
    Usage:
        service = PublisherService()
        result = service.publish(article_id)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.website_dir = Path(__file__).parent.parent.parent / "accounts" / "internal" / "website"
        
        self.articles = ArticleStore(data_dir=self.data_dir)
        self.pending_file = self.data_dir / "pending.json"
        self.image_service = ImageService()
        
        # Ensure directories exist
        self.website_dir.mkdir(exist_ok=True)

    def publish(self, article_id: str, rating: Optional[Dict] = None) -> Dict:
        """
        Publish an approved article.
        
        Args:
            article_id: ID of the article to publish
            rating: Optional rating breakdown to store with the article
            
        Returns:
            Dict with publish result
        """
        try:
            # Load article from pending (under lock so concurrent workers are safe)
            article = None
            with locked_json(self.pending_file, default=[]) as pending:
                for item in pending:
                    if item.get('id') == article_id:
                        article = item
                        break
                if not article:
                    return {
                        "success": False,
                        "error": "Article not found"
                    }

                # Create article record
                article_id_new = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                article_record = {
                    "id": article_id_new,
                    "headline": article.get("headline", "Untitled"),
                    "overview": article.get("overview", ""),
                    "paragraphs": article.get("paragraphs", []),
                    "source_url": article.get("url", ""),
                    "image_url": article.get("image_url", ""),
                    "rating": rating or article.get("rating"),
                    "provider": article.get("provider"),
                    "published_at": datetime.now().isoformat(),
                    "date_formatted": datetime.now().strftime("%B %d, %Y")
                }

                # Fetch an image for the article (rotating sources)
                if not article_record["image_url"]:
                    image_url = self.image_service.get_image(article_record["headline"], article_id_new)
                    if image_url:
                        article_record["image_url"] = image_url

                # Save as its own file (no shared-file write race)
                self.articles.save(article_record)

                # Remove from pending (inside the same lock)
                pending[:] = [p for p in pending if p.get('id') != article_id]

            # Update website HTML (local preview + static public site)
            try:
                from server.services.site_builder import SiteBuilder
                self._update_website(self.articles.all())
                SiteBuilder().build()
            except Exception as e:
                logger.error(f"Website update failed after publish: {e}")

            return {
                "success": True,
                "id": article_record["id"],
                "headline": article_record["headline"],
                "published_at": article_record["published_at"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def reject(self, article_id: str, feedback: str = "") -> Dict:
        """
        Reject an article.
        
        Args:
            article_id: ID of the article
            feedback: Optional feedback
            
        Returns:
            Dict with result
        """
        try:
            with locked_json(self.pending_file, default=[]) as pending:
                pending[:] = [p for p in pending if p.get('id') != article_id]

            return {
                "success": True,
                "message": "Article rejected"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_articles(self) -> list:
        """Get all published articles (newest first)"""
        return self.articles.all()

    def get_pending(self) -> list:
        """Get all pending articles"""
        with locked_json(self.pending_file, default=[]) as pending:
            return [p for p in pending if p.get('type') == 'article']

    def _update_website(self, articles: list):
        """Update the website HTML with articles"""
        # Generate article cards HTML
        articles_html = ""
        for article in articles[:10]:  # Show last 10
            paragraphs_html = ""
            for para in article.get("paragraphs", [])[:3]:
                paragraphs_html += f'<p>{para}</p>\n'

            image_html = ""
            if article.get("image_url"):
                image_html = f'<img src="{article["image_url"]}" alt="{article.get("headline", "Article")}" class="article-img" loading="lazy">'

            articles_html += f"""
            <article class="news-card">
                {image_html}
                <h2>{article.get('headline', 'Untitled')}</h2>
                <p class="overview">{article.get('overview', '')}</p>
                <div class="content">
                    {paragraphs_html}
                </div>
                <div class="meta">
                    <span class="source">
                        <a href="{article.get('source_url', '#')}" target="_blank">Source</a>
                    </span>
                    <span class="date">{article.get('date_formatted', '')}</span>
                    {f'<span class="date" style="float:right">✍️ {article.get("provider", "")}</span>' if article.get('provider') else ''}
                </div>
            </article>
            """

        # Generate full HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agency News</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }}
        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.9; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .news-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem; }}
        .news-card {{ background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .news-card .article-img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 1rem; }}
        .news-card h2 {{ font-size: 1.2rem; color: #333; margin-bottom: 0.5rem; line-height: 1.3; }}
        .news-card .overview {{ color: #667; margin-bottom: 1rem; font-style: italic; }}
        .news-card .content p {{ color: #444; line-height: 1.6; margin-bottom: 0.75rem; }}
        .news-card .meta {{ display: flex; justify-content: space-between; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.85rem; color: #999; }}
        .news-card .source a {{ color: #667eea; text-decoration: none; }}
        .news-card .source a:hover {{ text-decoration: underline; }}
        footer {{ text-align: center; padding: 2rem; color: #999; font-size: 0.9rem; }}
        @media (max-width: 768px) {{
            .news-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🤖 AI Agency News</h1>
            <p>Daily AI news curated by our multi-agent system</p>
        </div>
    </header>
    <div class="container">
        <div class="news-grid">
            {articles_html if articles_html else '''
            <div class="news-card">
                <h2>Welcome to AI Agency News</h2>
                <p class="overview">Your daily AI news will appear here.</p>
                <div class="content">
                    <p>Use the admin panel to add news from URLs.</p>
                </div>
            </div>
            '''}
        </div>
    </div>
    <footer>
        <p>Powered by AI Agency Multi-Agent System | Version 2.0</p>
    </footer>
</body>
</html>"""

        # Write to website
        index_file = self.website_dir / "index.html"
        index_file.write_text(html)


# Default instance
publisher_service = PublisherService()


if __name__ == "__main__":
    print("=" * 50)
    print("Publisher Service - Test")
    print("=" * 50)
    
    articles = publisher_service.get_articles()
    print(f"\nPublished articles: {len(articles)}")
    
    pending = publisher_service.get_pending()
    print(f"Pending articles: {len(pending)}")