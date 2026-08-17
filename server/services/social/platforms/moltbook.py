"""Moltbook publisher - AI agent social network."""
import os
import json
import logging
import requests
from typing import Dict, Optional
from .base import PlatformPublisher, PlatformConfig, register_publisher

logger = logging.getLogger(__name__)

API_BASE = "https://www.moltbook.com/api/v1"


@register_publisher("moltbook")
class MoltbookPublisher(PlatformPublisher):
    CONFIG = PlatformConfig(
        name="moltbook",
        display_name="Moltbook",
        auth_type="api_key",
        rate_limit_per_hour=30,
        rate_limit_per_day=200,
        max_post_length=40000,
        supports_title=True,
        supports_url=True,
        supports_hashtags=False,
        api_base=API_BASE,
        docs_url="https://www.moltbook.com/skill.md",
        env_keys=["MOLTBOOK_API_KEY"],
        features=["posts", "comments", "upvotes", "submolts", "feed", "search"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = os.environ.get("MOLTBOOK_API_KEY", "")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })
            self.authenticated = True

    def register_agent(self, name: str, description: str) -> Dict:
        """Register a new agent on Moltbook. Returns API key."""
        try:
            resp = requests.post(
                f"{API_BASE}/agents/register",
                json={"name": name, "description": description},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Registered on Moltbook: {data}")
            return data
        except Exception as e:
            logger.error(f"Moltbook registration failed: {e}")
            return {"error": str(e)}

    def authenticate(self) -> bool:
        """Verify API key is valid."""
        if not self.api_key:
            return False
        try:
            resp = self.session.get(f"{API_BASE}/agents/me")
            if resp.status_code == 200:
                self.authenticated = True
                return True
            return False
        except Exception as e:
            logger.error(f"Moltbook auth failed: {e}")
            return False

    def publish(self, title: str, content: str, url: str = None, submolt: str = "general", **kwargs) -> Dict:
        """Publish a post to Moltbook."""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}

        if not self._check_rate_limit(kwargs.get("data_dir", "data")):
            return {"success": False, "error": "Rate limit exceeded"}

        payload = {
            "submolt_name": submolt,
            "title": title[:300],
            "content": content[:40000],
        }
        if url:
            payload["url"] = url
            payload["type"] = "link"
        else:
            payload["type"] = "text"

        try:
            resp = self.session.post(f"{API_BASE}/posts", json=payload)
            resp.raise_for_status()
            data = resp.json()
            post_id = data.get("post", {}).get("id", "")
            logger.info(f"Published to Moltbook: {post_id}")
            return {
                "success": True,
                "post_id": post_id,
                "post_url": f"https://www.moltbook.com/post/{post_id}",
                "platform": "moltbook",
                "verification_required": "verification" in data,
            }
        except Exception as e:
            logger.error(f"Moltbook publish failed: {e}")
            return {"success": False, "error": str(e), "platform": "moltbook"}

    def get_status(self) -> Dict:
        """Get Moltbook publisher status."""
        return {
            "platform": "moltbook",
            "authenticated": self.authenticated,
            "api_key_set": bool(self.api_key),
            "rate_limit": f"{self.config.rate_limit_per_hour}/hr",
        }

    def list_submolts(self) -> list:
        """List available submolts."""
        try:
            resp = self.session.get(f"{API_BASE}/submolts")
            resp.raise_for_status()
            return resp.json().get("submolts", [])
        except Exception as e:
            logger.error(f"Failed to list submolts: {e}")
            return []
