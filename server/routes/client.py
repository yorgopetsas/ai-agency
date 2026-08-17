"""Client API routes."""
from flask import Blueprint, request, jsonify
from auth.middleware import require_auth, require_role, get_current_user
from client.manager import client_manager, INDUSTRIES, PLANS

client_bp = Blueprint("clients", __name__, url_prefix="/api/clients")


@client_bp.route("", methods=["POST"])
@require_role("admin", "superadmin")
def create_client():
    """Create a new client (admin/reseller only)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    reseller_id = data.get("reseller_id")
    company = data.get("company", "").strip() or None
    phone = data.get("phone", "").strip() or None
    industry = data.get("industry")
    plan = data.get("plan", "free")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    client, error = client_manager.create_client(
        name=name,
        email=email,
        reseller_id=reseller_id,
        company=company,
        phone=phone,
        industry=industry,
        plan=plan,
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"client": client.to_dict()}), 201


@client_bp.route("", methods=["GET"])
@require_role("admin", "superadmin")
def list_clients():
    """List all clients (admin can filter by reseller_id, status, plan)."""
    reseller_id = request.args.get("reseller_id")
    status = request.args.get("status")
    plan = request.args.get("plan")
    clients = client_manager.list_clients(reseller_id=reseller_id, status=status, plan=plan)
    return jsonify({
        "clients": [c.to_dict() for c in clients],
        "total": len(clients),
        "industries": INDUSTRIES,
        "plans": PLANS,
    })


@client_bp.route("/<client_id>", methods=["GET"])
@require_auth
def get_client(client_id):
    """Get client by ID."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    result = client_manager.get_client_with_reseller(client_id)
    if not result:
        return jsonify({"error": "Client not found"}), 404

    return jsonify({"client": result})


@client_bp.route("/<client_id>", methods=["PUT"])
@require_auth
def update_client(client_id):
    """Update client."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    client, error = client_manager.update_client(client_id, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"client": client.to_dict()})


@client_bp.route("/<client_id>", methods=["DELETE"])
@require_role("admin", "superadmin")
def delete_client(client_id):
    """Delete client (admin only)."""
    success, error = client_manager.delete_client(client_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Client deleted"})


@client_bp.route("/<client_id>/activate", methods=["POST"])
@require_role("admin", "superadmin")
def activate_client(client_id):
    """Activate a client."""
    success, error = client_manager.activate_client(client_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Client activated"})


@client_bp.route("/<client_id>/suspend", methods=["POST"])
@require_role("admin", "superadmin")
def suspend_client(client_id):
    """Suspend a client."""
    success, error = client_manager.suspend_client(client_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Client suspended"})


@client_bp.route("/<client_id>/stats", methods=["GET"])
@require_auth
def client_stats(client_id):
    """Get client usage stats."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    client = client_manager.get_client(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    return jsonify({
        "client_id": client_id,
        "plan": client.plan,
        "status": client.status,
        "industry": client.industry,
        "created_at": client.created_at,
    })
