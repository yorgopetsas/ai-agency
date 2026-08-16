"""
Static Site Builder
====================
Generates a fully static public site (GitHub Pages friendly) from the
published articles in the ArticleStore.

Output structure:
    out_dir/
        index.html
        style.css
        feed.xml
        sitemap.xml
        images/                  (copied from server/static/images)
        article/<article_id>/index.html

All links are relative so the site works hosted at a repo sub-path
(yorgopetsas.github.io/ai-agency-site/) or at a custom domain root.
"""

import html
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from xml.sax.saxutils import escape as xml_escape

from server.services.storage import ArticleStore

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "site_config.json"


def _clean_text(text: str) -> str:
    """Strip light markdown (bold/emphasis markers) from LLM text."""
    if not text:
        return text
    text = text.replace("**", "")
    text = re.sub(r"(?<!\w)\*(?!\*)([^*]+)(?<!\*)\*(?!\w)", r"\1", text)
    return text

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2.5rem 1rem; text-align: center; }
header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
header p { opacity: 0.92; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.5rem; }
.news-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); display: flex; flex-direction: column; }
.news-card .article-img { width: 100%; height: 200px; object-fit: cover; }
.news-card .card-body { padding: 1.5rem; display: flex; flex-direction: column; flex: 1; }
.news-card h2 { font-size: 1.15rem; margin-bottom: 0.6rem; }
.news-card h2 a { color: #333; text-decoration: none; }
.news-card h2 a:hover { color: #667eea; }
.news-card .overview { color: #667; font-style: italic; margin-bottom: 0.9rem; font-size: 0.95rem; }
.news-card .content p { color: #444; font-size: 0.95rem; margin-bottom: 0.6rem; }
.news-card .meta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.85rem; color: #999; }
.news-card .meta a { color: #667eea; text-decoration: none; }
.news-card .meta a:hover { text-decoration: underline; }
.badge { display: inline-block; background: #eef0ff; color: #667eea; border: 1px solid #dde0ff; border-radius: 999px; padding: 0.15rem 0.6rem; font-size: 0.78rem; }
.badge.rating { background: #eafaf1; color: #1a9e5c; border-color: #c9f0dc; }
.article { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.08); max-width: 800px; margin: 0 auto; }
.article img { width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 1.5rem; }
.article h1 { font-size: 1.7rem; margin-bottom: 0.75rem; line-height: 1.3; }
.article .overview { color: #667; font-style: italic; font-size: 1.05rem; margin-bottom: 1.5rem; }
.article .content p { margin-bottom: 1rem; font-size: 1.02rem; }
.article .actions { display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; padding-top: 1.2rem; border-top: 1px solid #eee; }
.btn { display: inline-block; background: #667eea; color: white; padding: 0.55rem 1.2rem; border-radius: 8px; text-decoration: none; font-size: 0.92rem; }
.btn.secondary { background: #eee; color: #555; }
.btn:hover { opacity: 0.9; }
.back { text-align: center; margin-top: 2rem; }
footer { text-align: center; padding: 2rem; color: #999; font-size: 0.9rem; }
.meta-line { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; color: #888; font-size: 0.88rem; margin-bottom: 1rem; }
@media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
"""


class SiteBuilder:
    """Builds a static public site from stored articles."""

    def __init__(self, out_dir: Optional[Path] = None, images_dir: Optional[Path] = None,
                 data_dir: Optional[Path] = None):
        self.store = ArticleStore(data_dir=data_dir)
        server_dir = Path(__file__).parent.parent
        self.images_dir = images_dir or (server_dir / "static" / "images")
        self.out_dir = out_dir or (server_dir / "data" / "site_build")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {
            "site_url": "https://yorgopetsas.github.io/ai-agency-site/",
            "site_title": "AI Agents News",
            "site_tagline": "Daily AI Agents news, researched and written by our multi-agent system",
            "max_cards": 12,
            "feed_entries": 10
        }

    # --- helpers ---

    def _local_image_name(self, image_url: str) -> Optional[str]:
        """If image_url points at a local /static/images/ file, return the filename."""
        if not image_url:
            return None
        marker = "/static/images/"
        if marker not in image_url:
            return None
        return image_url.split(marker)[-1].split("?")[0]

    def _rel_image(self, image_url: str, depth: int) -> str:
        """Rewrite a stored image URL to a site-relative path."""
        name = self._local_image_name(image_url)
        if name is None:
            return image_url
        prefix = "../" * depth
        return f"{prefix}images/{name}"

    @staticmethod
    def _is_local_image(image: str) -> bool:
        """True if the rewritten path points at a bundled site image."""
        return image.startswith(("../", "images/"))

    def _footer(self) -> str:
        return (
            f"<footer>Powered by AI Agency Multi-Agent System"
            f" | Version 3.0</footer>"
        )

    def _page_head(self, title: str, css_href: str, description: str = "") -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description or self.config.get('site_description', ''))}">
    <link rel="alternate" type="application/rss+xml" title="{html.escape(self.config.get('site_title', 'AI Agents News'))} RSS" href="{css_href.rpartition('/')[0]}/feed.xml">
    <link rel="stylesheet" href="{css_href}">
</head>
<body>
"""

    # --- page builders ---

    def _build_index(self, articles: List[Dict]) -> str:
        max_cards = self.config.get("max_cards", 12)
        cards = []
        for article in articles[:max_cards]:
            cards.append(self._card_html(article, depth=0))

        grid = "\n".join(cards) if cards else f"""<div class="news-card">
    <div class="card-body">
        <h2>Welcome to {html.escape(self.config.get('site_title', 'AI Agents News'))}</h2>
        <p class="overview">Your daily AI news will appear here.</p>
        <div class="content"><p>Articles are published automatically by the multi-agent system.</p></div>
    </div>
</div>"""

        return (
            self._page_head(
                self.config.get("site_title", "AI Agents News"),
                "style.css",
                self.config.get("site_description", "")
            )
            + f"""<header>
    <h1>🤖 {html.escape(self.config.get('site_title', 'AI Agents News'))}</h1>
    <p>{html.escape(self.config.get('site_tagline', ''))}</p>
</header>
<div class="container">
    <div class="news-grid">
{grid}
    </div>
</div>
"""
            + self._footer()
            + "</body>\n</html>\n"
        )

    def _card_html(self, article: Dict, depth: int) -> str:
        prefix = "../" * depth
        article_href = f"{prefix}article/{html.escape(article['id'])}/"
        image = self._rel_image(article.get("image_url", ""), depth)
        image_html = (
            f'<a href="{article_href}"><img class="article-img" src="{html.escape(image)}" '
            f'alt="{html.escape(_clean_text(article.get("headline", "Article")))}" loading="lazy"></a>'
            if self._is_local_image(image) else ""
        )

        paragraphs_html = "".join(
            f"<p>{html.escape(_clean_text(p))}</p>" for p in article.get("paragraphs", [])[:3]
        )
        rating = article.get("rating") or {}
        rating_total = rating.get("total") if isinstance(rating, dict) else None
        rating_html = (
            f'<span class="badge rating">Score {html.escape(str(rating_total))}</span>'
            if rating_total is not None else ""
        )
        provider_html = (
            f'<span class="badge">✍️ {html.escape(article.get("provider", ""))}</span>'
            if article.get("provider") else ""
        )

        return f"""<article class="news-card">
    {image_html}
    <div class="card-body">
        <h2><a href="{article_href}">{html.escape(_clean_text(article.get('headline', 'Untitled')))}</a></h2>
        <p class="overview">{html.escape(_clean_text(article.get('overview', '')))}</p>
        <div class="content">
            {paragraphs_html}
        </div>
        <div class="meta">
            <span><a href="{html.escape(article.get('source_url', '#'))}" target="_blank">📰 Source</a></span>
            <span>{html.escape(article.get('date_formatted', ''))}</span>
        </div>
        <div class="meta">
            <span>{provider_html}</span>
            <span>{rating_html}</span>
        </div>
    </div>
</article>"""

    def _build_article_page(self, article: Dict) -> str:
        article_id = article["id"]
        image = self._rel_image(article.get("image_url", ""), 2)
        image_html = (
            f'<img src="{html.escape(image)}" alt="{html.escape(_clean_text(article.get("headline", "Article")))}">'
            if self._is_local_image(image) else ""
        )
        paragraphs_html = "".join(
            f"<p>{html.escape(_clean_text(p))}</p>" for p in article.get("paragraphs", [])
        )

        rating = article.get("rating") or {}
        rating_total = rating.get("total") if isinstance(rating, dict) else None
        badges = []
        if article.get("provider"):
            badges.append(f'<span class="badge">✍️ {html.escape(article["provider"])}</span>')
        if rating_total is not None:
            badges.append(f'<span class="badge rating">Score {html.escape(str(rating_total))}</span>')
        badges_html = "\n        ".join(badges)

        return (
            self._page_head(
                f"{_clean_text(article.get('headline', 'Article'))} — {self.config.get('site_title', 'AI Agents News')}",
                "../../style.css",
                _clean_text(article.get("overview", ""))
            )
            + f"""<header>
    <h1>🤖 {html.escape(self.config.get('site_title', 'AI Agents News'))}</h1>
</header>
<div class="container">
    <div class="article">
        {image_html}
        <h1>{html.escape(_clean_text(article.get('headline', 'Untitled')))}</h1>
        <p class="overview">{html.escape(_clean_text(article.get('overview', '')))}</p>
        <div class="meta-line">
            <span>{html.escape(article.get('date_formatted', ''))}</span>
            {badges_html}
        </div>
        <div class="content">
            {paragraphs_html}
        </div>
        <div class="actions">
            <a class="btn" href="{html.escape(article.get('source_url', '#'))}" target="_blank">📰 View Original Source</a>
        </div>
    </div>
    <div class="back">
        <a class="btn secondary" href="../../">← Back to News</a>
    </div>
</div>
"""
            + self._footer()
            + "</body>\n</html>\n"
        )

    def _build_feed(self, articles: List[Dict]) -> str:
        site_url = self.config.get("site_url", "").rstrip("/")
        title = self.config.get("site_title", "AI Agents News")
        feed_entries = self.config.get("feed_entries", 10)

        items = []
        for article in articles[:feed_entries]:
            link = f"{site_url}/article/{article['id']}/"
            pub_date = article.get("published_at", "")
            items.append(f"""<item>
    <title>{xml_escape(_clean_text(article.get('headline', '')))}</title>
    <link>{xml_escape(link)}</link>
    <guid>{xml_escape(link)}</guid>
    <pubDate>{xml_escape(article.get('published_at', ''))}</pubDate>
    <description>{xml_escape(_clean_text(article.get('overview', '')))}</description>
</item>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>{xml_escape(title)}</title>
    <link>{xml_escape(site_url)}</link>
    <description>{xml_escape(self.config.get('site_description', ''))}</description>
    <lastBuildDate>{xml_escape(articles[0].get('published_at', '') if articles else '')}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""

    def _build_sitemap(self, articles: List[Dict]) -> str:
        site_url = self.config.get("site_url", "").rstrip("/")
        urls = [f"<url><loc>{xml_escape(site_url)}/</loc></url>"]
        for article in articles:
            urls.append(
                f"<url><loc>{xml_escape(site_url + '/article/' + article['id'] + '/')}</loc></url>"
            )
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""

    # --- main build ---

    def _site_hostname(self) -> str:
        """Bare hostname from site_url (for the Pages CNAME file)."""
        from urllib.parse import urlsplit
        try:
            return urlsplit(self.config.get("site_url", "")).hostname or ""
        except Exception:
            return ""

    def build(self) -> Path:
        """Generate the full static site into out_dir and return it."""
        articles = self.store.all()
        logger.info(f"Building static site: {len(articles)} articles -> {self.out_dir}")

        article_dir = self.out_dir / "article"
        images_out = self.out_dir / "images"

        # Clean the build dir (but not the images copy source!)
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir)
        self.out_dir.mkdir(parents=True)
        article_dir.mkdir(parents=True)
        images_out.mkdir(parents=True)

        # Copy local article images
        copied = 0
        for article in articles:
            name = self._local_image_name(article.get("image_url", ""))
            if not name:
                continue
            src = self.images_dir / name
            if src.exists():
                shutil.copy2(src, images_out / name)
                copied += 1
        logger.info(f"Copied {copied} images")

        # Pages
        (self.out_dir / "style.css").write_text(CSS)
        (self.out_dir / "index.html").write_text(self._build_index(articles))
        (self.out_dir / "feed.xml").write_text(self._build_feed(articles))
        (self.out_dir / "sitemap.xml").write_text(self._build_sitemap(articles))

        # CNAME file keeps the GitHub Pages custom domain across redeploys
        # (the publish script syncs the whole build dir into the repo).
        cname_host = self._site_hostname()
        if cname_host:
            (self.out_dir / "CNAME").write_text(cname_host + "\n")

        for article in articles:
            page_dir = article_dir / article["id"]
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(self._build_article_page(article))

        logger.info(f"Static site built at {self.out_dir}")
        return self.out_dir


# Default instance
site_builder = SiteBuilder()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out = site_builder.build()
    print(f"Built site at {out}")
    for path in sorted(out.rglob("index.html"))[:12]:
        print(f"  {path.relative_to(out)}")
