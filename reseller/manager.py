"""Reseller management business logic."""
import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .models import Reseller, reseller_db


class ResellerManager:
    """High-level reseller operations."""

    def __init__(self):
        self.db = reseller_db

    def create_reseller(
        self,
        name: str,
        email: str,
        company: str = None,
        phone: str = None,
        parent_id: str = None,
        tier: str = "standard",
        max_clients: int = 10,
    ) -> Tuple[Optional[Reseller], str]:
        """Create a new reseller. Returns (reseller, error_message)."""
        # Validate email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return None, "Invalid email format"

        # Check email uniqueness
        existing = self.db.get_by_email(email)
        if existing:
            return None, "Email already registered"

        # Generate slug from name
        slug = self._generate_slug(name)

        # Validate parent exists if provided
        if parent_id:
            parent = self.db.get_by_id(parent_id)
            if not parent:
                return None, "Parent reseller not found"
            if parent.status != "active":
                return None, "Parent reseller is not active"

        reseller = Reseller(
            id=str(uuid.uuid4()),
            name=name,
            slug=slug,
            email=email,
            phone=phone,
            company=company,
            parent_id=parent_id,
            status="active",  # Auto-activate for now
            tier=tier,
            max_clients=max_clients,
        )
        self.db.create(reseller)
        return reseller, None

    def update_reseller(self, reseller_id: str, **kwargs) -> Tuple[Optional[Reseller], str]:
        """Update reseller fields."""
        reseller = self.db.get_by_id(reseller_id)
        if not reseller:
            return None, "Reseller not found"

        # Update allowed fields
        allowed = {"name", "email", "phone", "company", "tier", "max_clients", "status", "config"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(reseller, key, value)

        # Regenerate slug if name changed
        if "name" in kwargs:
            reseller.slug = self._generate_slug(kwargs["name"], exclude_id=reseller_id)

        self.db.update(reseller)
        return reseller, None

    def delete_reseller(self, reseller_id: str) -> Tuple[bool, str]:
        """Delete reseller (only if no children or clients)."""
        reseller = self.db.get_by_id(reseller_id)
        if not reseller:
            return False, "Reseller not found"

        # Check for children
        children = self.db.get_children(reseller_id)
        if children:
            return False, "Cannot delete reseller with children"

        # Check for clients
        client_count = self.db.count_clients(reseller_id)
        if client_count > 0:
            return False, f"Cannot delete reseller with {client_count} clients"

        self.db.delete(reseller_id)
        return True, None

    def get_reseller(self, reseller_id: str) -> Optional[Reseller]:
        """Get reseller by ID."""
        return self.db.get_by_id(reseller_id)

    def get_reseller_by_slug(self, slug: str) -> Optional[Reseller]:
        """Get reseller by slug."""
        return self.db.get_by_slug(slug)

    def list_resellers(self, parent_id: str = None, status: str = None) -> List[Reseller]:
        """List resellers."""
        return self.db.list_resellers(parent_id=parent_id, status=status)

    def get_hierarchy(self, reseller_id: str) -> Dict:
        """Get reseller with full hierarchy info."""
        reseller = self.db.get_by_id(reseller_id)
        if not reseller:
            return {}

        children = self.db.get_children(reseller_id)
        client_count = self.db.count_clients(reseller_id)

        return {
            "reseller": reseller.to_dict(),
            "children": [c.to_dict() for c in children],
            "client_count": client_count,
            "max_clients": reseller.max_clients,
            "can_add_client": self.db.can_add_client(reseller_id),
        }

    def suspend_reseller(self, reseller_id: str) -> Tuple[bool, str]:
        """Suspend a reseller."""
        reseller = self.db.get_by_id(reseller_id)
        if not reseller:
            return False, "Reseller not found"
        reseller.status = "suspended"
        self.db.update(reseller)
        return True, None

    def activate_reseller(self, reseller_id: str) -> Tuple[bool, str]:
        """Activate a reseller."""
        reseller = self.db.get_by_id(reseller_id)
        if not reseller:
            return False, "Reseller not found"
        reseller.status = "active"
        self.db.update(reseller)
        return True, None

    def _generate_slug(self, name: str, exclude_id: str = None) -> str:
        """Generate a URL-friendly slug from name."""
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        # Check uniqueness
        existing = self.db.get_by_slug(slug)
        if existing and existing.id != exclude_id:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug


reseller_manager = ResellerManager()
