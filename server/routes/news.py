"""
News Routes
==========
API routes for news articles.
"""

from flask import Blueprint, jsonify, current_app
from server.services.publisher import PublisherService

news_bp = Blueprint('news', __name__)
publisher = PublisherService()


@news_bp.route('/news', methods=['GET'])
def get_news():
    """
    Get all published articles.
    
    Returns:
        JSON array of articles
    """
    articles = publisher.get_articles()
    return jsonify(articles)


@news_bp.route('/news/<article_id>', methods=['GET'])
def get_article(article_id):
    """
    Get a single article by ID.
    
    Args:
        article_id: Article ID
        
    Returns:
        JSON article object
    """
    articles = publisher.get_articles()
    for article in articles:
        if article.get('id') == article_id:
            return jsonify(article)
    
    return jsonify({"error": "Article not found"}), 404


@news_bp.route('/news/latest', methods=['GET'])
def get_latest():
    """
    Get the latest article.
    
    Returns:
        JSON latest article
    """
    articles = publisher.get_articles()
    if articles:
        return jsonify(articles[0])
    return jsonify(None)


@news_bp.route('/news/count', methods=['GET'])
def count_news():
    """
    Get count of published articles.
    
    Returns:
        JSON with count
    """
    articles = publisher.get_articles()
    return jsonify({"count": len(articles)})