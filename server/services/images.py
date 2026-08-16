"""
Image Service
============
Provides article images from rotating free sources.

Sources:
- wikimedia: Wikimedia Commons search by keywords (free, no key)
- pollinations: AI text-to-image generation (free, no key)
- pexels: Pexels stock photo API (free key, optional)

Rotation: providers are cycled round-robin per run, stored in a state file.
"""

import json
import os
import re
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional

from server.services.storage import read_json, atomic_write_json

logger = logging.getLogger(__name__)

# Simple stopwords for building search prompts
STOPWORDS = set("""a an the and or but if because as until while of at by for with about against between
into through during before after above below to from up down in out on off over under again further then
once here there when where why how all any both each few more most other some such no nor not only own
same so than too very s t can will just don should now is are was were be been being have has had having
new today latest""".split())

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"
PEXELS_URL = "https://api.pexels.com/v1/search"


class ImageService:
    """Fetches article images from rotating free sources."""

    def __init__(self, static_dir: Optional[Path] = None, state_file: Optional[Path] = None):
        server_dir = Path(__file__).parent.parent
        self.static_dir = static_dir or (server_dir / "static")
        self.images_dir = self.static_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = state_file or (server_dir / "data" / "image_rotation_state.json")
        self.providers = ["wikimedia", "pollinations", "pexels"]
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY", "")
        self.headers = {
            "User-Agent": "AI-Agency-News/1.0 (local news automation)"
        }

    def _load_state(self) -> Dict:
        return read_json(self.state_file, default={})

    def _save_state(self, state: Dict):
        atomic_write_json(self.state_file, state)

    def _next_provider(self) -> str:
        """Round-robin through providers, skipping unavailable ones."""
        state = self._load_state()
        last = state.get("last_provider", "")
        order = self.providers
        # Start after the last used provider
        if last and last in order:
            idx = order.index(last) + 1
            order = order[idx:] + order[:idx]

        for provider in order:
            if provider == "pexels" and not self.pexels_api_key:
                continue
            return provider
        return "wikimedia"

    def _keywords_from_title(self, title: str, max_words: int = 4) -> str:
        """Extract meaningful keywords from a title."""
        words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]+", title)]
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        return " ".join(words[:max_words])

    def _build_ai_prompt(self, title: str) -> str:
        """Build a text-to-image prompt from the title."""
        base = ("photorealistic news illustration, clean editorial style, "
                "professional lighting, high detail, no text, no watermark")
        keywords = self._keywords_from_title(title, max_words=8)
        prompt = f"{keywords}, {base}" if keywords else base
        return prompt[:300]

    def _download_image(self, url: str, article_id: str) -> Optional[str]:
        """Download image and save locally. Returns relative URL path."""
        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code != 200:
                logger.warning(f"Image download failed ({resp.status_code}): {url}")
                return None

            content_type = resp.headers.get("Content-Type", "")
            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"
            elif "gif" in content_type:
                ext = "gif"

            filename = f"{article_id}.{ext}"
            filepath = self.images_dir / filename
            filepath.write_bytes(resp.content)

            return f"/static/images/{filename}"
        except Exception as e:
            logger.error(f"Image download error: {e}")
            return None

    # --- Providers ---

    def _wikimedia(self, title: str, article_id: str) -> Optional[str]:
        """Search Wikimedia Commons for a relevant image."""
        query = self._keywords_from_title(title, max_words=3) or "artificial intelligence"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 3,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 800,
            "format": "json"
        }
        try:
            resp = requests.get(WIKIMEDIA_API, params=params, headers=self.headers, timeout=30)
            data = resp.json()
            pages = (data.get("query") or {}).get("pages") or {}
            for page in pages.values():
                info = (page.get("imageinfo") or [{}])[0]
                thumb_url = info.get("thumburl") or info.get("url")
                if thumb_url:
                    return self._download_image(thumb_url, article_id)
        except Exception as e:
            logger.error(f"Wikimedia error: {e}")
        return None

    def _pollinations(self, title: str, article_id: str) -> Optional[str]:
        """Generate an AI image from the title prompt."""
        prompt = self._build_ai_prompt(title)
        url = f"{POLLINATIONS_URL}{requests.utils.quote(prompt)}?width=800&height=450&nologo=true&seed={abs(hash(title)) % 100000}"
        return self._download_image(url, article_id)

    def _pexels(self, title: str, article_id: str) -> Optional[str]:
        """Search Pexels for a stock photo."""
        if not self.pexels_api_key:
            return None
        query = self._keywords_from_title(title, max_words=3) or "artificial intelligence"
        try:
            resp = requests.get(
                PEXELS_URL,
                params={"query": query, "per_page": 3, "orientation": "landscape"},
                headers={"Authorization": self.pexels_api_key, **self.headers},
                timeout=30
            )
            data = resp.json()
            photos = data.get("photos") or []
            if photos:
                return self._download_image(photos[0]["src"]["large"], article_id)
        except Exception as e:
            logger.error(f"Pexels error: {e}")
        return None

    # --- Public API ---

    def get_image(self, title: str, article_id: str) -> Optional[str]:
        """
        Get an image for an article using the next provider in rotation.

        Args:
            title: Article title (used for search/prompt)
            article_id: Article ID (used for filename)

        Returns:
            Local image URL path or None
        """
        provider = self._next_provider()
        logger.info(f"Getting image from provider: {provider}")

        result = None
        successful_provider = None
        if provider == "wikimedia":
            result = self._wikimedia(title, article_id)
        elif provider == "pollinations":
            result = self._pollinations(title, article_id)
        elif provider == "pexels":
            result = self._pexels(title, article_id)

        if result:
            successful_provider = provider

        # Fallback chain
        if not result:
            for fallback in self.providers:
                if fallback == provider:
                    continue
                logger.info(f"Falling back to provider: {fallback}")
                if fallback == "wikimedia":
                    result = self._wikimedia(title, article_id)
                elif fallback == "pollinations":
                    result = self._pollinations(title, article_id)
                elif fallback == "pexels":
                    result = self._pexels(title, article_id)
                if result:
                    successful_provider = fallback
                    break

        # Record rotation state (use successful provider if any)
        state = self._load_state()
        state["last_provider"] = successful_provider or provider
        self._save_state(state)

        return result


# Default instance
image_service = ImageService()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_id = "test_image"
    for i in range(3):
        provider = image_service._next_provider()
        print(f"Run {i+1}: provider = {provider}")
    print("\nTesting image fetch with rotation...")
    result = image_service.get_image("AI agents working together in an office", test_id)
    print(f"Result: {result}")
