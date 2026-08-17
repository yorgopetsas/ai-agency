"""Content generator - rewrites articles for different platforms."""
import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

PLATFORM_LIMITS = {
    "moltbook": {"title": 300, "content": 40000},
    "bluesky": {"content": 300},
    "mastodon": {"content": 500},
    "telegram": {"content": 4096},
    "reddit": {"title": 300, "content": 40000},
    "linkedin": {"content": 3000},
    "threads": {"content": 500},
    "twitter": {"content": 280},
}

PLATFORM_HASHTAGS = {
    "moltbook": [],
    "bluesky": ["AI", "AIAgents"],
    "mastodon": ["AI", "AIAgents", "OpenSource"],
    "telegram": [],
    "reddit": [],
    "linkedin": ["ArtificialIntelligence", "AIAgents", "TechNews"],
    "threads": ["AI", "AIAgents", "TechNews"],
    "twitter": ["AI", "AIAgents"],
}

PLATFORM_TONE = {
    "moltbook": "casual_technical",
    "bluesky": "casual_concise",
    "mastodon": "casual_detailed",
    "telegram": "informative",
    "reddit": "conversational_expert",
    "linkedin": "professional",
    "threads": "casual_trendy",
    "twitter": "punchy_direct",
}


@dataclass
class PlatformPost:
    platform: str
    title: str
    content: str
    url: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    tone: str = "neutral"
    char_count: int = 0
    over_limit: bool = False


@dataclass
class ContentPlan:
    article_id: str
    article_title: str
    article_summary: str
    article_url: str
    platforms: List[str]
    posts: Dict[str, PlatformPost] = field(default_factory=dict)
    created_at: str = ""
    status: str = "draft"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class ContentGenerator:
    """Generates platform-specific social media content from articles."""

    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.limits = PLATFORM_LIMITS

    def generate_plan(self, article: Dict, platforms: List[str] = None) -> ContentPlan:
        """Create a content plan for an article across platforms."""
        if platforms is None:
            platforms = list(PLATFORM_LIMITS.keys())

        plan = ContentPlan(
            article_id=article.get("id", ""),
            article_title=article.get("title", ""),
            article_summary=article.get("summary", article.get("description", "")),
            article_url=article.get("url", article.get("source_url", "")),
            platforms=platforms,
        )

        for platform in platforms:
            post = self._generate_post(platform, article)
            plan.posts[platform] = post

        return plan

    def _generate_post(self, platform: str, article: Dict) -> PlatformPost:
        """Generate a post for a specific platform."""
        title = article.get("title", "")
        summary = article.get("summary", article.get("description", ""))
        url = article.get("url", article.get("source_url", ""))
        source = article.get("source", "")
        topics = article.get("topics", [])
        rating = article.get("rating", 0)

        tone = PLATFORM_TONE.get(platform, "neutral")
        limits = self.limits.get(platform, {"content": 2000})
        max_content = limits.get("content", 2000)
        max_title = limits.get("title", 300)

        hashtags = PLATFORM_HASHTAGS.get(platform, [])
        if topics:
            for topic in topics[:3]:
                tag = topic.replace(" ", "").replace("-", "")
                if tag and tag not in hashtags:
                    hashtags.append(tag)

        if self.llm:
            content = self._llm_rewrite(platform, title, summary, tone, max_content)
        else:
            content = self._template_rewrite(platform, title, summary, url, hashtags)

        if len(content) > max_content:
            content = content[:max_content - 3] + "..."

        truncated_title = title[:max_title] if title else ""

        post = PlatformPost(
            platform=platform,
            title=truncated_title,
            content=content,
            url=url,
            hashtags=hashtags,
            tone=tone,
            char_count=len(content),
            over_limit=len(content) > max_content,
        )

        return post

    def _template_rewrite(self, platform: str, title: str, summary: str, url: str, hashtags: List[str]) -> str:
        """Template-based content generation when no LLM is available."""
        hashtag_str = " ".join(f"#{t}" for t in hashtags[:5]) if hashtags else ""

        templates = {
            "moltbook": f"## {title}\n\n{summary}\n\n{url}\n\n{hashtag_str}".strip(),
            "bluesky": f"{title}\n\n{summary[:200]}\n\n{url}\n\n{hashtag_str}".strip(),
            "mastodon": f"{title}\n\n{summary[:400]}\n\n{url}\n\n{hashtag_str}".strip(),
            "telegram": f"📰 **{title}**\n\n{summary}\n\n🔗 {url}\n\n{hashtag_str}".strip(),
            "reddit": f"{title}\n\n{summary}\n\nSource: {url}".strip(),
            "linkedin": f"{title}\n\n{summary}\n\n{url}\n\n{hashtag_str}".strip(),
            "threads": f"{title} 🤖\n\n{summary[:200]}\n\n{url}\n\n{hashtag_str}".strip(),
            "twitter": f"{title} 🤖\n\n{summary[:200]}\n\n{url}\n\n{hashtag_str}".strip(),
        }

        return templates.get(platform, f"{title}\n\n{summary}\n\n{url}")

    def _llm_rewrite(self, platform: str, title: str, summary: str, tone: str, max_chars: int) -> str:
        """Use LLM to rewrite content for the platform."""
        try:
            prompt = f"""Rewrite this AI news article for {platform}.
Tone: {tone}
Max length: {max_chars} characters
Include the article URL at the end.

Title: {title}
Summary: {summary}

Write only the post content, no explanation:"""

            response = self.llm.complete(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_chars,
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"LLM rewrite failed for {platform}: {e}")
            return self._template_rewrite(platform, title, summary, "", PLATFORM_HASHTAGS.get(platform, []))

    def save_plan(self, plan: ContentPlan, data_dir: str):
        """Save a content plan to disk."""
        plans_dir = os.path.join(data_dir, "social_plans")
        os.makedirs(plans_dir, exist_ok=True)

        plan_file = os.path.join(plans_dir, f"{plan.article_id}.json")
        with open(plan_file, "w") as f:
            json.dump(asdict(plan), f, indent=2)

        logger.info(f"Saved content plan: {plan_file}")

    def load_plan(self, article_id: str, data_dir: str) -> Optional[ContentPlan]:
        """Load a content plan from disk."""
        plan_file = os.path.join(data_dir, "social_plans", f"{article_id}.json")
        if not os.path.exists(plan_file):
            return None

        with open(plan_file) as f:
            data = json.load(f)

        posts = {}
        for platform, post_data in data.get("posts", {}).items():
            posts[platform] = PlatformPost(**post_data)

        return ContentPlan(
            article_id=data["article_id"],
            article_title=data["article_title"],
            article_summary=data["article_summary"],
            article_url=data["article_url"],
            platforms=data["platforms"],
            posts=posts,
            created_at=data.get("created_at", ""),
            status=data.get("status", "draft"),
        )

    def update_plan_status(self, article_id: str, status: str, data_dir: str):
        """Update a plan's status."""
        plan = self.load_plan(article_id, data_dir)
        if plan:
            plan.status = status
            self.save_plan(plan, data_dir)
