"""Social media manager - orchestrates content generation and publishing."""
import os
import json
import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import asdict

from .content_generator import ContentGenerator, ContentPlan, PlatformPost
from .platforms import get_publisher, list_platforms, PlatformConfig
from .scheduler import SocialScheduler, ScheduledPost, PostStatus

logger = logging.getLogger(__name__)


class SocialMediaManager:
    """Orchestrates content generation, scheduling, and publishing."""

    def __init__(self, data_dir: str = "data", llm_client=None, client_id: str = "internal"):
        self.data_dir = data_dir
        self.client_id = client_id
        self.content_gen = ContentGenerator(llm_client=llm_client)
        self.scheduler = SocialScheduler(data_dir=data_dir)
        self.publishers = {}
        self._init_publishers()

    def _init_publishers(self):
        """Initialize all available publishers."""
        for config in list_platforms():
            publisher = get_publisher(config.name)
            if publisher:
                self.publishers[config.name] = publisher

    def get_platforms(self) -> List[Dict]:
        """Get all platform statuses."""
        statuses = []
        for name, publisher in self.publishers.items():
            status = publisher.get_status()
            statuses.append(status)
        return statuses

    def generate_content(self, article: Dict, platforms: List[str] = None) -> ContentPlan:
        """Generate social media content for an article."""
        plan = self.content_gen.generate_plan(article, platforms)
        self.content_gen.save_plan(plan, self.data_dir)
        return plan

    def queue_article(self, article_id: str, platforms: List[str] = None, delay_minutes: int = 0) -> List[str]:
        """Queue an article for publishing across platforms."""
        plan = self.content_gen.load_plan(article_id, self.data_dir)
        if not plan:
            logger.error(f"No content plan found for article {article_id}")
            return []

        post_ids = []
        for platform_name, post in plan.posts.items():
            if platforms and platform_name not in platforms:
                continue

            scheduled = ScheduledPost(
                id=str(uuid.uuid4())[:8],
                article_id=article_id,
                platform=platform_name,
                title=post.title,
                content=post.content,
                url=post.url or plan.article_url,
                client_id=self.client_id,
            )

            if delay_minutes > 0:
                from datetime import timedelta
                scheduled_time = (datetime.utcnow() + timedelta(minutes=delay_minutes)).isoformat()
                scheduled.scheduled_for = scheduled_time

            post_id = self.scheduler.queue_post(scheduled)
            post_ids.append(post_id)

        logger.info(f"Queued {len(post_ids)} posts for article {article_id}")
        return post_ids

    def publish_now(self, post_id: str, data_dir: str = None) -> Dict:
        """Immediately publish a queued post."""
        post = self.scheduler._load_post(post_id)
        if not post:
            return {"success": False, "error": f"Post {post_id} not found"}

        publisher = self.publishers.get(post.platform)
        if not publisher:
            return {"success": False, "error": f"Publisher for {post.platform} not available"}

        if not publisher.authenticated:
            return {"success": False, "error": f"Not authenticated with {post.platform}"}

        self.scheduler.mark_publishing(post_id)

        result = publisher.publish(
            title=post.title,
            content=post.content,
            url=post.url,
            data_dir=data_dir or self.data_dir,
        )

        if result.get("success"):
            self.scheduler.mark_published(
                post_id,
                post_url=result.get("post_url", ""),
                remote_post_id=result.get("post_id", ""),
            )
        else:
            self.scheduler.mark_failed(post_id, result.get("error", "Unknown error"))

        return result

    def process_queue(self, client_id: str = None) -> List[Dict]:
        """Process all due posts in the queue, optionally filtered by client."""
        results = []
        due_posts = self.scheduler.get_due_posts(client_id=client_id or self.client_id)

        for post in due_posts:
            result = self.publish_now(post.id)
            results.append({"post_id": post.id, "result": result})

        return results

    def publish_article_now(self, article: Dict, platforms: List[str] = None) -> Dict:
        """Generate and publish content for an article immediately."""
        plan = self.generate_content(article, platforms)
        results = {}

        for platform_name, post in plan.posts.items():
            if platforms and platform_name not in platforms:
                continue

            publisher = self.publishers.get(platform_name)
            if not publisher or not publisher.authenticated:
                results[platform_name] = {"success": False, "error": "Not available/authenticated"}
                continue

            result = publisher.publish(
                title=post.title,
                content=post.content,
                url=post.url or plan.article_url,
                data_dir=self.data_dir,
            )
            results[platform_name] = result

        return {
            "article_id": plan.article_id,
            "platforms": results,
            "plan_status": "published" if all(r.get("success") for r in results.values()) else "partial",
        }

    def get_scheduler_stats(self, client_id: str = None) -> Dict:
        """Get scheduler statistics, optionally filtered by client."""
        return self.scheduler.get_stats(client_id=client_id or self.client_id)

    def get_post_history(self, limit: int = 50, client_id: str = None) -> List[Dict]:
        """Get recent post history, optionally filtered by client."""
        return self.scheduler.get_history(limit, client_id=client_id or self.client_id)

    def cancel_scheduled(self, post_id: str) -> bool:
        """Cancel a scheduled post."""
        self.scheduler.cancel_post(post_id)
        return True
