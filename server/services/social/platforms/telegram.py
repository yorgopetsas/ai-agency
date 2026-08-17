"""Telegram publisher - messaging platform."""
import os
import logging
import requests
from typing import Dict
from .base import PlatformPublisher, PlatformConfig, register_publisher

logger = logging.getLogger(__name__)


@register_publisher("telegram")
class TelegramPublisher(PlatformPublisher):
    CONFIG = PlatformConfig(
        name="telegram",
        display_name="Telegram",
        auth_type="bot_token",
        rate_limit_per_hour=30,
        rate_limit_per_day=500,
        max_post_length=4096,
        supports_title=True,
        supports_url=True,
        supports_images=True,
        supports_hashtags=True,
        docs_url="https://core.telegram.org/bots/api",
        env_keys=["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"],
        features=["messages", "photos", "inline_keyboards", "channels"],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"

    def authenticate(self) -> bool:
        """Verify bot token is valid."""
        if not self.bot_token:
            return False
        try:
            resp = requests.get(f"{self.api_base}/getMe")
            if resp.status_code == 200:
                data = resp.json()
                self.authenticated = data.get("ok", False)
                return self.authenticated
            return False
        except Exception as e:
            logger.error(f"Telegram auth failed: {e}")
            return False

    def publish(self, title: str, content: str, url: str = None, chat_id: str = None, **kwargs) -> Dict:
        """Publish a message to Telegram."""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}

        if not self._check_rate_limit(kwargs.get("data_dir", "data")):
            return {"success": False, "error": "Rate limit exceeded"}

        target_chat = chat_id or self.chat_id
        if not target_chat:
            return {"success": False, "error": "No chat_id specified"}

        text = content[:4096]
        if title:
            text = f"**{title}**\n\n{text}"

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }

        try:
            resp = requests.post(f"{self.api_base}/sendMessage", json=payload)
            resp.raise_for_status()
            data = resp.json()
            message_id = data.get("result", {}).get("message_id", "")
            logger.info(f"Published to Telegram: chat={target_chat}, msg={message_id}")
            return {
                "success": True,
                "post_id": str(message_id),
                "post_url": f"https://t.me/{target_chat}/{message_id}" if str(target_chat).startswith("@") else "",
                "platform": "telegram",
            }
        except Exception as e:
            logger.error(f"Telegram publish failed: {e}")
            return {"success": False, "error": str(e), "platform": "telegram"}

    def get_status(self) -> Dict:
        """Get Telegram publisher status."""
        bot_info = None
        if self.authenticated:
            try:
                resp = requests.get(f"{self.api_base}/getMe")
                bot_info = resp.json().get("result", {})
            except:
                pass

        return {
            "platform": "telegram",
            "authenticated": self.authenticated,
            "bot_token_set": bool(self.bot_token),
            "chat_id_set": bool(self.chat_id),
            "bot_username": bot_info.get("username", "") if bot_info else "",
            "rate_limit": f"{self.config.rate_limit_per_hour}/hr",
        }

    def send_to_chat(self, text: str, chat_id: str = None, parse_mode: str = "Markdown") -> Dict:
        """Send a simple text message."""
        target = chat_id or self.chat_id
        payload = {
            "chat_id": target,
            "text": text[:4096],
            "parse_mode": parse_mode,
        }
        try:
            resp = requests.post(f"{self.api_base}/sendMessage", json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def send_photo(self, photo_path: str, caption: str = "", chat_id: str = None) -> Dict:
        """Send a photo with optional caption."""
        target = chat_id or self.chat_id
        try:
            with open(photo_path, "rb") as f:
                resp = requests.post(
                    f"{self.api_base}/sendPhoto",
                    data={"chat_id": target, "caption": caption[:1024]},
                    files={"photo": f},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            return {"error": str(e)}
