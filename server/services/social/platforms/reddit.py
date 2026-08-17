"""Reddit publisher - link aggregation platform."""
import os
import logging
import requests
import time
from typing import Dict
from .base import PlatformPublisher, PlatformConfig, register_publisher

logger = logging.getLogger(__name__)

REDDIT_OAUTH_BASE = "https://www.reddit.com"
REDDIT_API_BASE = "https://oauth.reddit.com"


@register_publisher("reddit")
class RedditPublisher(PlatformPublisher):
    CONFIG = PlatformConfig(
        name="reddit",
        display_name="Reddit",
        auth_type="oauth2",
        rate_limit_per_hour=30,
        rate_limit_per_day=100,
        max_post_length=40000,
        supports_title=True,
        supports_url=True,
        supports_images=True,
        supports_hashtags=False,
        docs_url="https://www.reddit.com/dev/api",
        env_keys=["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT", "REDDIT_USERNAME", "REDDIT_PASSWORD"],
        features=["posts", "comments", "votes", "subreddits"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        self.user_agent = os.environ.get("REDDIT_USER_AGENT", "AIAgencyBot/1.0")
        self.username = os.environ.get("REDDIT_USERNAME", "")
        self.password = os.environ.get("REDDIT_PASSWORD", "")
        self.access_token = ""
        self.token_expires = 0
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with Reddit using script app credentials."""
        if not self.client_id or not self.client_secret or not self.username or not self.password:
            return False

        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            }
            headers = {"User-Agent": self.user_agent}

            resp = requests.post(
                f"{REDDIT_OAUTH_BASE}/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers,
            )
            resp.raise_for_status()
            token_data = resp.json()

            if "access_token" in token_data:
                self.access_token = token_data["access_token"]
                self.token_expires = time.time() + token_data.get("expires_in", 3600)
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": self.user_agent,
                })
                self.authenticated = True
                logger.info(f"Authenticated with Reddit as u/{self.username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Reddit auth failed: {e}")
            return False

    def _refresh_token_if_needed(self):
        """Refresh token if expired."""
        if time.time() > self.token_expires - 300:
            self.authenticate()

    def publish(self, title: str, content: str, url: str = None, subreddit: str = "artificial", **kwargs) -> Dict:
        """Publish a post to Reddit."""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}

        if not self._check_rate_limit(kwargs.get("data_dir", "data")):
            return {"success": False, "error": "Rate limit exceeded"}

        self._refresh_token_if_needed()

        if url:
            payload = {
                "sr": subreddit,
                "kind": "link",
                "title": title[:300],
                "url": url,
            }
        else:
            payload = {
                "sr": subreddit,
                "kind": "self",
                "title": title[:300],
                "text": content[:40000],
            }

        try:
            resp = self.session.post(f"{REDDIT_API_BASE}/api/submit", data=payload)
            resp.raise_for_status()
            data = resp.json()

            post_id = data.get("jquery", [[None, None, None, None]])[0][3] if "jquery" in data else ""

            post_url = f"https://reddit.com/r/{subreddit}/comments/{post_id}" if post_id else ""

            logger.info(f"Published to Reddit r/{subreddit}: {post_url}")
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url,
                "platform": "reddit",
                "subreddit": subreddit,
            }
        except Exception as e:
            logger.error(f"Reddit publish failed: {e}")
            return {"success": False, "error": str(e), "platform": "reddit"}

    def get_status(self) -> Dict:
        """Get Reddit publisher status."""
        return {
            "platform": "reddit",
            "authenticated": self.authenticated,
            "client_id_set": bool(self.client_id),
            "username": self.username if self.authenticated else "",
            "rate_limit": f"{self.config.rate_limit_per_hour}/hr",
        }

    def list_subreddits(self, query: str = "artificial") -> list:
        """Search for subreddits."""
        try:
            self._refresh_token_if_needed()
            resp = self.session.get(
                f"{REDDIT_API_BASE}/subreddits/search",
                params={"query": query, "limit": 10},
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {"name": s["data"]["display_name"], "subscribers": s["data"]["subscribers"]}
                for s in data.get("data", {}).get("children", [])
            ]
        except Exception as e:
            logger.error(f"Reddit subreddit search failed: {e}")
            return []
