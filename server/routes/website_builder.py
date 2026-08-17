"""Website builder API routes."""
from flask import Blueprint, request, jsonify
from auth.middleware import require_auth, require_role
from website_builder.engine import WebsiteBuilder

website_builder_bp = Blueprint("website_builder", __name__)
builder = WebsiteBuilder()


@website_builder_bp.route("/api/websites/build", methods=["POST"])
@require_auth
@require_role("admin", "reseller")
def build_website():
    """Build a website for a client."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    client_id = data.get("client_id")
    if not client_id:
        return jsonify({"error": "client_id required"}), 400

    # Load client branding if not provided
    branding = data.get("branding")
    client_name = data.get("client_name", "My Website")
    industry = data.get("industry", "technology")
    pages = data.get("pages")

    if not branding:
        try:
            from branding.manager import BrandingManager
            bm = BrandingManager()
            b = bm.get_branding(client_id)
            if b:
                branding = {
                    "primary_color": b.primary_color,
                    "secondary_color": b.secondary_color,
                    "accent_color": b.accent_color,
                    "font_family": b.font_family,
                    "theme": b.theme,
                    "welcome_message": b.welcome_message,
                    "footer_text": b.footer_text,
                }
        except Exception:
            branding = {}

    result = builder.build(
        client_id=client_id,
        client_name=client_name,
        industry=industry,
        branding=branding,
        pages=pages,
    )

    status = 201 if result["success"] else 500
    return jsonify(result), status


@website_builder_bp.route("/api/websites", methods=["GET"])
@require_auth
@require_role("admin")
def list_websites():
    """List all built client websites."""
    websites = builder.list_websites()
    return jsonify({
        "websites": list(websites.values()),
        "total": len(websites),
    })


@website_builder_bp.route("/api/websites/<client_id>", methods=["GET"])
@require_auth
@require_role("admin", "reseller")
def get_website(client_id):
    """Get info about a client's website."""
    path = builder.get_website_path(client_id)
    if not path:
        return jsonify({"error": "Website not found"}), 404

    import os
    info = {"client_id": client_id, "path": path, "files": []}
    for root, dirs, files in os.walk(path):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), path)
            info["files"].append(rel)
    info["total_files"] = len(info["files"])
    return jsonify(info)


@website_builder_bp.route("/api/websites/<client_id>", methods=["DELETE"])
@require_auth
@require_role("admin")
def delete_website(client_id):
    """Delete a client's website."""
    deleted = builder.delete_website(client_id)
    if not deleted:
        return jsonify({"error": "Website not found"}), 404
    return jsonify({"success": True, "client_id": client_id})


@website_builder_bp.route("/api/websites/<client_id>/preview", methods=["GET"])
@require_auth
def preview_website(client_id):
    """Get the website preview data (branding + content)."""
    from branding.manager import BrandingManager
    from billing.manager import BillingManager

    bm = BrandingManager()
    bill = BillingManager()

    branding = bm.get_branding(client_id)
    plan_info = bill.get_client_plan(client_id)

    return jsonify({
        "client_id": client_id,
        "branding": branding.to_dict() if branding else None,
        "plan": plan_info,
        "has_website": builder.get_website_path(client_id) is not None,
    })
