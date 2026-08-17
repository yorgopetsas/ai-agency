# AGENTS.md

## Git workflow
After completing any task that changes files in this project, sync progress with:
```
git add -A && git commit && git push
```
- Commit messages should summarize what was done.
- Never commit secrets, API keys, tokens, or `.env` files (`.env` is gitignored).
- Runtime data is gitignored (`data/`, `server/data/`, `server/static/images/`, `*.db`).

## Environment & secrets
- This project uses a Python virtual environment: `.venv/` (gitignored).
- Run the server with:
  ```
  cd server && ../.venv/bin/python3 app.py
  ```
- Sensitive tokens live in the project root `.env` file (gitignored), loaded by
  `server/app.py` via python-dotenv at startup. Keys are read with `os.environ.get(...)`.
- Providers that check `.env`: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`,
  `OPENROUTER_API_KEY`, `PEXELS_API_KEY`, `TELEGRAM_BOT_TOKEN`.
- `.env.example` lists all keys (commit-safe, placeholders only).

## Project layout
- `server/` — Flask API (port 5001), routes, services, templates
- `server/services/` — storage.py (locked JSON + per-article store), llm.py
  (multi-provider router), rating.py, automation.py, research.py, writer.py,
  publisher.py, images.py
- `server/config/` — automation_config.json, llm_config.json
- `server/scheduler.py` — APScheduler 6-hour automation

## Storage model
- Articles are stored as **one JSON file per article** under `server/data/articles/`
  (write via `ArticleStore`, read via `article_store` in `app.py`).
  No single shared `articles.json` file.
- Shared JSON files (`pending.json`, `processed_urls.json`, `image_rotation_state.json`)
  are read-modify-written under an `fcntl` lock via `locked_json()` in
  `server/services/storage.py`, so multiple gunicorn workers can't corrupt them.
- `server/data/` is gitignored (runtime data, not committed).

## Public site (Phase 3: static GitHub Pages, hybrid)
- The public site is **static** and hosted on GitHub Pages at
  **`https://amanita.barcelona/news/`** — the root domain serves the
  `amanita-solutions` repo (Vite/React app); the news site lives under `/news/`.
- Deploy chain: `publish_site.py` builds + pushes to `yorgopetsas/ai-agency-site`
  (source of truth for the news build), then triggers the `amanita-solutions`
  deploy CI which clones `ai-agency-site` and copies it into `dist/news/` before
  publishing to `gh-pages`. Custom domain `amanita.barcelona` → `amanita-solutions`.
- `server/services/site_builder.py` generates the static site (index, per-article
  pages, images, `feed.xml`, `sitemap.xml`) into `server/data/site_build/` using
  relative links — self-contained, works at any nesting depth.
- Site config: `server/config/site_config.json` (`site_url`, `site_title`, `repo`, ...).
- Every `publisher.publish()` rebuilds the static site automatically.
- To deploy the latest build to GitHub Pages:
  ```
  cd ai_agency && .venv/bin/python3 scripts/publish_site.py
  ```
  (`--no-push` builds without pushing; `--repo user/repo` overrides the target.)
- Automation (RSS → research → rate → write → publish) runs locally (Ollama + hosted
  LLMs via the router); only the output site is pushed. The Flask app stays as the
  private admin/dev interface on port 5001.
