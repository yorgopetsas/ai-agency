"""Client management business logic."""
import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .models import Client, client_db
from reseller.models import reseller_db


# Allowed industries for client classification
INDUSTRIES = [
    "healthcare", "finance", "ecommerce", "education", "technology",
    "real_estate", "marketing", "legal", "manufacturing", "other",
]

# Allowed plans
PLANS = ["free", "starter", "pro", "enterprise"]


class ClientManager:
    """High-level client operations."""

    def __init__(self):
        self.db = client_db

    def create_client(
        self,
        name: str,
        email: str,
        reseller_id: str = None,
        company: str = None,
        phone: str = None,
        industry: str = None,
        plan: str = "free",
    ) -> Tuple[Optional[Client], str]:
        """Create a new client. Returns (client, error_message)."""
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return None, "Invalid email format"

        existing = self.db.get_by_email(email)
        if existing:
            return None, "Email already registered"

        slug = self._generate_slug(name)

        if industry and industry not in INDUSTRIES:
            return None, f"Invalid industry. Allowed: {', '.join(INDUSTRIES)}"

        if plan not in PLANS:
            return None, f"Invalid plan. Allowed: {', '.join(PLANS)}"

        # Validate reseller exists and can add client
        if reseller_id:
            reseller = reseller_db.get_by_id(reseller_id)
            if not reseller:
                return None, "Reseller not found"
            if reseller.status != "active":
                return None, "Reseller is not active"
            if not reseller_db.can_add_client(reseller_id):
                return None, "Reseller has reached client limit"

        client = Client(
            id=str(uuid.uuid4()),
            name=name,
            slug=slug,
            email=email,
            phone=phone,
            company=company,
            industry=industry,
            reseller_id=reseller_id,
            status="active",
            plan=plan,
        )
        self.db.create(client)
        return client, None

    def update_client(self, client_id: str, **kwargs) -> Tuple[Optional[Client], str]:
        """Update client fields."""
        client = self.db.get_by_id(client_id)
        if not client:
            return None, "Client not found"

        allowed = {"name", "email", "phone", "company", "industry", "plan", "status", "config", "reseller_id"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                if key == "industry" and value and value not in INDUSTRIES:
                    return None, f"Invalid industry"
                if key == "plan" and value not in PLANS:
                    return None, f"Invalid plan"
                setattr(client, key, value)

        if "name" in kwargs:
            client.slug = self._generate_slug(kwargs["name"], exclude_id=client_id)

        self.db.update(client)
        return client, None

    def delete_client(self, client_id: str) -> Tuple[bool, str]:
        """Delete a client."""
        client = self.db.get_by_id(client_id)
        if not client:
            return False, "Client not found"
        self.db.delete(client_id)
        return True, None

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        return self.db.get_by_id(client_id)

    def get_client_by_slug(self, slug: str) -> Optional[Client]:
        """Get client by slug."""
        return self.db.get_by_slug(slug)

    def list_clients(self, reseller_id: str = None, status: str = None,
                     plan: str = None) -> List[Client]:
        """List clients."""
        return self.db.list_clients(reseller_id=reseller_id, status=status, plan=plan)

    def suspend_client(self, client_id: str) -> Tuple[bool, str]:
        """Suspend a client."""
        client = self.db.get_by_id(client_id)
        if not client:
            return False, "Client not found"
        client.status = "suspended"
        self.db.update(client)
        return True, None

    def activate_client(self, client_id: str) -> Tuple[bool, str]:
        """Activate a client."""
        client = self.db.get_by_id(client_id)
        if not client:
            return False, "Client not found"
        client.status = "active"
        self.db.update(client)
        return True, None

    def get_client_with_reseller(self, client_id: str) -> Optional[Dict]:
        """Get client with reseller info."""
        client = self.db.get_by_id(client_id)
        if not client:
            return None
        result = client.to_dict()
        if client.reseller_id:
            reseller = reseller_db.get_by_id(client.reseller_id)
            if reseller:
                result["reseller"] = reseller.to_dict()
        return result

    def _generate_slug(self, name: str, exclude_id: str = None) -> str:
        """Generate a URL-friendly slug from name."""
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        existing = self.db.get_by_slug(slug)
        if existing and existing.id != exclude_id:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug


client_manager = ClientManager()
