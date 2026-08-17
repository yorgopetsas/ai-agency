"""Mastodon publisher - federated social network."""
import os
import logging
import requests
from typing import Dict
from .base import PlatformPublisher, PlatformConfig, register_publisher

logger = logging.getLogger(__name__)


@register_publisher("mastodon")
class MastodonPublisher(PlatformPublisher):
    CONFIG = PlatformConfig(
        name="mastodon",
        display_name="Mastodon",
        auth_type="token",
        rate_limit_per_hour=30,
        rate_limit_per_day=300,
        max_post_length=500,
        supports_title=False,
        supports_url=True,
        supports_images=True,
        supports_hashtags=True,
        docs_url="https://docs.joinmastodon.org/api/",
        env_keys=["MASTODON_ACCESS_TOKEN", "MASTODON_API_BASE"],
        features=["posts", "favourites", "reblogs", "follows", "media"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.access_token = os.environ.get("MASTODON_ACCESS_TOKEN", "")
        self.api_base = os.environ.get("MASTODON_API_BASE", "https://mastodon.social")
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
            })
            self.authenticated = True

    def authenticate(self) -> bool:
        """Verify access token is valid."""
        if not self.access_token:
            return False
        try:
            resp = self.session.get(f"{self.api_base}/api/v1/accounts/verify_credentials")
            if resp.status_code == 200:
                self.authenticated = True
                return True
            return False
        except Exception as e:
            logger.error(f"Mastodon auth failed: {e}")
            return False

    def publish(self, title: str, content: str, url: str = None, **kwargs) -> Dict:
        """Publish a post to Mastodon."""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}

        if not self._check_rate_limit(kwargs.get("data_dir", "data")):
            return {"success": False, "error": "Rate limit exceeded"}

        text = content[:500]

        payload = {"status": text}
        if url:
            payload["visibility"] = "public"

        try:
            resp = self.session.post(f"{self.api_base}/api/v1/statuses", json=payload)
            resp.raise_for_status()
            data = resp.json()
            post_id = data.get("id", "")
            post_url = data.get("url", f"{self.api_base}/@{self._get_username()}/{post_id}")

            logger.info(f"Published to Mastodon: {post_url}")
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "platform": "mastodon",
            }
        except Exception as e:
            logger.error(f"Mastodon publish failed: {e}")
            return {"success": False, "error": str(e), "platform": "mastodon"}

    def get_status(self) -> Dict:
        """Get Mastodon publisher status."""
        return {
            "platform": "mastodon",
            "authenticated": self.authenticated,
            "api_base": self.api_base,
            "token_set": bool(self.access_token),
            "rate_limit": f"{self.config.rate_limit_per_hour}/hr",
        }

    def _get_username(self) -> str:
        """Get current username."""
        try:
            resp = self.session.get(f"{self.api_base}/api/v1/accounts/verify_credentials")
            return resp.json().get("username", "unknown")
        except:
            return "unknown"

    def upload_media(self, file_path: str) -> Dict:
        """Upload media to Mastodon."""
        try:
            with open(file_path, "rb") as f:
                resp = self.session.post(
                    f"{self.api_base}/api/v2/media",
                    files={"file": f},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Mastodon media upload failed: {e}")
            return {"error": str(e)}
