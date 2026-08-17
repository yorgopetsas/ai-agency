"""
Flask API Server - Daily News Workflow
===================================
Port: 5001
Run: python3 -m server.app
"""

from flask import Flask, render_template, jsonify, request, abort
from pathlib import Path
import os
import json
import sys

# Load secrets from .env in the project root (before importing services
# that read env vars at import time). .env is gitignored.
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import routes (using relative imports)
from server.routes.news import news_bp
from server.routes.workflow import workflow_bp
from server.routes.admin import admin_bp
from server.routes.social import social_bp
from server.routes.auth import auth_bp
from server.routes.reseller import reseller_bp
from server.routes.client import client_bp
from server.routes.branding import branding_bp
from server.routes.billing import billing_bp
from server.services.automation import automation_service
from server.scheduler import init_scheduler
from auth.middleware import init_auth

# Create Flask app
app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static")
)

# Configuration
app.config['SERVER_DIR'] = Path(__file__).parent
app.config['DATA_DIR'] = app.config['SERVER_DIR'] / "data"
app.config['WEBSITE_DIR'] = Path(__file__).parent.parent / "accounts" / "internal" / "website"

# Ensure data directories exist
app.config['DATA_DIR'].mkdir(exist_ok=True)
app.config['WEBSITE_DIR'].mkdir(exist_ok=True)

# Initialize data files
articles_file = app.config['DATA_DIR'] / "articles.json"
pending_file = app.config['DATA_DIR'] / "pending.json"

if not pending_file.exists():
    pending_file.write_text("[]")

# Migrate legacy articles.json (if present) into per-article files,
# then archive the legacy single-file list.
from server.services.storage import migrate_legacy_articles, ArticleStore
migrated = migrate_legacy_articles(articles_file)
if migrated >= 0 and articles_file.exists():
    try:
        articles_file.unlink()
    except OSError:
        pass
article_store = ArticleStore(data_dir=app.config['DATA_DIR'])

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(reseller_bp)
app.register_blueprint(client_bp)
app.register_blueprint(branding_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(news_bp, url_prefix='/api')
app.register_blueprint(workflow_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(social_bp, url_prefix='/api')

# Initialize auth middleware
init_auth(app)


# ============================================================
# Automation Routes
# ============================================================

@app.route('/api/automation/status', methods=['GET'])
def automation_status():
    """Get automation status."""
    return jsonify(automation_service.get_status())


@app.route('/api/automation/run', methods=['POST'])
def automation_run():
    """Manually trigger the automation run."""
    result = automation_service.run_once()
    if result.get('success'):
        return jsonify(result)
    return jsonify(result), 500


@app.route('/api/llm/status', methods=['GET'])
def llm_status():
    """Get LLM provider status."""
    from server.services.llm import llm_client
    return jsonify({"providers": llm_client.get_status()})


# Start scheduler (only in the reloader child process under debug, or once in prod)
# Prevents double scheduler instances from Flask's file-watcher reloader.
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    init_scheduler()


# ============================================================
# Public Routes (Website Pages)
# ============================================================

@app.route('/')
def index():
    """Main news page"""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Admin panel for adding news"""
    return render_template('admin.html')


@app.route('/article/<article_id>')
def article(article_id):
    """Single article view"""
    article_data = article_store.get(article_id)
    if not article_data:
        abort(404, description="Article not found")
    return render_template('article.html', **article_data)


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "server": "daily-news-api",
        "version": "1.0.0"
    })


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("Daily News API Server")
    print("=" * 50)
    print(f"Port: 5001")
    print(f"Website: http://localhost:5001")
    print(f"Admin: http://localhost:5001/admin")
    print(f"API: http://localhost:5001/api/news")
    print("=" * 50)

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=True
    )