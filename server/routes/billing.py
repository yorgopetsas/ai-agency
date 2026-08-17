"""Billing API routes."""
from flask import Blueprint, request, jsonify
from auth.middleware import require_auth, require_role, get_current_user
from billing.manager import billing_manager

billing_bp = Blueprint("billing", __name__, url_prefix="/api/billing")


@billing_bp.route("/plans", methods=["GET"])
def list_plans():
    """List available plans (public)."""
    plans = billing_manager.list_plans()
    return jsonify({"plans": [p.to_dict() for p in plans]})


@billing_bp.route("/plans/<plan_id>", methods=["GET"])
def get_plan(plan_id):
    """Get plan details (public)."""
    plan = billing_manager.get_plan(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify({"plan": plan.to_dict()})


@billing_bp.route("/clients/<client_id>", methods=["GET"])
@require_auth
def get_client_plan(client_id):
    """Get client's current plan."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    plan = billing_manager.get_client_plan(client_id)
    return jsonify({"client_plan": plan})


@billing_bp.route("/clients/<client_id>/assign", methods=["POST"])
@require_role("admin", "superadmin")
def assign_plan(client_id):
    """Assign a plan to a client."""
    data = request.get_json()
    if not data or not data.get("plan_id"):
        return jsonify({"error": "plan_id required"}), 400

    cp, error = billing_manager.assign_plan(
        client_id,
        data["plan_id"],
        data.get("billing_cycle", "monthly"),
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"client_plan": cp.to_dict()})


@billing_bp.route("/clients/<client_id>/usage", methods=["GET"])
@require_auth
def get_usage(client_id):
    """Get usage records."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    metric = request.args.get("metric")
    period = request.args.get("period")
    records = billing_manager.get_usage(client_id, metric=metric, period=period)
    return jsonify({
        "records": [r.to_dict() for r in records],
        "total": len(records),
    })


@billing_bp.route("/clients/<client_id>/usage", methods=["POST"])
@require_role("admin", "superadmin")
def record_usage(client_id):
    """Record usage for a client."""
    data = request.get_json()
    if not data or not data.get("metric"):
        return jsonify({"error": "metric required"}), 400

    record = billing_manager.record_usage(
        client_id,
        data["metric"],
        data.get("quantity", 1),
        data.get("metadata"),
    )
    return jsonify({"record": record.to_dict()}), 201


@billing_bp.route("/clients/<client_id>/summary", methods=["GET"])
@require_auth
def usage_summary(client_id):
    """Get usage summary for all metrics."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    period = request.args.get("period")
    summary = billing_manager.get_usage_summary(client_id, period=period)
    return jsonify(summary)


@billing_bp.route("/clients/<client_id>/quota/<metric>", methods=["GET"])
@require_auth
def check_quota(client_id, metric):
    """Check quota for a specific metric."""
    user = get_current_user()
    if user.role not in ("admin", "superadmin"):
        if user.client_id != client_id:
            return jsonify({"error": "Access denied"}), 403

    available, info = billing_manager.check_quota(client_id, metric)
    return jsonify({"available": available, **info})


@billing_bp.route("/usage/<record_id>", methods=["DELETE"])
@require_role("admin", "superadmin")
def delete_usage(record_id):
    """Delete a usage record."""
    success = billing_manager.delete_usage(record_id)
    if not success:
        return jsonify({"error": "Record not found"}), 404
    return jsonify({"message": "Record deleted"})
