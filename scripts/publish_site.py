"""
Publish Site Script
====================
Builds the static site and pushes it to the GitHub Pages repo.

Usage:
    python3 scripts/publish_site.py           # build + push
    python3 scripts/publish_site.py --no-push # build only
    python3 scripts/publish_site.py --repo user/repo  # override repo
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_CONFIG = ROOT / "server" / "config" / "site_config.json"
BUILD_DIR = ROOT / "server" / "data" / "site_build"
REPO_DIR = ROOT / "server" / "data" / "site_repo"


def load_repo() -> str:
    config = json.loads(SITE_CONFIG.read_text())
    return config.get("repo", "yorgopetsas/ai-agency-site")


def sh(cmd: list, cwd: Path = ROOT):
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-push", action="store_true", help="Build only, do not push")
    parser.add_argument("--repo", default=None, help="Override repo (user/repo)")
    args = parser.parse_args()

    # 1. Build the static site
    sys.path.insert(0, str(ROOT))
    from server.services.site_builder import SiteBuilder
    build = SiteBuilder().build()
    print(f"Built site at {build}")

    if args.no_push:
        print("Skipping push (--no-push)")
        return 0

    repo = args.repo or load_repo()
    clone_url = f"https://github.com/{repo}.git"

    # 2. Ensure we have a local checkout of the Pages repo
    if not (REPO_DIR / ".git").exists():
        REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
        sh(["git", "clone", clone_url, str(REPO_DIR)])
    else:
        sh(["git", "-C", str(REPO_DIR), "pull", "--ff-only"])

    # 3. Sync build output into the repo (remove stale files first)
    for child in REPO_DIR.iterdir():
        if child.name != ".git":
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    shutil.copytree(build, REPO_DIR, dirs_exist_ok=True)

    # 4. Commit and push
    sh(["git", "-C", str(REPO_DIR), "add", "-A"])
    diff = subprocess.run(
        ["git", "-C", str(REPO_DIR), "diff", "--cached", "--quiet"],
        capture_output=True,
    ).returncode
    if diff != 0:
        sh(["git", "-C", str(REPO_DIR), "commit", "-m", "Update static site"])
        sh(["git", "-C", str(REPO_DIR), "push"])
        print(f"Pushed to https://github.com/{repo}")
    else:
        print("No changes to push")

    return 0


if __name__ == "__main__":
    sys.exit(main())
