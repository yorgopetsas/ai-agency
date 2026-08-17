"""Branding management business logic."""
import os
import re
import uuid
import base64
from typing import Optional, Dict, Tuple
from .models import ClientBranding, branding_db


# Allowed themes
THEMES = ["light", "dark", "auto"]

# Allowed font families
FONTS = ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat", "Poppins", "Source Sans Pro"]

# Logo storage path
LOGO_DIR = os.path.join(os.path.dirname(__file__), "..", "server", "static", "images", "logos")


def _validate_color(color: str) -> bool:
    """Validate hex color."""
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


class BrandingManager:
    """High-level branding operations."""

    def __init__(self):
        self.db = branding_db

    def get_branding(self, client_id: str) -> Optional[ClientBranding]:
        """Get branding for a client."""
        return self.db.get(client_id)

    def get_by_domain(self, domain: str) -> Optional[ClientBranding]:
        """Get branding by custom domain."""
        return self.db.get_by_domain(domain)

    def update_branding(self, client_id: str, **kwargs) -> Tuple[Optional[ClientBranding], str]:
        """Update branding fields."""
        branding = self.db.get(client_id)
        if not branding:
            # Create with defaults
            branding = ClientBranding(client_id=client_id)

        # Validate colors
        for color_field in ("primary_color", "secondary_color", "accent_color"):
            if color_field in kwargs:
                val = kwargs[color_field]
                if val and not _validate_color(val):
                    return None, f"Invalid {color_field}: must be #RRGGBB hex"

        # Validate theme
        if "theme" in kwargs and kwargs["theme"] not in THEMES:
            return None, f"Invalid theme. Allowed: {', '.join(THEMES)}"

        # Validate font
        if "font_family" in kwargs and kwargs["font_family"] not in FONTS:
            return None, f"Invalid font. Allowed: {', '.join(FONTS)}"

        # Validate domain uniqueness
        if "custom_domain" in kwargs and kwargs["custom_domain"]:
            existing = self.db.get_by_domain(kwargs["custom_domain"])
            if existing and existing.client_id != client_id:
                return None, "Domain already in use by another client"

        # Apply updates
        allowed = {
            "logo_url", "primary_color", "secondary_color", "accent_color",
            "font_family", "favicon_url", "custom_domain", "welcome_message",
            "footer_text", "theme",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(branding, key, value)

        self.db.create_or_update(branding)
        return branding, None

    def save_logo(self, client_id: str, file_data: bytes, filename: str) -> Tuple[Optional[str], str]:
        """Save logo file and return URL."""
        os.makedirs(LOGO_DIR, exist_ok=True)

        ext = os.path.splitext(filename)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".svg", ".webp"):
            return None, "Invalid file type. Use PNG, JPG, SVG, or WebP"

        safe_name = f"{client_id}_logo{ext}"
        path = os.path.join(LOGO_DIR, safe_name)
        with open(path, "wb") as f:
            f.write(file_data)

        url = f"/static/images/logos/{safe_name}"
        self.update_branding(client_id, logo_url=url)
        return url, None

    def get_preview(self, client_id: str) -> Dict:
        """Get branding as CSS preview data."""
        branding = self.db.get(client_id)
        if not branding:
            branding = ClientBranding(client_id=client_id)

        return {
            "client_id": client_id,
            "colors": {
                "primary": branding.primary_color,
                "secondary": branding.secondary_color,
                "accent": branding.accent_color,
            },
            "font": branding.font_family,
            "theme": branding.theme,
            "logo_url": branding.logo_url,
            "favicon_url": branding.favicon_url,
            "welcome_message": branding.welcome_message,
            "footer_text": branding.footer_text,
            "custom_domain": branding.custom_domain,
            "css_variables": {
                "--color-primary": branding.primary_color,
                "--color-secondary": branding.secondary_color,
                "--color-accent": branding.accent_color,
                "--font-family": branding.font_family,
            },
        }

    def delete_branding(self, client_id: str) -> Tuple[bool, str]:
        """Reset branding to defaults."""
        branding = self.db.get(client_id)
        if not branding:
            return False, "No branding found"
        self.db.delete(client_id)
        return True, None


branding_manager = BrandingManager()
