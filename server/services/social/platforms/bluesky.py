"""Bluesky publisher - AT Protocol social network."""
import os
import logging
import requests
from typing import Dict
from .base import PlatformPublisher, PlatformConfig, register_publisher

logger = logging.getLogger(__name__)

ATProto = None
try:
    from atproto import Client, models
    ATProto = Client
except ImportError:
    pass


@register_publisher("bluesky")
class BlueskyPublisher(PlatformPublisher):
    CONFIG = PlatformConfig(
        name="bluesky",
        display_name="Bluesky",
        auth_type="app_password",
        rate_limit_per_hour=50,
        rate_limit_per_day=500,
        max_post_length=300,
        supports_title=False,
        supports_url=True,
        supports_images=False,
        supports_hashtags=True,
        docs_url="https://docs.bsky.app/",
        env_keys=["BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"],
        features=["posts", "likes", "reposts", "follows", "feeds"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.handle = os.environ.get("BLUESKY_HANDLE", "")
        self.app_password = os.environ.get("BLUESKY_APP_PASSWORD", "")
        self.client = None

    def authenticate(self) -> bool:
        """Authenticate with Bluesky using app password."""
        if not self.handle or not self.app_password:
            return False

        if ATProto is None:
            logger.error("atproto not installed: pip install atproto")
            return False

        try:
            self.client = ATProto()
            self.client.login(self.handle, self.app_password)
            self.authenticated = True
            logger.info(f"Authenticated with Bluesky as {self.handle}")
            return True
        except Exception as e:
            logger.error(f"Bluesky auth failed: {e}")
            return False

    def publish(self, title: str, content: str, url: str = None, **kwargs) -> Dict:
        """Publish a post to Bluesky."""
        if not self.authenticated or not self.client:
            return {"success": False, "error": "Not authenticated"}

        if not self._check_rate_limit(kwargs.get("data_dir", "data")):
            return {"success": False, "error": "Rate limit exceeded"}

        text = content[:300]

        try:
            if url:
                # Create record with embed for URL
                record = {
                    "text": text,
                    "createdAt": self._now_iso(),
                    "embed": {
                        "$type": "app.bsky.embed.external",
                        "external": {
                            "uri": url,
                            "title": title[:100] if title else "",
                            "description": content[:200],
                        },
                    },
                }
                resp = self.client.com.atproto.repo.create_record(
                    models.ComAtprotoRepoCreateRecord.Data(
                        repo=self.client.me.did,
                        collection="app.bsky.feed.post",
                        record=record,
                    )
                )
            else:
                post_record = models.AppBskyFeedPost.Record(text=text)
                resp = self.client.send_post(text)

            post_uri = getattr(resp, "uri", "")
            post_rkey = post_uri.split("/")[-1] if post_uri else ""
            post_url = f"https://bsky.app/profile/{self.handle}/post/{post_rkey}"

            logger.info(f"Published to Bluesky: {post_url}")
            return {
                "success": True,
                "post_id": post_rkey,
                "post_url": post_url,
                "platform": "bluesky",
            }
        except Exception as e:
            logger.error(f"Bluesky publish failed: {e}")
            return {"success": False, "error": str(e), "platform": "bluesky"}

    def get_status(self) -> Dict:
        """Get Bluesky publisher status."""
        return {
            "platform": "bluesky",
            "authenticated": self.authenticated,
            "handle": self.handle,
            "app_password_set": bool(self.app_password),
            "atproto_installed": ATProto is not None,
            "rate_limit": f"{self.config.rate_limit_per_hour}/hr",
        }

    def _now_iso(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
