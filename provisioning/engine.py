"""
Provisioning Engine — auto-provision new client instances.

Steps:
1. Create client record
2. Set up default branding
3. Assign billing plan
4. Create admin user for the client
5. Initialize data-isolation directories (knowledge, memory)
"""

import os
import uuid
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

from client.manager import ClientManager
from branding.manager import BrandingManager
from billing.manager import BillingManager
from auth.models import AuthDB, User
from auth.password import hash_password
from knowledge_manager import KnowledgeManager

logger = logging.getLogger(__name__)

# Knowledge base root
KNOWLEDGE_BASE_DIR = "/Users/yorgopetsasedel/dev/opencode/ai_agency/knowledge"

# Default branding for new clients
DEFAULT_BRANDING = {
    "primary_color": "#6366F1",
    "secondary_color": "#8B5CF6",
    "accent_color": "#22D3EE",
    "font_family": "Inter",
    "theme": "light",
    "welcome_message": "Welcome to our AI-powered platform!",
    "footer_text": "Powered by Amanita AI Agency",
}


class ProvisioningError(Exception):
    """Raised when provisioning fails."""
    pass


class ProvisioningResult:
    """Result of a provisioning operation."""

    def __init__(self):
        self.success = False
        self.client = None
        self.branding = None
        self.plan = None
        self.admin_user = None
        self.errors = []
        self.steps_completed = []

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "client": self.client.to_dict() if self.client else None,
            "branding": self.branding.to_dict() if self.branding else None,
            "plan": self.plan,
            "admin_user": self.admin_user.to_dict() if self.admin_user else None,
            "errors": self.errors,
            "steps_completed": self.steps_completed,
        }


class ProvisioningEngine:
    """Orchestrates full client provisioning in one atomic flow."""

    def __init__(self):
        self.client_mgr = ClientManager()
        self.branding_mgr = BrandingManager()
        self.billing_mgr = BillingManager()
        self.auth_db = AuthDB()

    def provision_client(
        self,
        name: str,
        email: str,
        admin_password: str,
        plan_id: str = "free",
        reseller_id: str = None,
        company: str = None,
        phone: str = None,
        industry: str = None,
        branding_overrides: Dict = None,
    ) -> ProvisioningResult:
        """
        Provision a new client end-to-end.

        Args:
            name: Client/business name
            email: Client contact email
            admin_password: Password for the client admin user
            plan_id: Billing plan (free, starter, pro, enterprise)
            reseller_id: Optional reseller who owns this client
            company: Optional company name
            phone: Optional phone
            industry: Optional industry classification
            branding_overrides: Optional branding field overrides

        Returns:
            ProvisioningResult with all created resources
        """
        result = ProvisioningResult()

        # Step 1: Create client record
        try:
            client, err = self.client_mgr.create_client(
                name=name,
                email=email,
                reseller_id=reseller_id,
                company=company,
                phone=phone,
                industry=industry,
                plan=plan_id,
            )
            if err:
                raise ProvisioningError(f"Client creation failed: {err}")
            result.client = client
            result.steps_completed.append("client_created")
            logger.info(f"Created client {client.id} ({client.name})")
        except ProvisioningError:
            raise
        except Exception as e:
            raise ProvisioningError(f"Client creation error: {e}")

        client_id = client.id

        # Step 2: Set up default branding
        try:
            branding_data = dict(DEFAULT_BRANDING)
            if branding_overrides:
                branding_data.update(branding_overrides)
            branding, err = self.branding_mgr.update_branding(client_id, **branding_data)
            if err:
                raise ProvisioningError(f"Branding setup failed: {err}")
            result.branding = branding
            result.steps_completed.append("branding_created")
            logger.info(f"Created branding for client {client_id}")
        except ProvisioningError:
            raise
        except Exception as e:
            raise ProvisioningError(f"Branding error: {e}")

        # Step 3: Assign billing plan
        try:
            plan, err = self.billing_mgr.assign_plan(client_id, plan_id)
            if err:
                raise ProvisioningError(f"Plan assignment failed: {err}")
            result.plan = self.billing_mgr.get_client_plan(client_id)
            result.steps_completed.append("plan_assigned")
            logger.info(f"Assigned plan {plan_id} to client {client_id}")
        except ProvisioningError:
            raise
        except Exception as e:
            raise ProvisioningError(f"Billing error: {e}")

        # Step 4: Create admin user
        try:
            admin_user = self._create_admin_user(
                client_id=client_id,
                email=email,
                name=f"{name} Admin",
                password=admin_password,
                reseller_id=reseller_id,
            )
            result.admin_user = admin_user
            result.steps_completed.append("admin_user_created")
            logger.info(f"Created admin user for client {client_id}")
        except Exception as e:
            raise ProvisioningError(f"Admin user creation error: {e}")

        # Step 5: Initialize data isolation directories
        try:
            self._init_client_data(client_id)
            result.steps_completed.append("data_dirs_created")
            logger.info(f"Initialized data dirs for client {client_id}")
        except Exception as e:
            # Non-fatal — directories can be created lazily
            logger.warning(f"Data dir init warning (non-fatal): {e}")
            result.steps_completed.append("data_dirs_created_with_warning")

        result.success = True
        logger.info(f"Provisioning complete for client {client_id} ({name})")
        return result

    def _create_admin_user(
        self,
        client_id: str,
        email: str,
        name: str,
        password: str,
        reseller_id: str = None,
    ) -> User:
        """Create an admin user for the client."""
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)

        user = User(
            id=user_id,
            email=email,
            name=name,
            password_hash=password_hash,
            role="admin",
            client_id=client_id,
            reseller_id=reseller_id,
            status="active",
        )
        return self.auth_db.create_user(user)

    def _init_client_data(self, client_id: str):
        """Create data-isolation directories for the client."""
        agents = ['researcher', 'writer', 'developer', 'designer', 'analyst']
        for agent in agents:
            path = os.path.join(KNOWLEDGE_BASE_DIR, client_id, agent)
            os.makedirs(path, exist_ok=True)

    def deprovision_client(self, client_id: str) -> Dict:
        """
        Deprovision a client (suspend + cleanup).

        This does NOT delete data — it suspends the client and marks resources
        as inactive. Full data deletion is a separate compliance operation.
        """
        # Suspend client
        client, err = self.client_mgr.suspend_client(client_id)
        if not client:
            return {"success": False, "error": err or "Client not found"}

        # Suspend admin users
        from auth.models import AuthDB
        db = AuthDB()
        users = db.list_users(client_id=client_id)
        for user in users:
            user.status = "suspended"
            db.update_user(user)

        return {
            "success": True,
            "client_id": client_id,
            "status": "suspended",
            "users_suspended": len(users),
        }

    def reprovision_client(self, client_id: str, new_plan: str = None) -> Dict:
        """
        Re-activate a previously suspended client.
        Optionally change their plan.
        """
        client, err = self.client_mgr.activate_client(client_id)
        if not client:
            return {"success": False, "error": err or "Client not found"}

        if new_plan:
            plan, err = self.billing_mgr.assign_plan(client_id, new_plan)
            if err:
                return {"success": False, "error": f"Plan change failed: {err}"}

        # Re-activate users
        db = AuthDB()
        users = db.list_users(client_id=client_id)
        for user in users:
            user.status = "active"
            db.update_user(user)

        return {
            "success": True,
            "client_id": client_id,
            "status": "active",
            "plan": new_plan or "unchanged",
            "users_reactivated": len(users),
        }
