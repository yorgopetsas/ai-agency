"""
Admin Routes
===========
API routes for admin operations (approve, reject, pending management).
"""

from flask import Blueprint, jsonify, request
from server.services.research import ResearchService
from server.services.writer import WriterService
from server.services.publisher import PublisherService

admin_bp = Blueprint('admin', __name__)

researcher = ResearchService()
writer = WriterService()
publisher = PublisherService()


@admin_bp.route('/approve', methods=['POST'])
def approve_item():
    """
    Approve a pending item.
    
    For research: mark as approved, continue to write
    For article: mark as approved, ready to publish
    
    Request body:
        {"id": "pending_xxx", "type": "research|article"}
    """
    data = request.get_json()
    
    if not data or 'id' not in data:
        return jsonify({"error": "ID is required"}), 400
    
    item_id = data['id']
    item_type = data.get('type', 'article')
    
    if item_type == 'research':
        # Get research item
        pending = researcher.get_pending()
        research_item = None
        for p in pending:
            if p.get('id') == item_id:
                research_item = p
                break
        
        if not research_item:
            return jsonify({"error": "Research not found"}), 404
        
        # Write article from summary (include title for reference)
        write_result = writer.write(
            research_item['summary'],
            research_item['url'],
            title=research_item.get('title', '')
        )
        
        # Remove research from pending
        researcher.remove_pending(item_id)
        
        if write_result.get('success'):
            return jsonify({
                "step": "write_complete",
                "article_id": write_result.get('id'),
                "headline": write_result.get('headline'),
                "next_step": "publish",
                "message": "Article written. Approve to publish."
            })
        else:
            return jsonify(write_result), 500
    
    elif item_type == 'article':
        # Ready to publish
        return jsonify({
            "step": "ready_to_publish",
            "article_id": item_id,
            "message": "Article approved. Ready to publish."
        })
    
    return jsonify({"error": "Invalid type"}), 400


@admin_bp.route('/reject', methods=['POST'])
def reject_item():
    """
    Reject a pending item.
    
    Request body:
        {"id": "pending_xxx", "feedback": "Optional feedback"}
    """
    data = request.get_json()
    
    if not data or 'id' not in data:
        return jsonify({"error": "ID is required"}), 400
    
    item_id = data['id']
    feedback = data.get('feedback', '')
    
    # Remove from pending
    publisher.reject(item_id, feedback)
    
    return jsonify({
        "success": True,
        "message": "Item rejected"
    })


@admin_bp.route('/publish', methods=['POST'])
def publish_article():
    """
    Publish an approved article.
    
    Request body:
        {"article_id": "pending_xxx"}
    """
    data = request.get_json()
    
    if not data or 'article_id' not in data:
        return jsonify({"error": "Article ID is required"}), 400
    
    article_id = data['article_id']
    
    result = publisher.publish(article_id)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@admin_bp.route('/pending/all', methods=['GET'])
def get_all_pending():
    """
    Get all pending items (research + articles).
    
    Returns:
        JSON with both types
    """
    research_pending = researcher.get_pending()
    articles_pending = publisher.get_pending()
    
    return jsonify({
        "research": research_pending,
        "articles": articles_pending,
        "total": len(research_pending) + len(articles_pending)
    })


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get workflow statistics.
    
    Returns:
        JSON with counts
    """
    research_pending = researcher.get_pending()
    articles_pending = publisher.get_pending()
    published = publisher.get_articles()
    
    return jsonify({
        "pending_research": len(research_pending),
        "pending_articles": len(articles_pending),
        "published": len(published)
    })