"""
Rating Service
============
Scores articles for AI Agents relevance and quality.
Used to decide what gets published automatically.

Scoring (0-100):
- Relevance to AI Agents (0-60): keyword-based topic matching
- Quality signals (0-25): content depth, source weight
- Freshness (0-15): recency of the article

A score >= min_rating (config, default 60) means auto-publish.
"""

import re
from typing import Dict, List
from datetime import datetime
from dateutil import parser as date_parser

# Keywords that strongly indicate AI Agents topic
AGENT_STRONG_KEYWORDS = [
    "ai agent", "agentic", "autonomous agent", "agent framework", "agent platform",
    "agent architecture", "multi-agent", "agent workflow", "coding agent",
    "agent market", "agent economy", "agent toolkit", "agent studio",
    "agent developer", "agent network", "agent runtime", "agentic commerce",
    "agent payments", "agentic search", "computer use", "mcp", "model context protocol",
    "agent memory", "agent memory", "agent tools", "function calling", "tool use",
    "tool calling", "agentic ai", "agentic workflow", "agent engineering",
    "agents.json", "agent protocol", "a2a", "agent-to-agent", "clawhub",
    "openclaw", "agentops", "agent safety", "agent security", "agent guardrails",
    "orchestration", "agent orchestration", "agent stack", "agent builder"
]

# Keywords that suggest the article IS about agents (weaker signal)
AGENT_MEDIUM_KEYWORDS = [
    "automation", "copilot", "assistant", "chatbot", "autonomous",
    "workflow", "orchestrat", "llm tool", "agentic ai", "agent", "agents",
    "autopilot", "self-operating", "autonomous task", "deploy agent",
    "agentic platform", "agentic system", "intelligent agent", "agent swarm"
]

# Keywords that suggest it's NOT relevant (off-topic)
NEGATIVE_KEYWORDS = [
    "climate change", "election", "sports", "crypto price", "bitcoin rally",
    "gaming console", "recipe", "movie review", "music release",
    "weather", "stock tip", "celebrity", "fashion", "travel deal"
]

# High-quality sources
PREMIUM_SOURCES = [
    "agent times", "omc agent news", "latent space", "anthropic", "openai",
    "google", "deepmind", "hugging face", "mit tech review", "marktechpost",
    "simon willison", "microsoft", "nvidia", "the batch", "techcrunch"
]

# Feeds considered fully agent-focused (relevance floor)
AGENT_FOCUSED_SOURCES = ["agent times", "omc agent news", "latent space", "daemonfeed"]


class RatingService:
    """Scores articles for AI Agents relevance and quality."""

    def relevance_score(self, title: str, summary: str = "", source: str = "") -> int:
        """
        Score relevance to AI Agents (0-60).

        Args:
            title: Article title
            summary: Article summary/overview
            source: Source feed name

        Returns:
            Relevance score out of 60
        """
        text = f"{title} {summary}".lower()
        title_text = title.lower()
        score = 0

        # Strong keywords: +8 each (max 40)
        strong_hits = [kw for kw in AGENT_STRONG_KEYWORDS if kw in text]
        score += min(len(strong_hits) * 8, 40)

        # Title mentions agent(s)/agentic: very strong signal in a news feed
        if re.search(r"\bagent(ic|s)?\b", title_text):
            score += 12

        # Medium keywords: +2 each (max 8)
        medium_hits = [kw for kw in AGENT_MEDIUM_KEYWORDS if kw in text]
        score += min(len(medium_hits) * 2, 8)

        # Source is agent-focused: guaranteed minimum relevance
        if source and any(s in source.lower() for s in AGENT_FOCUSED_SOURCES):
            score = max(score, 30)

        # Negative keywords: reduce score
        neg_hits = [kw for kw in NEGATIVE_KEYWORDS if kw in text]
        score -= len(neg_hits) * 8

        return max(0, min(score, 60))

    def quality_score(self, summary: str = "", source: str = "", title: str = "") -> int:
        """
        Score quality signals (0-25).

        Args:
            summary: Article summary
            source: Source feed name
            title: Article title

        Returns:
            Quality score out of 25
        """
        score = 0
        text = f"{title} {summary}"

        # Content depth: longer summaries = more substantive
        words = len(text.split())
        if words > 200:
            score += 10
        elif words > 100:
            score += 7
        elif words > 50:
            score += 4
        else:
            score += 2

        # Source credibility
        if source:
            sl = source.lower()
            if any(s in sl for s in PREMIUM_SOURCES):
                score += 10
            elif any(s in sl for s in AGENT_FOCUSED_SOURCES):
                score += 8
            else:
                score += 4

        # Actionable signals (mentions of tools, launches, releases)
        actionable = ["launch", "release", "introduc", "announce", "ship", "deploy",
                      "open source", "available", "new", "upgrad", "partner", "fund"]
        hits = sum(1 for kw in actionable if kw in text.lower())
        score += min(hits * 2, 5)

        return min(score, 25)

    def freshness_score(self, published: str = "") -> int:
        """
        Score recency (0-15). Newer is better.

        Args:
            published: ISO timestamp or date string

        Returns:
            Freshness score out of 15
        """
        if not published:
            return 10  # Unknown date, assume recent

        try:
            pub_date = date_parser.parse(published)
            if pub_date.tzinfo is None:
                from datetime import timezone
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
        except Exception:
            return 10

        if days_old <= 1:
            return 15
        elif days_old <= 3:
            return 12
        elif days_old <= 7:
            return 9
        elif days_old <= 14:
            return 6
        else:
            return 2

    def rate(self, title: str, summary: str = "", source: str = "", published: str = "") -> Dict:
        """
        Rate an article. Returns breakdown and total score.

        Args:
            title: Article title
            summary: Article summary
            source: Source feed name
            published: Publication date

        Returns:
            Dict with relevance, quality, freshness, total, and verdict
        """
        relevance = self.relevance_score(title, summary, source)
        quality = self.quality_score(summary, source, title)
        freshness = self.freshness_score(published)

        total = relevance + quality + freshness

        return {
            "total": total,
            "relevance": relevance,
            "quality": quality,
            "freshness": freshness,
            "is_ai_agents": relevance >= 16 or (source and any(s in source.lower() for s in AGENT_FOCUSED_SOURCES)),
            "verdict": "publish" if total >= 60 else "review",
            "matches": [kw for kw in AGENT_STRONG_KEYWORDS if kw in f"{title} {summary}".lower()][:8]
        }


# Default instance
rating_service = RatingService()


if __name__ == "__main__":
    tests = [
        ("Anthropic releases Claude Agent SDK with tool calling",
         "Anthropic today released the Claude Agent SDK, a new framework for building autonomous agents with tool use, MCP support, and agent memory. The SDK includes orchestration for multi-agent workflows.",
         "Agent Times"),
        ("OpenAI launches GPT-5.6 model",
         "OpenAI has launched GPT-5.6, its latest frontier model with improved reasoning and faster inference for general use cases.",
         "TechCrunch AI"),
        ("New framework for building AI agents with MCP integration",
         "A new open source agent framework with MCP servers, agent orchestration, and workflow automation for developers building agentic applications.",
         "MarkTechPost"),
    ]

    for title, summary, source in tests:
        r = rating_service.rate(title, summary, source)
        print(f"\nTitle: {title[:50]}")
        print(f"  Total: {r['total']} (relevance={r['relevance']}, quality={r['quality']}, freshness={r['freshness']})")
        print(f"  Verdict: {r['verdict']} | is_ai_agents: {r['is_ai_agents']}")
