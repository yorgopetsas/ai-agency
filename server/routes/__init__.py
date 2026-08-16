"""Routes package"""
from server.routes.news import news_bp
from server.routes.workflow import workflow_bp
from server.routes.admin import admin_bp

__all__ = ['news_bp', 'workflow_bp', 'admin_bp']