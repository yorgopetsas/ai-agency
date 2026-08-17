"""
Mobile App Builder Routes
=========================
API endpoints for generating white-labeled mobile apps.
"""

from flask import Blueprint, request, jsonify
from server.services.mobile_builder import mobile_app_builder
from server.services.branding_manager import branding_manager

mobile_bp = Blueprint("mobile", __name__)


@mobile_bp.route("/api/mobile/build", methods=["POST"])
def build_app():
    """Generate a mobile app for a client."""
    data = request.get_json() or {}
    client_id = data.get("client_id")
    if not client_id:
        return jsonify({"error": "client_id required"}), 400

    branding = branding_manager.get(client_id)
    if not branding:
        return jsonify({"error": "Client branding not found"}), 404

    branding_dict = branding if isinstance(branding, dict) else branding.to_dict()
    result = mobile_app_builder.build(
        client_id=client_id,
        branding=branding_dict,
        server_url=data.get("server_url", "http://localhost:5001"),
    )
    status = 200 if result.get("success") else 500
    return jsonify(result), status


@mobile_bp.route("/api/mobile/apps", methods=["GET"])
def list_apps():
    """List all generated mobile apps."""
    apps = mobile_app_builder.list_apps()
    return jsonify({"apps": apps, "count": len(apps)})


@mobile_bp.route("/api/mobile/apps/<client_id>", methods=["GET"])
def get_app(client_id):
    """Get info about a generated app."""
    app = mobile_app_builder.get_app(client_id)
    if not app:
        return jsonify({"error": "App not found"}), 404
    return jsonify(app)


@mobile_bp.route("/api/mobile/apps/<client_id>", methods=["DELETE"])
def delete_app(client_id):
    """Delete a generated app."""
    import shutil
    app_dir = mobile_app_builder.clients_dir / client_id
    if app_dir.exists():
        shutil.rmtree(app_dir)
        return jsonify({"success": True, "message": f"Deleted app for {client_id}"})
    return jsonify({"error": "App not found"}), 404
