#!/usr/bin/env python3
"""
Website Generator
=================
End-to-end orchestration: design → scaffold → components → Docker.

Usage:
    python3 generate.py --name "acme-saas" --industry "saas" --pages "home,about,pricing,contact"
"""

import argparse
import importlib.util
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent  # skills/agency/


def load_module(name, script_path):
    """Dynamically load a Python module from a script path."""
    spec = importlib.util.spec_from_file_location(name, script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def step_design(industry):
    """Step 1: Get design system for the industry."""
    print("  [1/4] Design system: {}".format(industry))
    search_script = SKILLS_DIR / "ui-ux-design" / "scripts" / "search.py"
    mod = load_module("ui_ux_search", search_script)
    result = mod.search_industry(industry)
    if result:
        palette = result.get("palette", {})
        style = result.get("style", {})
        font = result.get("font", {})
        print("        Palette: {}".format(palette.get("name", "default")))
        print("        Style: {}".format(style.get("name", "default")))
        print("        Font: {}".format(font.get("name", "default")))
    else:
        print("        Using defaults for '{}'".format(industry))
    return result


def step_scaffold(name, industry, pages, output_dir):
    """Step 2: Scaffold the React project."""
    print("  [2/4] Scaffolding project: {}".format(name))
    scaffold_script = SKILLS_DIR / "scaffold-react-app" / "scripts" / "scaffold.py"
    mod = load_module("scaffold", scaffold_script)
    mod.scaffold(name, industry, pages, output_dir)
    print("        Created at: {}".format(output_dir))


# Component mappings: page → components to generate
PAGE_COMPONENTS = {
    "home": [
        ("hero", "HomeHero"),
        ("feature-card", "HomeFeatures"),
        ("testimonial", "HomeTestimonials"),
        ("cta", "HomeCta"),
    ],
    "about": [],
    "pricing": [
        ("pricing", "PricingTable"),
    ],
    "contact": [
        ("contact-form", "ContactForm"),
    ],
}


def step_components(pages, output_dir):
    """Step 3: Generate components for each page."""
    print("  [3/4] Generating components")
    gen_script = SKILLS_DIR / "create-component" / "scripts" / "generate.py"
    mod = load_module("create_component", gen_script)

    components_dir = output_dir / "src" / "components"
    count = 0
    for page in pages:
        comps = PAGE_COMPONENTS.get(page, [])
        for comp_type, comp_name in comps:
            mod.generate(comp_type, comp_name, components_dir)
            count += 1
    print("        Generated {} components".format(count))


def step_docker(name, output_dir):
    """Step 4: Add Docker configuration."""
    print("  [4/4] Containerizing")
    docker_script = SKILLS_DIR / "containerize-docker" / "scripts" / "generate.py"
    mod = load_module("containerize_docker", docker_script)
    mod.generate_react(name, 3000, output_dir)
    print("        Added Dockerfile + docker-compose.yml")


def generate(name, industry, pages, output_base):
    """Run the full website generation pipeline."""
    output_dir = Path(output_base) / name

    print("=" * 50)
    print("Website Generator")
    print("=" * 50)
    print("  Name: {}".format(name))
    print("  Industry: {}".format(industry))
    print("  Pages: {}".format(", ".join(pages)))
    print("  Output: {}".format(output_dir))
    print()

    # Step 1: Design
    step_design(industry)
    print()

    # Step 2: Scaffold
    step_scaffold(name, industry, pages, output_dir)
    print()

    # Step 3: Components
    step_components(pages, output_dir)
    print()

    # Step 4: Docker
    step_docker(name, output_dir)
    print()

    # Summary
    print("=" * 50)
    print("Done!")
    print("=" * 50)
    print("  Project: {}".format(output_dir))
    print()
    print("  Next steps:")
    print("    cd {}".format(name))
    print("    npm install")
    print("    npm run dev          # development")
    print("    docker compose up    # production")
    print()
    print("  Edit src/pages/HomePage.tsx to customize content.")


def main():
    parser = argparse.ArgumentParser(description="Generate a complete website")
    parser.add_argument("--name", required=True, help="Project name (e.g., 'acme-saas')")
    parser.add_argument("--industry", default="saas", help="Industry for design defaults")
    parser.add_argument("--pages", default="home,about,pricing,contact",
                        help="Comma-separated page names")
    parser.add_argument("--output", default=".", help="Base output directory")
    args = parser.parse_args()

    pages = [p.strip() for p in args.pages.split(",")]
    generate(args.name, args.industry, pages, args.output)


if __name__ == "__main__":
    main()
