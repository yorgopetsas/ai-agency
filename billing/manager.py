"""Billing management business logic."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Tuple, List
from .models import Plan, ClientPlan, UsageRecord, billing_db


class BillingManager:
    """High-level billing operations."""

    def __init__(self):
        self.db = billing_db
        self.db.seed_plans()

    def list_plans(self) -> List[Plan]:
        """List available plans."""
        return self.db.list_plans()

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan details."""
        return self.db.get_plan(plan_id)

    def get_client_plan(self, client_id: str) -> Optional[Dict]:
        """Get client's current plan with details."""
        cp = self.db.get_client_plan(client_id)
        if not cp:
            # Default to free plan
            plan = self.db.get_plan("free")
            return {
                "plan_id": "free",
                "plan": plan.to_dict() if plan else None,
                "billing_cycle": "monthly",
                "status": "active",
            }
        plan = self.db.get_plan(cp.plan_id)
        return {
            "plan_id": cp.plan_id,
            "plan": plan.to_dict() if plan else None,
            "billing_cycle": cp.billing_cycle,
            "started_at": cp.started_at,
            "expires_at": cp.expires_at,
            "status": cp.status,
        }

    def assign_plan(self, client_id: str, plan_id: str,
                    billing_cycle: str = "monthly") -> Tuple[Optional[ClientPlan], str]:
        """Assign a plan to a client."""
        plan = self.db.get_plan(plan_id)
        if not plan:
            return None, "Plan not found"

        if billing_cycle not in ("monthly", "yearly"):
            return None, "billing_cycle must be 'monthly' or 'yearly'"

        cp = ClientPlan(
            client_id=client_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
        )
        self.db.assign_plan(cp)
        return cp, None

    def record_usage(self, client_id: str, metric: str, quantity: int = 1,
                     metadata: Dict = None) -> UsageRecord:
        """Record usage for a client."""
        record = UsageRecord(
            id=str(uuid.uuid4()),
            client_id=client_id,
            metric=metric,
            quantity=quantity,
            metadata=metadata or {},
        )
        self.db.record_usage(record)
        return record

    def get_usage(self, client_id: str, metric: str = None, period: str = None) -> List[UsageRecord]:
        """Get usage records."""
        return self.db.get_usage(client_id, metric=metric, period=period)

    def get_usage_summary(self, client_id: str, period: str = None) -> Dict:
        """Get usage summary for all metrics."""
        if not period:
            period = datetime.utcnow().strftime("%Y-%m")

        plan_info = self.get_client_plan(client_id)
        quotas = {}
        if plan_info and plan_info.get("plan"):
            quotas = plan_info["plan"].get("quotas", {})

        # Map metric names to quota keys
        metric_to_quota = {
            "tasks": "tasks_per_month",
            "api_calls": "api_calls",
            "storage_mb": "storage_mb",
            "users": "users",
        }

        metrics = ["tasks", "storage_mb", "api_calls", "users"]
        usage = {}
        for metric in metrics:
            used = self.db.sum_usage(client_id, metric, period)
            quota_key = metric_to_quota.get(metric, metric)
            limit = quotas.get(quota_key, 0)
            usage[metric] = {
                "used": used,
                "limit": limit,
                "unlimited": limit == -1,
                "percentage": round(used / limit * 100, 1) if limit > 0 else 0,
            }

        return {
            "client_id": client_id,
            "period": period,
            "plan": plan_info.get("plan_id", "free"),
            "usage": usage,
        }

    def check_quota(self, client_id: str, metric: str) -> Tuple[bool, Dict]:
        """Check if client has quota available for a metric."""
        # Map metric names to quota keys
        metric_to_quota = {
            "tasks": "tasks_per_month",
            "api_calls": "api_calls",
            "storage_mb": "storage_mb",
            "users": "users",
        }
        quota_key = metric_to_quota.get(metric, metric)

        plan_info = self.get_client_plan(client_id)
        quotas = {}
        if plan_info and plan_info.get("plan"):
            quotas = plan_info["plan"].get("quotas", {})

        limit = quotas.get(quota_key, 0)
        if limit == -1:
            return True, {"unlimited": True}

        used = self.db.sum_usage(client_id, metric)
        if used >= limit:
            return False, {
                "used": used,
                "limit": limit,
                "remaining": 0,
                "error": f"Quota exceeded for {metric}",
            }

        return True, {
            "used": used,
            "limit": limit,
            "remaining": limit - used,
        }

    def delete_usage(self, record_id: str) -> bool:
        """Delete a usage record."""
        return self.db.delete_usage(record_id)


billing_manager = BillingManager()
