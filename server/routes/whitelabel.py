"""Whitelabel dashboard route."""
from flask import Blueprint, render_template

whitelabel_bp = Blueprint("whitelabel", __name__)


@whitelabel_bp.route("/dashboard")
def dashboard():
    """Render the whitelabel admin dashboard."""
    return render_template("whitelabel.html")
