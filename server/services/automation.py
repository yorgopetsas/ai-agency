"""
Automation Service
================
Automatically fetches news from RSS feeds and runs the research → write → publish workflow.

Usage:
    service = AutomationService()
    service.run_once()  # Process all feeds once
"""

import json
import os
import logging
import feedparser
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from server.services.research import ResearchService
from server.services.writer import WriterService
from server.services.publisher import PublisherService
from server.services.rating import RatingService
from server.services.llm import llm_client
from server.services.storage import locked_json, read_json

logger = logging.getLogger(__name__)


class AutomationService:
    """
    Fetches RSS feeds and runs the full news workflow for new articles.
    """

    def __init__(self, config_path: Optional[Path] = None, data_dir: Optional[Path] = None):
        self.server_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.server_dir / "config" / "automation_config.json"
        self.data_dir = data_dir or self.server_dir / "data"

        self.researcher = ResearchService(data_dir=self.data_dir)
        self.writer = WriterService(data_dir=self.data_dir)
        self.publisher = PublisherService(data_dir=self.data_dir)
        self.rating = RatingService()

        self.config = self._load_config()
        processed_urls_file = self.config.get("processed_urls_file", "server/data/processed_urls.json")
        p = Path(processed_urls_file)
        self.processed_urls_file = p if p.is_absolute() else (self.server_dir / processed_urls_file).resolve()

        # In-memory lock to prevent concurrent runs
        self._running = False

    def _load_config(self) -> Dict:
        """Load automation config."""
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {
            "enabled": False,
            "interval_hours": 6,
            "max_articles_per_run": 5,
            "auto_publish": True,
            "auto_push_github": True,
            "feeds": [],
            "processed_urls_file": "server/data/processed_urls.json"
        }

    def _load_processed_urls(self) -> set:
        """Load URLs already processed."""
        return set(read_json(self.processed_urls_file, default=[]))

    def _save_processed_urls(self, urls: set):
        """Save processed URLs."""
        self.processed_urls_file.parent.mkdir(parents=True, exist_ok=True)
        with locked_json(self.processed_urls_file, default=[]) as data:
            data[:] = sorted(urls)

    def _get_known_urls(self) -> set:
        """Get URLs already in pending or published articles."""
        known = set()

        # Published articles
        for article in self.publisher.get_articles():
            if article.get("source_url"):
                known.add(article["source_url"])

        # Pending items
        for item in self.publisher.get_pending():
            if item.get("url"):
                known.add(item["url"])

        # Research pending items
        for item in self.researcher.get_pending():
            if item.get("url"):
                known.add(item["url"])

        return known

    def fetch_feed_urls(self) -> List[Dict]:
        """
        Fetch all feeds and return new article links.

        Returns:
            List of {"url": str, "title": str, "source": str}
        """
        feed_urls = []
        seen = set()
        max_per_feed = self.config.get("max_per_feed", 3)

        for feed in self.config.get("feeds", []):
            feed_name = feed.get("name", "Unknown")
            feed_url = feed.get("url", "")

            if not feed_url:
                continue

            feed_count = 0
            try:
                logger.info(f"Fetching feed: {feed_name} ({feed_url})")
                parsed = feedparser.parse(feed_url)

                for entry in parsed.entries[:10]:
                    link = entry.get("link", "")
                    if not link or link in seen:
                        continue

                    seen.add(link)
                    feed_urls.append({
                        "url": link,
                        "title": entry.get("title", ""),
                        "source": feed_name
                    })
                    feed_count += 1
                    if feed_count >= max_per_feed:
                        break

            except Exception as e:
                logger.error(f"Error fetching feed {feed_name}: {e}")

        return feed_urls

    def run_once(self) -> Dict:
        """
        Run the automation once: fetch feeds, process new articles.

        Returns:
            Dict with run summary
        """
        if self._running:
            return {
                "success": True,
                "message": "Automation already running",
                "skipped": True
            }

        if not self.config.get("enabled", True):
            return {
                "success": True,
                "message": "Automation disabled in config",
                "skipped": True
            }

        self._running = True
        start_time = datetime.now()

        try:
            processed_urls = self._load_processed_urls()
            known_urls = self._get_known_urls()
            all_known = processed_urls | known_urls

            new_articles = self.fetch_feed_urls()
            # Filter out already-known URLs
            new_articles = [a for a in new_articles if a["url"] not in all_known]

            max_articles = self.config.get("max_articles_per_run", 5)
            new_articles = new_articles[:max_articles]

            results = []
            for article in new_articles:
                result = self._process_article(article)
                results.append(result)
                if result.get("success"):
                    processed_urls.add(article["url"])
                else:
                    logger.warning(f"Skipped URL (will retry next run): {article['url']}")

            self._save_processed_urls(processed_urls)

            success_count = sum(1 for r in results if r.get("success"))
            published_count = sum(1 for r in results if r.get("published"))

            # Step 5: Push to GitHub if any articles were published
            github_push = None
            if published_count > 0 and self.config.get("auto_push_github", True):
                logger.info(f"Pushing {published_count} published articles to GitHub...")
                github_push = self.push_to_github()

            return {
                "success": True,
                "new_articles_found": len(new_articles),
                "processed": len(results),
                "success_count": success_count,
                "published_count": published_count,
                "skipped_count": sum(1 for r in results if r.get("skipped")),
                "min_rating": self.config.get("min_rating", 60),
                "results": results,
                "errors": [r for r in results if not r.get("success")],
                "github_push": github_push,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "ran_at": start_time.isoformat()
            }

        finally:
            self._running = False

    def _process_article(self, article: Dict) -> Dict:
        """
        Process a single article: research → rate → write → publish.

        Args:
            article: {"url", "title", "source"}
        """
        url = article["url"]
        logger.info(f"Processing article: {article.get('title', url)}")

        # Pick one LLM provider for the whole article (per-article rotation).
        # Research + write share the same model for consistent voice.
        provider = llm_client.pick()
        logger.info(f"LLM provider for this article: {provider}")

        # Step 1: Research
        research = self.researcher.research(url, provider=provider)
        if not research.get("success"):
            return {
                "success": False,
                "url": url,
                "error": f"Research failed: {research.get('error')}",
                "stage": "research"
            }

        summary = research.get("summary", "")
        title = research.get("title", article.get("title", ""))

        # Step 2: Rate the article for AI Agents relevance + quality
        rating = self.rating.rate(
            title=title,
            summary=summary,
            source=article.get("source", ""),
            published=research.get("published") or research.get("date")
        )
        min_rating = self.config.get("min_rating", 60)

        if not rating.get("is_ai_agents"):
            logger.info(f"Skipping (not AI Agents): {title}")
            return {
                "success": True,
                "url": url,
                "title": title,
                "skipped": True,
                "stage": "rated",
                "reason": "Not AI Agents content",
                "rating": rating.get("total"),
                "rating_breakdown": rating
            }

        if rating.get("total") < min_rating:
            logger.info(f"Rating {rating.get('total')} below threshold {min_rating}: {title}")
            return {
                "success": True,
                "url": url,
                "title": title,
                "skipped": True,
                "stage": "rated",
                "reason": f"Rating below threshold ({rating.get('total')} < {min_rating})",
                "rating": rating.get("total"),
                "rating_breakdown": rating
            }

        # Step 3: Write article
        written = self.writer.write(summary, url, title, provider=provider)
        if not written.get("success"):
            return {
                "success": False,
                "url": url,
                "error": f"Write failed: {written.get('error')}",
                "stage": "write"
            }

        article_id = written.get("id")

        # Step 4: Publish (if auto_publish is enabled)
        published = False
        if self.config.get("auto_publish", True):
            publish_result = self.publisher.publish(article_id, rating=rating)
            if publish_result.get("success"):
                published = True
            else:
                return {
                    "success": True,
                    "url": url,
                    "published": False,
                    "article_id": article_id,
                    "stage": "published",
                    "warning": f"Publish failed, left in pending: {publish_result.get('error')}"
                }

        return {
            "success": True,
            "url": url,
            "title": title,
            "article_id": article_id,
            "published": published,
            "provider": written.get("provider"),
            "rating": rating.get("total"),
            "rating_breakdown": rating,
            "stage": "publish" if published else "pending"
        }

    def push_to_github(self) -> Dict:
        """
        Build the static site and push to GitHub Pages.

        Returns:
            Dict with push result
        """
        try:
            root = Path(__file__).parent.parent.parent
            script = root / "scripts" / "publish_site.py"
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=120,
                cwd=root
            )
            if result.returncode == 0:
                logger.info("Successfully pushed to GitHub")
                return {"success": True, "output": result.stdout}
            else:
                logger.error(f"GitHub push failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
        except Exception as e:
            logger.error(f"GitHub push error: {e}")
            return {"success": False, "error": str(e)}

    def get_status(self) -> Dict:
        """Get automation status for display."""
        processed = self._load_processed_urls()
        return {
            "enabled": self.config.get("enabled", True),
            "interval_hours": self.config.get("interval_hours", 6),
            "max_articles_per_run": self.config.get("max_articles_per_run", 5),
            "auto_publish": self.config.get("auto_publish", True),
            "auto_push_github": self.config.get("auto_push_github", True),
            "min_rating": self.config.get("min_rating", 60),
            "image_rotation": self.publisher.image_service.providers,
            "feeds": self.config.get("feeds", []),
            "processed_urls_count": len(processed),
            "currently_running": self._running
        }


# Default instance
automation_service = AutomationService()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1 and sys.argv[1] == "run":
        result = automation_service.run_once()
        print(json.dumps(result, indent=2, default=str))
    else:
        status = automation_service.get_status()
        print(json.dumps(status, indent=2, default=str))
