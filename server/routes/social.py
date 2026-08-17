"""Social media API routes."""
from flask import Blueprint, jsonify, request
import os

social_bp = Blueprint('social', __name__)

_social_manager = None


def get_social_manager():
    """Lazy-init social media manager."""
    global _social_manager
    if _social_manager is None:
        from server.services.social.manager import SocialMediaManager
        from server.services.llm import llm_client
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        _social_manager = SocialMediaManager(data_dir=data_dir, llm_client=llm_client)
    return _social_manager


# ============================================================
# Platform Management
# ============================================================

@social_bp.route('/social/platforms', methods=['GET'])
def get_platforms():
    """Get all platform statuses."""
    manager = get_social_manager()
    return jsonify({"platforms": manager.get_platforms()})


@social_bp.route('/social/platforms/<platform>/auth', methods=['POST'])
def authenticate_platform(platform):
    """Authenticate with a platform."""
    manager = get_social_manager()
    publisher = manager.publishers.get(platform)
    if not publisher:
        return jsonify({"error": f"Unknown platform: {platform}"}), 404

    success = publisher.authenticate()
    return jsonify({
        "platform": platform,
        "authenticated": success,
        "status": publisher.get_status(),
    })


@social_bp.route('/social/platforms/<platform>/test', methods=['POST'])
def test_publish(platform):
    """Test publish to a platform."""
    manager = get_social_manager()
    publisher = manager.publishers.get(platform)
    if not publisher:
        return jsonify({"error": f"Unknown platform: {platform}"}), 404

    data = request.json or {}
    result = publisher.publish(
        title=data.get("title", "Test Post"),
        content=data.get("content", "This is a test post from AI Agency."),
        url=data.get("url", ""),
    )
    return jsonify(result)


# ============================================================
# Content Generation
# ============================================================

@social_bp.route('/social/generate', methods=['POST'])
def generate_content():
    """Generate social media content for an article."""
    manager = get_social_manager()
    data = request.json or {}

    article_id = data.get("article_id")
    if not article_id:
        return jsonify({"error": "article_id required"}), 400

    from server.services.storage import ArticleStore
    article_store = ArticleStore(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    article = article_store.get(article_id)
    if not article:
        return jsonify({"error": f"Article {article_id} not found"}), 404

    platforms = data.get("platforms")
    plan = manager.generate_content(article, platforms)

    return jsonify({
        "article_id": plan.article_id,
        "platforms": plan.platforms,
        "posts": {
            name: {
                "title": post.title,
                "content": post.content[:500] + "..." if len(post.content) > 500 else post.content,
                "char_count": post.char_count,
                "over_limit": post.over_limit,
                "hashtags": post.hashtags,
                "tone": post.tone,
            }
            for name, post in plan.posts.items()
        },
        "status": plan.status,
    })


# ============================================================
# Queue Management
# ============================================================

@social_bp.route('/social/queue', methods=['GET'])
def get_queue():
    """Get all queued posts."""
    manager = get_social_manager()
    stats = manager.get_scheduler_stats()
    pending = manager.scheduler.get_pending_posts()

    return jsonify({
        "stats": stats,
        "posts": [
            {
                "id": p.id,
                "article_id": p.article_id,
                "platform": p.platform,
                "title": p.title[:100],
                "status": p.status,
                "scheduled_for": p.scheduled_for,
                "retries": p.retries,
            }
            for p in pending
        ],
    })


@social_bp.route('/social/queue', methods=['POST'])
def add_to_queue():
    """Queue an article for publishing."""
    manager = get_social_manager()
    data = request.json or {}

    article_id = data.get("article_id")
    if not article_id:
        return jsonify({"error": "article_id required"}), 400

    platforms = data.get("platforms")
    delay_minutes = data.get("delay_minutes", 0)

    post_ids = manager.queue_article(article_id, platforms, delay_minutes)
    return jsonify({
        "article_id": article_id,
        "queued": len(post_ids),
        "post_ids": post_ids,
    })


@social_bp.route('/social/queue/<post_id>', methods=['DELETE'])
def cancel_post(post_id):
    """Cancel a scheduled post."""
    manager = get_social_manager()
    manager.cancel_scheduled(post_id)
    return jsonify({"cancelled": post_id})


@social_bp.route('/social/queue/<post_id>/publish', methods=['POST'])
def publish_post(post_id):
    """Immediately publish a queued post."""
    manager = get_social_manager()
    result = manager.publish_now(post_id)
    return jsonify(result)


@social_bp.route('/social/queue/process', methods=['POST'])
def process_queue():
    """Process all due posts in the queue."""
    manager = get_social_manager()
    results = manager.process_queue()
    return jsonify({
        "processed": len(results),
        "results": results,
    })


# ============================================================
# Quick Publish
# ============================================================

@social_bp.route('/social/publish', methods=['POST'])
def publish_now():
    """Generate and publish an article immediately."""
    manager = get_social_manager()
    data = request.json or {}

    article_id = data.get("article_id")
    if not article_id:
        return jsonify({"error": "article_id required"}), 400

    from server.services.storage import ArticleStore
    article_store = ArticleStore(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    article = article_store.get(article_id)
    if not article:
        return jsonify({"error": f"Article {article_id} not found"}), 404

    platforms = data.get("platforms")
    result = manager.publish_article_now(article, platforms)
    return jsonify(result)


# ============================================================
# History & Stats
# ============================================================

@social_bp.route('/social/history', methods=['GET'])
def get_history():
    """Get recent post history."""
    manager = get_social_manager()
    limit = request.args.get("limit", 50, type=int)
    history = manager.get_post_history(limit)
    return jsonify({"history": history})


@social_bp.route('/social/stats', methods=['GET'])
def get_stats():
    """Get social media statistics."""
    manager = get_social_manager()
    stats = manager.get_scheduler_stats()
    return jsonify(stats)


# ============================================================
# Moltbook-specific
# ============================================================

@social_bp.route('/social/moltbook/register', methods=['POST'])
def moltbook_register():
    """Register agent on Moltbook."""
    manager = get_social_manager()
    publisher = manager.publishers.get("moltbook")
    if not publisher:
        return jsonify({"error": "Moltbook publisher not available"}), 500

    data = request.json or {}
    result = publisher.register_agent(
        name=data.get("name", "AIAgencyBot"),
        description=data.get("description", "AI news and agent updates"),
    )
    return jsonify(result)


@social_bp.route('/social/moltbook/submolts', methods=['GET'])
def moltbook_submolts():
    """List Moltbook submolts."""
    manager = get_social_manager()
    publisher = manager.publishers.get("moltbook")
    if not publisher:
        return jsonify({"error": "Moltbook publisher not available"}), 500

    submolts = publisher.list_submolts()
    return jsonify({"submolts": submolts})
