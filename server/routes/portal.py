"""Client portal route — client-facing dashboard."""
from flask import Blueprint, render_template

portal_bp = Blueprint("portal", __name__)


@portal_bp.route("/portal")
def portal():
    """Render the client-facing portal."""
    return render_template("portal.html")
