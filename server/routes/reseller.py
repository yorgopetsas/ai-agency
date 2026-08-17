"""Reseller API routes."""
from flask import Blueprint, request, jsonify
from auth.middleware import require_auth, require_role, get_current_user
from reseller.manager import reseller_manager

reseller_bp = Blueprint("resellers", __name__, url_prefix="/api/resellers")


@reseller_bp.route("", methods=["POST"])
@require_role("admin", "superadmin")
def create_reseller():
    """Create a new reseller (admin only)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    company = data.get("company", "").strip() or None
    phone = data.get("phone", "").strip() or None
    parent_id = data.get("parent_id")
    tier = data.get("tier", "standard")
    max_clients = data.get("max_clients", 10)

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    reseller, error = reseller_manager.create_reseller(
        name=name,
        email=email,
        company=company,
        phone=phone,
        parent_id=parent_id,
        tier=tier,
        max_clients=max_clients,
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"reseller": reseller.to_dict()}), 201


@reseller_bp.route("", methods=["GET"])
@require_role("admin", "superadmin")
def list_resellers():
    """List all resellers (admin only)."""
    parent_id = request.args.get("parent_id")
    status = request.args.get("status")
    resellers = reseller_manager.list_resellers(parent_id=parent_id, status=status)
    return jsonify({
        "resellers": [r.to_dict() for r in resellers],
        "total": len(resellers),
    })


@reseller_bp.route("/<reseller_id>", methods=["GET"])
@require_auth
def get_reseller(reseller_id):
    """Get reseller by ID."""
    user = get_current_user()

    # Non-admins can only view their own reseller
    if user.role not in ("admin", "superadmin"):
        if not hasattr(user, "reseller_id") or user.reseller_id != reseller_id:
            return jsonify({"error": "Access denied"}), 403

    reseller = reseller_manager.get_reseller(reseller_id)
    if not reseller:
        return jsonify({"error": "Reseller not found"}), 404

    return jsonify({"reseller": reseller.to_dict()})


@reseller_bp.route("/<reseller_id>", methods=["PUT"])
@require_auth
def update_reseller(reseller_id):
    """Update reseller."""
    user = get_current_user()

    # Non-admins can only update their own reseller
    if user.role not in ("admin", "superadmin"):
        if not hasattr(user, "reseller_id") or user.reseller_id != reseller_id:
            return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    reseller, error = reseller_manager.update_reseller(reseller_id, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"reseller": reseller.to_dict()})


@reseller_bp.route("/<reseller_id>", methods=["DELETE"])
@require_role("admin", "superadmin")
def delete_reseller(reseller_id):
    """Delete reseller (admin only)."""
    success, error = reseller_manager.delete_reseller(reseller_id)
    if not success:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Reseller deleted"})


@reseller_bp.route("/<reseller_id>/hierarchy", methods=["GET"])
@require_auth
def get_hierarchy(reseller_id):
    """Get reseller hierarchy info."""
    user = get_current_user()

    # Non-admins can only view their own hierarchy
    if user.role not in ("admin", "superadmin"):
        if not hasattr(user, "reseller_id") or user.reseller_id != reseller_id:
            return jsonify({"error": "Access denied"}), 403

    hierarchy = reseller_manager.get_hierarchy(reseller_id)
    if not hierarchy:
        return jsonify({"error": "Reseller not found"}), 404

    return jsonify(hierarchy)


@reseller_bp.route("/<reseller_id>/children", methods=["GET"])
@require_auth
def get_children(reseller_id):
    """Get direct children of a reseller."""
    user = get_current_user()

    # Non-admins can only view their own children
    if user.role not in ("admin", "superadmin"):
        if not hasattr(user, "reseller_id") or user.reseller_id != reseller_id:
            return jsonify({"error": "Access denied"}), 403

    children = reseller_manager.db.get_children(reseller_id)
    return jsonify({
        "children": [c.to_dict() for c in children],
        "total": len(children),
    })


@reseller_bp.route("/<reseller_id>/suspend", methods=["POST"])
@require_role("admin", "superadmin")
def suspend_reseller(reseller_id):
    """Suspend a reseller (admin only)."""
    success, error = reseller_manager.suspend_reseller(reseller_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Reseller suspended"})


@reseller_bp.route("/<reseller_id>/activate", methods=["POST"])
@require_role("admin", "superadmin")
def activate_reseller(reseller_id):
    """Activate a reseller (admin only)."""
    success, error = reseller_manager.activate_reseller(reseller_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Reseller activated"})
