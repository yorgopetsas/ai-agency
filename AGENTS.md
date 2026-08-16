# AGENTS.md

## Git workflow
After completing any task that changes files in this project, sync progress with:
```
git add -A && git commit && git push
```
- Commit messages should summarize what was done.
- Never commit secrets, API keys, tokens, or `.env` files.
- Runtime data is gitignored (`data/`, `server/data/`, `server/static/images/`, `*.db`).

## Project layout
- `server/` — Flask API (port 5001), routes, services, templates
- `server/services/` — llm.py (multi-provider router), rating.py, automation.py,
  research.py, writer.py, publisher.py, images.py
- `server/config/` — automation_config.json, llm_config.json
- `server/scheduler.py` — APScheduler 6-hour automation
