"""Branding API routes."""
from flask import Blueprint, request, jsonify
from auth.middleware import require_auth, require_role, get_current_user
from branding.manager import branding_manager, THEMES, FONTS

branding_bp = Blueprint("branding", __name__, url_prefix="/api/branding")


@branding_bp.route("/<client_id>", methods=["GET"])
@require_auth
def get_branding(client_id):
    """Get branding for a client."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    branding = branding_manager.get_branding(client_id)
    if not branding:
        return jsonify({"branding": None, "message": "No custom branding set"})
    return jsonify({"branding": branding.to_dict()})


@branding_bp.route("/<client_id>", methods=["PUT"])
@require_auth
def update_branding(client_id):
    """Update branding for a client."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    branding, error = branding_manager.update_branding(client_id, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"branding": branding.to_dict()})


@branding_bp.route("/<client_id>/logo", methods=["POST"])
@require_auth
def upload_logo(client_id):
    """Upload logo for a client."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    url, error = branding_manager.save_logo(client_id, file.read(), file.filename)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"logo_url": url})


@branding_bp.route("/<client_id>", methods=["DELETE"])
@require_role("admin", "superadmin")
def delete_branding(client_id):
    """Reset branding to defaults."""
    success, error = branding_manager.delete_branding(client_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Branding reset to defaults"})


@branding_bp.route("/<client_id>/preview", methods=["GET"])
@require_auth
def preview_branding(client_id):
    """Get branding as CSS preview data."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    preview = branding_manager.get_preview(client_id)
    return jsonify(preview)


@branding_bp.route("/themes", methods=["GET"])
def list_themes():
    """List available themes."""
    return jsonify({"themes": THEMES})


@branding_bp.route("/fonts", methods=["GET"])
def list_fonts():
    """List available fonts."""
    return jsonify({"fonts": FONTS})


@branding_bp.route("/domain/<domain>", methods=["GET"])
def resolve_domain(domain):
    """Resolve a custom domain to client branding (public)."""
    branding = branding_manager.get_by_domain(domain)
    if not branding:
        return jsonify({"error": "Domain not configured"}), 404
    return jsonify({
        "client_id": branding.client_id,
        "branding": branding.to_dict(),
    })
