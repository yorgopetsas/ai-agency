"""Provisioning API routes."""
from flask import Blueprint, request, jsonify, g
from auth.middleware import require_auth, require_role
from provisioning.engine import ProvisioningEngine, ProvisioningError

provisioning_bp = Blueprint("provisioning", __name__)
engine = ProvisioningEngine()


@provisioning_bp.route("/api/provisioning/provision", methods=["POST"])
@require_auth
@require_role("admin", "reseller")
def provision_client():
    """Provision a new client (admin or reseller). Rate-limited to 10/minute."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ["name", "email", "admin_password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Resellers can only provision under themselves
    reseller_id = data.get("reseller_id")
    user = g.get("user")
    if user and getattr(user, "role", None) == "reseller" and not reseller_id:
        reseller_id = getattr(user, "reseller_id", None)

    try:
        result = engine.provision_client(
            name=data["name"],
            email=data["email"],
            admin_password=data["admin_password"],
            plan_id=data.get("plan_id", "free"),
            reseller_id=reseller_id,
            company=data.get("company"),
            phone=data.get("phone"),
            industry=data.get("industry"),
            branding_overrides=data.get("branding"),
        )
        return jsonify(result.to_dict()), 201
    except ProvisioningError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Provisioning failed: {e}"}), 500


@provisioning_bp.route("/api/provisioning/deprovision/<client_id>", methods=["POST"])
@require_auth
@require_role("admin")
def deprovision_client(client_id):
    """Suspend a client and all their users."""
    result = engine.deprovision_client(client_id)
    status = 200 if result["success"] else 404
    return jsonify(result), status


@provisioning_bp.route("/api/provisioning/reprovision/<client_id>", methods=["POST"])
@require_auth
@require_role("admin")
def reprovision_client(client_id):
    """Re-activate a suspended client."""
    data = request.get_json() or {}
    result = engine.reprovision_client(client_id, new_plan=data.get("plan_id"))
    status = 200 if result["success"] else 404
    return jsonify(result), status


@provisioning_bp.route("/api/provisioning/preview/<client_id>", methods=["GET"])
@require_auth
@require_role("admin", "reseller")
def preview_provisioning(client_id):
    """Preview what provisioning would create (dry run — does not create anything)."""
    from client.manager import ClientManager
    from branding.manager import BrandingManager
    from billing.manager import BillingManager
    from auth.models import AuthDB

    cm = ClientManager()
    bm = BrandingManager()
    bill = BillingManager()
    db = AuthDB()

    client = cm.get_client(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    branding = bm.get_branding(client_id)
    plan_info = bill.get_client_plan(client_id)
    users = db.list_users(client_id=client_id)

    return jsonify({
        "client": client.to_dict(),
        "branding": branding.to_dict() if branding else None,
        "plan": plan_info,
        "users": [u.to_dict() for u in users],
    })
