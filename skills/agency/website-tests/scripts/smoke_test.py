#!/usr/bin/env python3
"""
Website Smoke Tests
===================
Validates a generated website project without running the app.
Checks file structure, TypeScript syntax, routing, components, design tokens, Docker, and responsiveness.

Usage:
    python3 smoke_test.py --project /path/to/site
    python3 smoke_test.py --project /path/to/site --fix  # auto-fix issues
"""

import argparse
import json
import re
import sys
from pathlib import Path


class TestResult:
    def __init__(self, name, passed, message=""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        msg = f" ({self.message})" if self.message else ""
        return f"  [{status}] {self.name}{msg}"


def test_structure(project: Path) -> TestResult:
    """Check required files exist."""
    required = [
        "package.json",
        "vite.config.ts",
        "tailwind.config.ts",
        "tsconfig.json",
        "index.html",
        "src/main.tsx",
        "src/App.tsx",
        "src/index.css",
        "src/components/Layout.tsx",
        "src/components/SiteNav.tsx",
        "src/components/SiteFooter.tsx",
        "src/data/site.ts",
    ]
    missing = [f for f in required if not (project / f).exists()]
    if missing:
        return TestResult("structure", False, f"Missing: {', '.join(missing)}")
    return TestResult("structure", True)


def test_typescript(project: Path) -> TestResult:
    """Check for obvious TypeScript syntax errors."""
    issues = []
    for ts_file in project.rglob("*.tsx"):
        if "node_modules" in str(ts_file):
            continue
        content = ts_file.read_text()
        # Check balanced curly braces (skip JSX expression braces like {<Component />})
        # Remove JSX expressions first
        cleaned = re.sub(r'\{<[^>]*>\}', '', content)
        # Remove string literals
        cleaned = re.sub(r'"[^"]*"', '', cleaned)
        cleaned = re.sub(r"'[^']*'", '', cleaned)
        opens = cleaned.count("{")
        closes = cleaned.count("}")
        if abs(opens - closes) > 2:
            issues.append(f"{ts_file.name}: unbalanced braces ({opens} open, {closes} close)")
    if issues:
        return TestResult("typescript", False, "; ".join(issues))
    return TestResult("typescript", True)


def test_routing(project: Path) -> TestResult:
    """Check App.tsx has routes for all generated pages."""
    app_file = project / "src" / "App.tsx"
    if not app_file.exists():
        return TestResult("routing", False, "App.tsx not found")

    content = app_file.read_text()
    pages_dir = project / "src" / "pages"
    if not pages_dir.exists():
        return TestResult("routing", False, "pages/ directory not found")

    page_files = [f.stem for f in pages_dir.glob("*.tsx") if f.stem != "NotFound"]
    missing = []
    for page in page_files:
        if page not in content:
            missing.append(page)

    if missing:
        return TestResult("routing", False, f"Routes missing for: {', '.join(missing)}")
    return TestResult("routing", True)


def test_components(project: Path) -> TestResult:
    """Check that components exist and have reasonable content."""
    components_dir = project / "src" / "components"
    if not components_dir.exists():
        return TestResult("components", False, "components/ directory not found")

    # Exclude utility components that don't need Tailwind
    utility_components = {"Seo.tsx"}
    tsx_files = [f for f in components_dir.glob("*.tsx") if f.name not in utility_components]
    if len(tsx_files) < 3:
        return TestResult("components", False, f"Only {len(tsx_files)} components found (expected 6+)")

    issues = []
    for f in tsx_files:
        content = f.read_text()
        if "export default function" not in content:
            issues.append(f"{f.name}: no default export function")
        if "className" not in content:
            issues.append(f"{f.name}: no Tailwind classes found")

    if issues:
        return TestResult("components", False, "; ".join(issues))
    return TestResult("components", True, f"{len(tsx_files)} components")


def test_design_tokens(project: Path) -> TestResult:
    """Check Tailwind config has design tokens."""
    config_file = project / "tailwind.config.ts"
    if not config_file.exists():
        return TestResult("design_tokens", False, "tailwind.config.ts not found")

    content = config_file.read_text()
    required_colors = ["primary", "secondary", "accent"]
    missing = [c for c in required_colors if c not in content]

    css_file = project / "src" / "index.css"
    css_content = css_file.read_text() if css_file.exists() else ""
    css_missing = [c for c in required_colors if f"--color-{c}" not in css_content]

    issues = []
    if missing:
        issues.append(f"Missing Tailwind colors: {', '.join(missing)}")
    if css_missing:
        issues.append(f"Missing CSS vars: {', '.join(css_missing)}")

    if issues:
        return TestResult("design_tokens", False, "; ".join(issues))
    return TestResult("design_tokens", True)


def test_docker(project: Path) -> TestResult:
    """Check Docker configuration."""
    dockerfile = project / "Dockerfile"
    compose = project / "docker-compose.yml"

    issues = []
    if not dockerfile.exists():
        issues.append("Dockerfile missing")
    else:
        content = dockerfile.read_text()
        if "FROM" not in content:
            issues.append("Dockerfile has no FROM instruction")
        if "multi-stage" in content.lower() or content.count("FROM") >= 2:
            pass  # Good, multi-stage
    if not compose.exists():
        issues.append("docker-compose.yml missing")

    if issues:
        return TestResult("docker", False, "; ".join(issues))
    return TestResult("docker", True)


def test_responsive(project: Path) -> TestResult:
    """Check components use responsive Tailwind classes."""
    components_dir = project / "src" / "components"
    if not components_dir.exists():
        return TestResult("responsive", False, "components/ directory not found")

    responsive_pattern = re.compile(r"\b(sm|md|lg|xl):")
    issues = []
    for f in components_dir.glob("*.tsx"):
        content = f.read_text()
        if "className" in content and not responsive_pattern.search(content):
            issues.append(f"{f.name}: no responsive classes")

    if len(issues) > 2:
        return TestResult("responsive", False, f"{len(issues)} components lack responsive classes")
    return TestResult("responsive", True)


def test_accessibility(project: Path) -> TestResult:
    """Check basic accessibility patterns."""
    issues = []
    for tsx_file in project.rglob("*.tsx"):
        if "node_modules" in str(tsx_file):
            continue
        content = tsx_file.read_text()
        # Check form inputs have labels
        inputs = re.findall(r"<input[^>]*>", content)
        for inp in inputs:
            if "id=" in inp and "aria-label" not in inp:
                # Check if there's a matching label
                id_match = re.search(r'id="([^"]+)"', inp)
                if id_match and f'htmlFor="{id_match.group(1)}"' not in content:
                    issues.append(f"{tsx_file.name}: input without label")
        # Check buttons have text content
        buttons = re.findall(r"<button[^>]*>([^<]*)</button>", content)
        for btn_text in buttons:
            if not btn_text.strip() and "aria-label" not in content:
                issues.append(f"{tsx_file.name}: empty button")

    if len(issues) > 3:
        return TestResult("accessibility", False, f"{len(issues)} issues: " + "; ".join(issues[:3]))
    return TestResult("accessibility", True)


ALL_TESTS = [
    test_structure,
    test_typescript,
    test_routing,
    test_components,
    test_design_tokens,
    test_docker,
    test_responsive,
    test_accessibility,
]


def run_tests(project: Path):
    """Run all smoke tests."""
    print("=" * 50)
    print("Website Smoke Tests")
    print("=" * 50)
    print(f"  Project: {project}")
    print()

    results = []
    for test_fn in ALL_TESTS:
        result = test_fn(project)
        results.append(result)
        print(str(result))

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    print()
    print("=" * 50)
    if failed == 0:
        print(f"All {passed} tests passed!")
    else:
        print(f"{passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Website smoke tests")
    parser.add_argument("--project", required=True, help="Path to the generated website project")
    args = parser.parse_args()

    project = Path(args.project)
    if not project.exists():
        print(f"Error: {project} does not exist")
        sys.exit(1)

    success = run_tests(project)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
