"""Base publisher class and registry."""
import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

PUBLISHERS: Dict[str, type] = {}


@dataclass
class PlatformConfig:
    name: str
    display_name: str
    enabled: bool = True
    requires_auth: bool = True
    auth_type: str = "api_key"
    rate_limit_per_hour: int = 60
    rate_limit_per_day: int = 500
    max_post_length: int = 2000
    supports_title: bool = False
    supports_url: bool = True
    supports_images: bool = False
    supports_hashtags: bool = True
    api_base: str = ""
    docs_url: str = ""
    env_keys: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)


def register_publisher(name: str):
    """Decorator to register a publisher."""
    def decorator(cls):
        PUBLISHERS[name] = cls
        return cls
    return decorator


def get_publisher(name: str, **kwargs) -> Optional[Any]:
    """Get a publisher instance by name."""
    cls = PUBLISHERS.get(name)
    if cls:
        return cls(**kwargs)
    return None


def list_platforms() -> List[PlatformConfig]:
    """List all available platform configurations."""
    configs = []
    for name, cls in PUBLISHERS.items():
        if hasattr(cls, "CONFIG"):
            configs.append(cls.CONFIG)
    return configs


class PlatformPublisher(ABC):
    """Base class for all platform publishers."""

    CONFIG: PlatformConfig = None

    def __init__(self, **kwargs):
        self.config = self.CONFIG
        self.authenticated = False

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform. Returns True if successful."""
        pass

    @abstractmethod
    def publish(self, title: str, content: str, url: str = None, **kwargs) -> Dict:
        """Publish a post. Returns dict with success, post_id, post_url, error."""
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """Get publisher status including rate limits."""
        pass

    def validate_env(self) -> List[str]:
        """Check if required env vars are set. Returns list of missing keys."""
        missing = []
        for key in self.config.env_keys:
            if not os.environ.get(key):
                missing.append(key)
        return missing

    def _load_credentials(self) -> Dict:
        """Load credentials from env or file."""
        creds = {}
        for key in self.config.env_keys:
            creds[key] = os.environ.get(key, "")
        return creds

    def _check_rate_limit(self, data_dir: str) -> bool:
        """Check if we're within rate limits."""
        rate_file = os.path.join(data_dir, "social_rate_limits.json")
        now = time.time()

        if os.path.exists(rate_file):
            with open(rate_file) as f:
                rates = json.load(f)
        else:
            rates = {}

        platform_rates = rates.get(self.config.name, {"hour": [], "day": []})

        hour_ago = now - 3600
        day_ago = now - 86400

        platform_rates["hour"] = [t for t in platform_rates["hour"] if t > hour_ago]
        platform_rates["day"] = [t for t in platform_rates["day"] if t > day_ago]

        if len(platform_rates["hour"]) >= self.config.rate_limit_per_hour:
            return False
        if len(platform_rates["day"]) >= self.config.rate_limit_per_day:
            return False

        platform_rates["hour"].append(now)
        platform_rates["day"].append(now)
        rates[self.config.name] = platform_rates

        with open(rate_file, "w") as f:
            json.dump(rates, f)

        return True
