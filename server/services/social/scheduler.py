"""Social media scheduler - queue posts, rate limits, retry."""
import os
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class PostStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


@dataclass
class ScheduledPost:
    id: str
    article_id: str
    platform: str
    title: str
    content: str
    url: str = ""
    status: str = PostStatus.PENDING
    scheduled_for: str = ""
    published_at: str = ""
    post_id: str = ""
    post_url: str = ""
    error: str = ""
    retries: int = 0
    max_retries: int = 3
    client_id: str = "internal"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.scheduled_for:
            self.scheduled_for = self.created_at


class SocialScheduler:
    """Manages post scheduling, queue, and retries."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.queue_dir = os.path.join(data_dir, "social_queue")
        os.makedirs(self.queue_dir, exist_ok=True)
        self._rate_file = os.path.join(data_dir, "social_rate_limits.json")

    def queue_post(self, post: ScheduledPost) -> str:
        """Add a post to the queue."""
        post.status = PostStatus.QUEUED
        self._save_post(post)
        logger.info(f"Queued post {post.id} for {post.platform}")
        return post.id

    def schedule_post(self, post: ScheduledPost, scheduled_for: str) -> str:
        """Schedule a post for a specific time."""
        post.scheduled_for = scheduled_for
        post.status = PostStatus.QUEUED
        self._save_post(post)
        logger.info(f"Scheduled post {post.id} for {scheduled_for}")
        return post.id

    def get_due_posts(self, client_id: str = None) -> List[ScheduledPost]:
        """Get posts that are due to be published, optionally filtered by client."""
        now = datetime.utcnow().isoformat()
        due = []
        for post in self._load_all_posts(client_id=client_id):
            if post.status == PostStatus.QUEUED and post.scheduled_for <= now:
                due.append(post)
        return due

    def get_pending_posts(self, client_id: str = None) -> List[ScheduledPost]:
        """Get all pending/queued posts, optionally filtered by client."""
        return [
            p for p in self._load_all_posts(client_id=client_id)
            if p.status in (PostStatus.PENDING, PostStatus.QUEUED, PostStatus.RETRY)
        ]

    def mark_publishing(self, post_id: str):
        """Mark a post as currently being published."""
        post = self._load_post(post_id)
        if post:
            post.status = PostStatus.PUBLISHING
            self._save_post(post)

    def mark_published(self, post_id: str, post_url: str = "", remote_post_id: str = ""):
        """Mark a post as successfully published."""
        post = self._load_post(post_id)
        if post:
            post.status = PostStatus.PUBLISHED
            post.published_at = datetime.utcnow().isoformat()
            post.post_url = post_url
            post.post_id = remote_post_id
            self._save_post(post)
            logger.info(f"Marked post {post_id} as published")

    def mark_failed(self, post_id: str, error: str):
        """Mark a post as failed, schedule retry if under limit."""
        post = self._load_post(post_id)
        if post:
            post.error = error
            post.retries += 1
            if post.retries < post.max_retries:
                post.status = PostStatus.RETRY
                delay_minutes = 2 ** post.retries * 5
                post.scheduled_for = (
                    datetime.utcnow() + timedelta(minutes=delay_minutes)
                ).isoformat()
                logger.info(f"Post {post_id} failed, retry {post.retries} in {delay_minutes}min")
            else:
                post.status = PostStatus.FAILED
                logger.error(f"Post {post_id} failed permanently after {post.retries} retries")
            self._save_post(post)

    def cancel_post(self, post_id: str):
        """Cancel a scheduled post."""
        post = self._load_post(post_id)
        if post:
            post.status = PostStatus.CANCELLED
            self._save_post(post)

    def get_stats(self, client_id: str = None) -> Dict:
        """Get scheduler statistics, optionally filtered by client."""
        posts = self._load_all_posts(client_id=client_id)
        return {
            "total": len(posts),
            "pending": sum(1 for p in posts if p.status == PostStatus.QUEUED),
            "published": sum(1 for p in posts if p.status == PostStatus.PUBLISHED),
            "failed": sum(1 for p in posts if p.status == PostStatus.FAILED),
            "retry": sum(1 for p in posts if p.status == PostStatus.RETRY),
            "by_platform": self._count_by_platform(posts),
        }

    def get_history(self, limit: int = 50, client_id: str = None) -> List[Dict]:
        """Get recent post history, optionally filtered by client."""
        posts = self._load_all_posts(client_id=client_id)
        published = [p for p in posts if p.status == PostStatus.PUBLISHED]
        published.sort(key=lambda p: p.published_at or "", reverse=True)
        return [asdict(p) for p in published[:limit]]

    def _save_post(self, post: ScheduledPost):
        """Save a post to disk."""
        post_file = os.path.join(self.queue_dir, f"{post.id}.json")
        with open(post_file, "w") as f:
            json.dump(asdict(post), f, indent=2)

    def _load_post(self, post_id: str) -> Optional[ScheduledPost]:
        """Load a post from disk."""
        post_file = os.path.join(self.queue_dir, f"{post_id}.json")
        if not os.path.exists(post_file):
            return None
        with open(post_file) as f:
            data = json.load(f)
        return ScheduledPost(**data)

    def _load_all_posts(self, client_id: str = None) -> List[ScheduledPost]:
        """Load all posts from disk, optionally filtered by client."""
        posts = []
        if not os.path.exists(self.queue_dir):
            return posts
        for fname in os.listdir(self.queue_dir):
            if fname.endswith(".json"):
                post_file = os.path.join(self.queue_dir, fname)
                try:
                    with open(post_file) as f:
                        data = json.load(f)
                    post = ScheduledPost(**data)
                    if client_id and post.client_id != client_id:
                        continue
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to load post {fname}: {e}")
        return posts

    def _count_by_platform(self, posts: List[ScheduledPost]) -> Dict:
        """Count posts by platform."""
        counts = {}
        for post in posts:
            counts[post.platform] = counts.get(post.platform, 0) + 1
        return counts

    def cleanup_old_posts(self, days: int = 30):
        """Remove old published posts."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        for post in self._load_all_posts():
            if post.status == PostStatus.PUBLISHED and post.published_at < cutoff:
                post_file = os.path.join(self.queue_dir, f"{post.id}.json")
                os.remove(post_file)
                logger.debug(f"Cleaned up old post {post.id}")
