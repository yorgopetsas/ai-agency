"""
Mobile App Builder
==================
Generates white-labeled React Native apps for clients.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

import logging

logger = logging.getLogger(__name__)


class MobileAppBuilder:
    """
    Generates a client-specific React Native app.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.mobile_dir = self.project_root / "mobile"
        self.clients_dir = self.mobile_dir / "clients"

    def build(self, client_id: str, branding: Dict, server_url: str = "http://localhost:5001") -> Dict:
        """
        Generate a white-labeled app for a client.

        Args:
            client_id: Client identifier
            branding: Branding config dict (primary_color, company_name, etc.)
            server_url: Backend API URL

        Returns:
            Dict with build result
        """
        try:
            output_dir = self.clients_dir / client_id

            # Clean existing
            if output_dir.exists():
                shutil.rmtree(output_dir)

            # Copy base template
            self._copy_template(output_dir)

            # Apply branding
            self._apply_branding(output_dir, client_id, branding, server_url)

            # Generate config
            self._write_config(output_dir, client_id, branding, server_url)

            file_count = sum(1 for _ in output_dir.rglob("*") if _.is_file())

            return {
                "success": True,
                "client_id": client_id,
                "path": str(output_dir),
                "files": file_count,
                "message": f"App generated at {output_dir}",
            }

        except Exception as e:
            logger.error(f"Mobile app build failed: {e}")
            return {"success": False, "error": str(e)}

    def _copy_template(self, output_dir: Path):
        """Copy base mobile template."""
        skip = {"node_modules", "clients", ".expo", "__pycache__"}
        shutil.copytree(
            self.mobile_dir, output_dir,
            ignore=shutil.ignore_patterns(*skip),
        )

    def _apply_branding(self, output_dir: Path, client_id: str, branding: Dict, server_url: str):
        """Apply client branding to the template."""
        # app.json
        app_json_path = output_dir / "app.json"
        app_json = json.loads(app_json_path.read_text())
        company = branding.get("company_name", "AI Agency")
        primary = branding.get("primary_color", "#6366f1")

        app_json["expo"]["name"] = company
        app_json["expo"]["slug"] = f"ai-agency-{client_id}"
        app_json["expo"]["ios"]["bundleIdentifier"] = f"com.amanita.{client_id}"
        app_json["expo"]["android"]["package"] = f"com.amanita.{client_id}"
        app_json["expo"]["splash"]["backgroundColor"] = primary
        app_json["expo"]["android"]["adaptiveIcon"]["backgroundColor"] = primary
        app_json_path.write_text(json.dumps(app_json, indent=2))

        # package.json
        pkg_path = output_dir / "package.json"
        pkg = json.loads(pkg_path.read_text())
        pkg["name"] = f"ai-agency-{client_id}"
        pkg_path.write_text(json.dumps(pkg, indent=2))

        # Client branding file
        branding_ts = f"""
import {{ applyBranding }} from '../theme';

export const clientBranding = {{
  primary_color: '{primary}',
  secondary_color: '{branding.get("secondary_color", "#8b5cf6")}',
  accent_color: '{branding.get("accent_color", "#06b6d4")}',
  company_name: '{company}',
}};
"""
        (output_dir / "src" / "theme" / "clientBranding.ts").write_text(branding_ts)

    def _write_config(self, output_dir: Path, client_id: str, branding: Dict, server_url: str):
        """Write client config JSON."""
        config = {
            "clientId": client_id,
            "companyName": branding.get("company_name", "AI Agency"),
            "theme": {
                "primary": branding.get("primary_color", "#6366f1"),
                "secondary": branding.get("secondary_color", "#8b5cf6"),
                "accent": branding.get("accent_color", "#06b6d4"),
            },
            "serverUrl": server_url,
            "generatedAt": __import__("datetime").datetime.now().isoformat(),
        }
        config_dir = output_dir / "config"
        config_dir.mkdir(exist_ok=True)
        (config_dir / "client.json").write_text(json.dumps(config, indent=2))

    def list_apps(self) -> list:
        """List all generated client apps."""
        if not self.clients_dir.exists():
            return []
        return [
            d.name for d in self.clients_dir.iterdir()
            if d.is_dir() and (d / "config" / "client.json").exists()
        ]

    def get_app(self, client_id: str) -> Optional[Dict]:
        """Get info about a generated app."""
        config_file = self.clients_dir / client_id / "config" / "client.json"
        if config_file.exists():
            return json.loads(config_file.read_text())
        return None


mobile_app_builder = MobileAppBuilder()
