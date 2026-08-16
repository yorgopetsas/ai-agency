"""
Storage Service
==============
File-based storage with atomic, locked reads/writes.

Articles are stored as one JSON file per article in `data/articles/`
(no shared-file write races). Shared JSON files (pending, processed
URLs, rotation state) use `fcntl` file locks so concurrent worker
processes can't corrupt them.

Design:
- Per-article files: save via temp file + atomic rename.
- Shared JSON files: read-modify-write inside an exclusive `flock`,
  so two gunicorn workers can't clobber each other.
"""

import json
import os
import fcntl
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


@contextmanager
def locked_json(path: Path, default: Optional[list] = None):
    """
    Read a JSON file, yield its contents, and write back atomically
    under an exclusive file lock.

    Usage:
        with locked_json(path, default=[]) as data:
            data.append(item)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "a+")
    fcntl.flock(f, fcntl.LOCK_EX)
    try:
        f.seek(0)
        raw = f.read()
        if raw.strip():
            data = json.loads(raw)
        else:
            data = default if default is not None else []
        yield data
        f.seek(0)
        f.truncate()
        f.write(json.dumps(data, indent=2))
        f.flush()
        os.fsync(f.fileno())
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def atomic_write_json(path: Path, data) -> None:
    """Write a JSON file atomically (temp file + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)


def read_json(path: Path, default=None):
    """Read a JSON file (best-effort, returns default on failure)."""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
    return default if default is not None else []


class ArticleStore:
    """
    Stores one JSON file per article under a folder, e.g.
    `data/articles/article_20260816_181212.json`.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.articles_dir = self.data_dir / "articles"
        self.articles_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, article_id: str) -> Path:
        # Guard against path traversal from external ids
        safe_id = article_id.replace("/", "_").replace("\\", "_").replace("..", "_")
        return self.articles_dir / f"{safe_id}.json"

    def save(self, article: Dict) -> Path:
        """Save an article record to its own file (atomic)."""
        article_id = article.get("id", "")
        if not article_id:
            raise ValueError("Article record requires an 'id'")
        path = self._path_for(article_id)
        atomic_write_json(path, article)
        return path

    def delete(self, article_id: str) -> bool:
        """Delete an article file."""
        path = self._path_for(article_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def get(self, article_id: str) -> Optional[Dict]:
        """Load a single article."""
        path = self._path_for(article_id)
        if not path.exists():
            return None
        return read_json(path, default=None)

    def all(self) -> List[Dict]:
        """Load all articles, newest first (by published_at)."""
        articles = []
        try:
            for path in self.articles_dir.glob("*.json"):
                if path.name.endswith(".tmp"):
                    continue
                article = read_json(path, default=None)
                if isinstance(article, dict) and article.get("id"):
                    articles.append(article)
        except Exception as e:
            logger.error(f"Error listing articles: {e}")
        articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
        return articles

    def count(self) -> int:
        """Number of stored articles."""
        return len(list(self.articles_dir.glob("*.json")))


# Default instances
article_store = ArticleStore()


def migrate_legacy_articles(legacy_file: Path) -> int:
    """
    Migrate a legacy `articles.json` list into per-article files.

    Returns:
        -1 if the legacy file could not be read/parsed,
        otherwise the number of articles migrated (>= 0).
    """
    if not legacy_file.exists():
        return 0
    try:
        legacy = json.loads(legacy_file.read_text())
    except Exception as e:
        logger.error(f"Failed to read legacy articles file: {e}")
        return -1

    migrated = 0
    for article in legacy:
        if not isinstance(article, dict) or not article.get("id"):
            continue
        if not article_store.get(article["id"]):
            article_store.save(article)
            migrated += 1

    if migrated:
        logger.info(f"Migrated {migrated} articles to per-file storage")
    return migrated
