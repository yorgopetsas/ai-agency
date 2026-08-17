"""
Client Website Builder Engine
=============================
Generates a custom React + Tailwind website for each client using the
existing agency skill pipeline, then applies their branding.

Flow:
1. Load client branding (colors, font, theme, name, industry)
2. Scaffold React project via scaffold-react-app skill
3. Generate components via create-component skill
4. Apply branding: inject colors/font into tailwind.config.ts + CSS
5. Store output in server/data/websites/{client_id}/
"""

import os
import json
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Paths
SKILLS_DIR = Path(__file__).parent.parent / "skills" / "agency"
WEBSITES_DIR = Path(__file__).parent.parent / "server" / "data" / "websites"

# Default pages per industry
INDUSTRY_PAGES = {
    "healthcare": ["home", "about", "services", "contact"],
    "finance": ["home", "about", "pricing", "contact"],
    "ecommerce": ["home", "about", "pricing", "contact"],
    "education": ["home", "about", "courses", "contact"],
    "technology": ["home", "about", "pricing", "contact"],
    "real_estate": ["home", "about", "listings", "contact"],
    "marketing": ["home", "about", "services", "contact"],
    "legal": ["home", "about", "services", "contact"],
    "manufacturing": ["home", "about", "services", "contact"],
    "other": ["home", "about", "pricing", "contact"],
}


def _load_skill_module(name: str, script_path: Path):
    """Dynamically load a Python skill module."""
    spec = importlib.util.spec_from_file_location(name, str(script_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #RRGGBB to (r, g, b)."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _generate_tailwind_config(branding: Dict, industry: str) -> str:
    """Generate tailwind.config.ts with client branding colors."""
    primary = branding.get("primary_color", "#6366F1")
    secondary = branding.get("secondary_color", "#8B5CF6")
    accent = branding.get("accent_color", "#22D3EE")
    font = branding.get("font_family", "Inter")

    p = _hex_to_rgb(primary)
    s = _hex_to_rgb(secondary)
    a = _hex_to_rgb(accent)

    return f'''import type {{ Config }} from 'tailwindcss'

export default {{
  content: ['./index.html', './src/**/*.{{
js,ts,jsx,tsx}}'],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          50: 'rgb({min(p[0]+200,255)}, {min(p[1]+200,255)}, {min(p[2]+200,255)})',
          100: 'rgb({min(p[0]+170,255)}, {min(p[1]+170,255)}, {min(p[2]+170,255)})',
          200: 'rgb({min(p[0]+130,255)}, {min(p[1]+130,255)}, {min(p[2]+130,255)})',
          300: 'rgb({min(p[0]+90,255)}, {min(p[1]+90,255)}, {min(p[2]+90,255)})',
          400: 'rgb({min(p[0]+40,255)}, {min(p[1]+40,255)}, {min(p[2]+40,255)})',
          500: '{primary}',
          600: 'rgb({max(p[0]-30,0)}, {max(p[1]-30,0)}, {max(p[2]-30,0)})',
          700: 'rgb({max(p[0]-60,0)}, {max(p[1]-60,0)}, {max(p[2]-60,0)})',
          800: 'rgb({max(p[0]-90,0)}, {max(p[1]-90,0)}, {max(p[2]-90,0)})',
          900: 'rgb({max(p[0]-120,0)}, {max(p[1]-120,0)}, {max(p[2]-120,0)})',
        }},
        secondary: {{
          500: '{secondary}',
        }},
        accent: {{
          500: '{accent}',
        }},
      }},
      fontFamily: {{
        heading: ['{font}', 'system-ui', 'sans-serif'],
        body: ['{font}', 'system-ui', 'sans-serif'],
      }},
    }},
  }},
  plugins: [],
}}
'''


def _generate_index_css(branding: Dict) -> str:
    """Generate index.css with client branding as CSS custom properties."""
    primary = branding.get("primary_color", "#6366F1")
    secondary = branding.get("secondary_color", "#8B5CF6")
    accent = branding.get("accent_color", "#22D3EE")
    font = branding.get("font_family", "Inter")

    return f'''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-accent: {accent};
  --font-family: '{font}', system-ui, sans-serif;
}}

body {{
  font-family: var(--font-family);
}}

.bg-primary {{
  background-color: var(--color-primary);
}}

.text-primary {{
  color: var(--color-primary);
}}

.border-primary {{
  border-color: var(--color-primary);
}}
'''


def _generate_site_data(client_name: str, industry: str, branding: Dict) -> str:
    """Generate site.ts data file with client content."""
    welcome = branding.get("welcome_message", f"Welcome to {client_name}")
    footer = branding.get("footer_text", f"© 2026 {client_name}. All rights reserved.")

    return f'''export const siteConfig = {{
  name: "{client_name}",
  industry: "{industry}",
  welcomeMessage: "{welcome}",
  footerText: "{footer}",
  primaryColor: "{branding.get('primary_color', '#6366F1')}",
  secondaryColor: "{branding.get('secondary_color', '#8B5CF6')}",
  accentColor: "{branding.get('accent_color', '#22D3EE')}",
  font: "{branding.get('font_family', 'Inter')}",
  theme: "{branding.get('theme', 'light')}",
}}

export const navigation = [
  {{ name: 'Home', href: '/' }},
  {{ name: 'About', href: '/about' }},
  {{ name: 'Pricing', href: '/pricing' }},
  {{ name: 'Contact', href: '/contact' }},
]

export const features = [
  {{
    icon: '🤖',
    title: 'AI-Powered',
    description: 'Leverage cutting-edge AI technology to automate your workflows.',
  }},
  {{
    icon: '⚡',
    title: 'Fast & Efficient',
    description: 'Get results in minutes, not hours. Streamlined for productivity.',
  }},
  {{
    icon: '🔒',
    title: 'Secure & Private',
    description: 'Your data stays yours. Enterprise-grade security built in.',
  }},
]

export const testimonials = [
  {{
    quote: "This platform transformed how we handle operations. Highly recommended!",
    author: "Sarah Chen",
    role: "CTO, TechCorp",
  }},
  {{
    quote: "The AI agents saved us 20+ hours per week. Game changer.",
    author: "Marcus Johnson",
    role: "CEO, StartupXYZ",
  }},
]

export const pricingPlans = [
  {{
    name: "Starter",
    price: "$29",
    period: "/month",
    features: ["5 AI Agents", "1,000 tasks/mo", "Email support", "Basic analytics"],
    cta: "Get Started",
    popular: false,
  }},
  {{
    name: "Pro",
    price: "$99",
    period: "/month",
    features: ["25 AI Agents", "10,000 tasks/mo", "Priority support", "Advanced analytics", "Custom branding"],
    cta: "Start Free Trial",
    popular: true,
  }},
  {{
    name: "Enterprise",
    price: "Custom",
    period: "",
    features: ["Unlimited agents", "Unlimited tasks", "Dedicated support", "SLA", "White-label"],
    cta: "Contact Sales",
    popular: false,
  }},
]
'''


class WebsiteBuilder:
    """Builds a custom website for a client using the skill pipeline."""

    def __init__(self):
        self.output_base = str(WEBSITES_DIR)
        os.makedirs(self.output_base, exist_ok=True)

    def build(
        self,
        client_id: str,
        client_name: str,
        industry: str = "technology",
        branding: Dict = None,
        pages: list = None,
    ) -> Dict:
        """
        Build a complete website for a client.

        Args:
            client_id: Client identifier
            client_name: Display name for the site
            industry: Industry for default design
            branding: Branding overrides (colors, font, theme)
            pages: List of pages to generate

        Returns:
            Dict with build result
        """
        branding = branding or {}
        pages = pages or INDUSTRY_PAGES.get(industry, INDUSTRY_PAGES["other"])
        output_dir = Path(self.output_base) / client_id

        result = {
            "client_id": client_id,
            "client_name": client_name,
            "industry": industry,
            "pages": pages,
            "output_dir": str(output_dir),
            "steps": [],
            "success": False,
        }

        try:
            # Step 1: Scaffold React project
            self._step_scaffold(client_name, industry, pages, output_dir)
            result["steps"].append("scaffolded")

            # Step 2: Generate components
            self._step_components(pages, output_dir)
            result["steps"].append("components_generated")

            # Step 3: Apply branding
            self._step_branding(client_name, industry, branding, output_dir)
            result["steps"].append("branding_applied")

            # Step 4: Add Docker support
            self._step_docker(client_name, output_dir)
            result["steps"].append("docker_added")

            result["success"] = True
            logger.info(f"Built website for {client_id} at {output_dir}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Website build failed for {client_id}: {e}")

        return result

    def _step_scaffold(self, name: str, industry: str, pages: list, output_dir: Path):
        """Scaffold the React project."""
        scaffold_script = SKILLS_DIR / "scaffold-react-app" / "scripts" / "scaffold.py"
        mod = _load_skill_module("scaffold", scaffold_script)
        mod.scaffold(name, industry, pages, output_dir)
        logger.info(f"Scaffolded project at {output_dir}")

    def _step_components(self, pages: list, output_dir: Path):
        """Generate components for each page."""
        gen_script = SKILLS_DIR / "create-component" / "scripts" / "generate.py"
        mod = _load_skill_module("create_component", gen_script)

        PAGE_COMPONENTS = {
            "home": [("hero", "HomeHero"), ("feature-card", "HomeFeatures"),
                     ("testimonial", "HomeTestimonials"), ("cta", "HomeCta")],
            "about": [],
            "pricing": [("pricing", "PricingTable")],
            "contact": [("contact-form", "ContactForm")],
            "services": [("feature-card", "Services")],
            "courses": [("feature-card", "Courses")],
            "listings": [("feature-card", "Listings")],
        }

        components_dir = output_dir / "src" / "components"
        count = 0
        for page in pages:
            comps = PAGE_COMPONENTS.get(page, [])
            for comp_type, comp_name in comps:
                mod.generate(comp_type, comp_name, components_dir)
                count += 1
        logger.info(f"Generated {count} components")

    def _step_branding(self, name: str, industry: str, branding: Dict, output_dir: Path):
        """Apply client branding to the generated project."""
        # Overwrite tailwind.config.ts
        tw_path = output_dir / "tailwind.config.ts"
        tw_path.write_text(_generate_tailwind_config(branding, industry))

        # Overwrite index.css
        css_path = output_dir / "src" / "index.css"
        css_path.write_text(_generate_index_css(branding))

        # Overwrite site data
        data_path = output_dir / "src" / "data" / "site.ts"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(_generate_site_data(name, industry, branding))

        # Update index.html title
        html_path = output_dir / "index.html"
        if html_path.exists():
            content = html_path.read_text()
            content = content.replace(
                "<title>Vite + React + TS</title>",
                f"<title>{name}</title>"
            )
            html_path.write_text(content)

        logger.info(f"Applied branding to {output_dir}")

    def _step_docker(self, name: str, output_dir: Path):
        """Add Docker configuration."""
        docker_script = SKILLS_DIR / "containerize-docker" / "scripts" / "generate.py"
        mod = _load_skill_module("containerize_docker", docker_script)
        mod.generate_react(name, 3000, output_dir)
        logger.info(f"Added Docker config to {output_dir}")

    def get_website_path(self, client_id: str) -> Optional[str]:
        """Get the path to a client's built website."""
        path = Path(self.output_base) / client_id
        if path.exists():
            return str(path)
        return None

    def list_websites(self) -> Dict[str, Dict]:
        """List all built client websites."""
        websites = {}
        if WEBSITES_DIR.exists():
            for entry in WEBSITES_DIR.iterdir():
                if entry.is_dir():
                    pkg = entry / "package.json"
                    websites[entry.name] = {
                        "client_id": entry.name,
                        "path": str(entry),
                        "has_package_json": pkg.exists(),
                    }
        return websites

    def delete_website(self, client_id: str) -> bool:
        """Delete a client's website."""
        import shutil
        path = Path(self.output_base) / client_id
        if path.exists():
            shutil.rmtree(path)
            logger.info(f"Deleted website for {client_id}")
            return True
        return False
