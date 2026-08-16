"""
Workflow Routes
=============
API routes for the news workflow (research → write → approve).
"""

from flask import Blueprint, jsonify, request
from server.services.research import ResearchService
from server.services.writer import WriterService
from server.services.publisher import PublisherService

workflow_bp = Blueprint('workflow', __name__)

researcher = ResearchService()
writer = WriterService()
publisher = PublisherService()


@workflow_bp.route('/research', methods=['POST'])
def research_url():
    """
    Research a URL and generate summary.
    
    Request body:
        {"url": "https://example.com/news"}
        
    Returns:
        JSON with summary and pending ID
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    
    if not url.startswith('http'):
        return jsonify({"error": "Invalid URL"}), 400
    
    result = researcher.research(url)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@workflow_bp.route('/write', methods=['POST'])
def write_article():
    """
    Write an article from a summary.
    
    Request body:
        {"summary": "Summary text", "url": "Source URL"}
        
    Returns:
        JSON with article content and pending ID
    """
    data = request.get_json()
    
    if not data or 'summary' not in data:
        return jsonify({"error": "Summary is required"}), 400
    
    summary = data['summary']
    url = data.get('url', '')
    title = data.get('title', '')
    
    result = writer.write(summary, url, title)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@workflow_bp.route('/pending', methods=['GET'])
def get_pending():
    """
    Get all pending items.
    
    Returns:
        JSON array of pending items
    """
    research_pending = researcher.get_pending()
    articles_pending = publisher.get_pending()
    
    return jsonify({
        "research": research_pending,
        "articles": articles_pending
    })


@workflow_bp.route('/workflow/research-to-article', methods=['POST'])
def research_to_article():
    """
    Combined endpoint: research URL then write article.
    First returns summary for approval, then article.
    
    Request body:
        {"url": "https://example.com/news"}
        
    Step 1: Returns summary for approval
    Step 2: After approval, call /api/write with summary
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    
    # Step 1: Research
    research_result = researcher.research(url)
    
    if not research_result.get('success'):
        return jsonify(research_result), 500
    
    # Return for approval step
    return jsonify({
        "step": "research_complete",
        "pending_id": research_result.get('id'),
        "summary": research_result.get('summary'),
        "url": url,
        "next_step": "write",
        "message": "Summary ready. Approve to continue to article writing."
    })


@workflow_bp.route('/workflow/complete', methods=['POST'])
def complete_workflow():
    """
    Complete workflow: publish approved article.
    
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