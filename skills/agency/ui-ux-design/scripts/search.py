#!/usr/bin/env python3
"""
UI/UX Design Search Tool
========================
Search and retrieve design system components: styles, palettes, fonts, UX guidelines.

Usage:
    python3 search.py --style glassmorphism
    python3 search.py --palette "saas-tech"
    python3 search.py --font "modern"
    python3 search.py --ux "navigation"
    python3 search.py --industry "healthcare"
    python3 search.py --generate --industry "fintech" --style "professional"
"""

import argparse
import json
import sys
from pathlib import Path

# ── Design System Database ──────────────────────────────────────────

STYLES = {
    "glassmorphism": {
        "name": "Glassmorphism",
        "description": "Frosted glass effect with blur, transparency, and subtle borders",
        "css": {
            "background": "rgba(255, 255, 255, 0.15)",
            "backdrop-filter": "blur(12px)",
            "border": "1px solid rgba(255, 255, 255, 0.2)",
            "border-radius": "16px",
            "box-shadow": "0 8px 32px rgba(0, 0, 0, 0.1)"
        },
        "best_for": ["dashboards", "creative agencies", "music", "portfolio"],
        "avoid_for": ["enterprise", "healthcare", "government"]
    },
    "professional": {
        "name": "Professional",
        "description": "Clean, corporate design with subtle shadows and structured layouts",
        "css": {
            "background": "#FFFFFF",
            "border": "1px solid #E5E7EB",
            "border-radius": "8px",
            "box-shadow": "0 1px 3px rgba(0, 0, 0, 0.1)"
        },
        "best_for": ["B2B SaaS", "consulting", "finance", "enterprise"],
        "avoid_for": ["creative agencies", "gaming", "music"]
    },
    "minimalist": {
        "name": "Minimalist",
        "description": "Maximum whitespace, thin typography, no decorative elements",
        "css": {
            "background": "#FFFFFF",
            "border": "none",
            "border-radius": "0",
            "box-shadow": "none"
        },
        "best_for": ["architecture", "luxury", "photography", "editorial"],
        "avoid_for": ["e-commerce", "education", "children"]
    },
    "neumorphism": {
        "name": "Neumorphism",
        "description": "Soft UI with inner/outer shadows creating a raised/forged effect",
        "css": {
            "background": "#E0E5EC",
            "border-radius": "20px",
            "box-shadow": "8px 8px 16px #b8bec7, -8px -8px 16px #ffffff"
        },
        "best_for": ["fitness", "productivity", "weather", "calculator apps"],
        "avoid_for": ["content-heavy sites", "e-commerce", "enterprise"]
    },
    "bold": {
        "name": "Bold",
        "description": "High contrast, large typography, strong visual hierarchy",
        "css": {
            "background": "#000000",
            "color": "#FFFFFF",
            "font-weight": "900",
            "letter-spacing": "-0.02em"
        },
        "best_for": ["creative agencies", "fashion", "music", "sports"],
        "avoid_for": ["healthcare", "finance", "education"]
    },
    "flat": {
        "name": "Flat Design",
        "description": "No shadows or gradients, solid colors, simple shapes",
        "css": {
            "background": "#FFFFFF",
            "border": "none",
            "border-radius": "4px",
            "box-shadow": "none"
        },
        "best_for": ["SaaS", "startups", "mobile-first", "dashboards"],
        "avoid_for": ["luxury", "editorial", "photography"]
    },
    "material": {
        "name": "Material Design",
        "description": "Google's design system with elevation, ripple effects, and grid",
        "css": {
            "background": "#FFFFFF",
            "border-radius": "12px",
            "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
            "transition": "box-shadow 0.2s"
        },
        "best_for": ["Android apps", "enterprise", "education", "productivity"],
        "avoid_for": ["creative agencies", "luxury", "portfolio"]
    },
    "brutalist": {
        "name": "Brutalism",
        "description": "Raw, unpolished, intentionally rough with exposed structure",
        "css": {
            "background": "#FFFFFF",
            "border": "3px solid #000000",
            "border-radius": "0",
            "font-family": "monospace"
        },
        "best_for": ["creative agencies", "art", "activism", "experimental"],
        "avoid_for": ["enterprise", "healthcare", "finance", "e-commerce"]
    },
    "artisan": {
        "name": "Artisan",
        "description": "Handcrafted feel with organic shapes, warm tones, and texture",
        "css": {
            "background": "#FDF6E3",
            "border-radius": "8px",
            "font-family": "Georgia, serif",
            "color": "#3C2415"
        },
        "best_for": ["food & beverage", "craft", "organic", "boutique"],
        "avoid_for": ["tech", "SaaS", "enterprise"]
    },
    "luxury": {
        "name": "Luxury",
        "description": "Dark backgrounds, gold/champagne accents, elegant typography",
        "css": {
            "background": "#0A0A0A",
            "color": "#F5F5F5",
            "border": "1px solid #C9A96E",
            "font-family": "Playfair Display, serif"
        },
        "best_for": ["luxury brands", "high-end services", "jewelry", "hotels"],
        "avoid_for": ["SaaS", "startups", "education"]
    }
}

PALETTES = {
    "saas-tech": {
        "name": "SaaS Tech",
        "primary": "#2563EB",
        "secondary": "#475569",
        "accent": "#06B6D4",
        "background": "#FFFFFF",
        "surface": "#F8FAFC",
        "text_primary": "#0F172A",
        "text_secondary": "#64748B",
        "text_muted": "#94A3B8",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#3B82F6"
    },
    "saas-indigo": {
        "name": "SaaS Indigo",
        "primary": "#4F46E5",
        "secondary": "#64748B",
        "accent": "#7C3AED",
        "background": "#FFFFFF",
        "surface": "#F8FAFC",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "success": "#059669",
        "warning": "#D97706",
        "error": "#DC2626",
        "info": "#6366F1"
    },
    "healthcare-teal": {
        "name": "Healthcare Teal",
        "primary": "#0D9488",
        "secondary": "#6B7280",
        "accent": "#059669",
        "background": "#FFFFFF",
        "surface": "#F0FDFA",
        "text_primary": "#134E4A",
        "text_secondary": "#6B7280",
        "text_muted": "#9CA3AF",
        "success": "#059669",
        "warning": "#D97706",
        "error": "#E11D48",
        "info": "#0891B2"
    },
    "finance-navy": {
        "name": "Finance Navy",
        "primary": "#1E3A5F",
        "secondary": "#64748B",
        "accent": "#D97706",
        "background": "#FFFFFF",
        "surface": "#F1F5F9",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "success": "#059669",
        "warning": "#D97706",
        "error": "#DC2626",
        "info": "#2563EB"
    },
    "creative-dark": {
        "name": "Creative Dark",
        "primary": "#D946EF",
        "secondary": "#A1A1AA",
        "accent": "#84CC16",
        "background": "#18181B",
        "surface": "#27272A",
        "text_primary": "#FAFAFA",
        "text_secondary": "#A1A1AA",
        "text_muted": "#71717A",
        "success": "#22C55E",
        "warning": "#EAB308",
        "error": "#EF4444",
        "info": "#38BDF8"
    },
    "education-blue": {
        "name": "Education Blue",
        "primary": "#2563EB",
        "secondary": "#475569",
        "accent": "#7C3AED",
        "background": "#FFFFFF",
        "surface": "#EFF6FF",
        "text_primary": "#1E293B",
        "text_secondary": "#64748B",
        "text_muted": "#94A3B8",
        "success": "#16A34A",
        "warning": "#D97706",
        "error": "#DC2626",
        "info": "#2563EB"
    },
    "ecommerce-warm": {
        "name": "E-commerce Warm",
        "primary": "#EA580C",
        "secondary": "#525252",
        "accent": "#DC2626",
        "background": "#FFFFFF",
        "surface": "#FAFAF9",
        "text_primary": "#1C1917",
        "text_secondary": "#78716C",
        "text_muted": "#A8A29E",
        "success": "#16A34A",
        "warning": "#CA8A04",
        "error": "#DC2626",
        "info": "#2563EB"
    },
    "organic-green": {
        "name": "Organic Green",
        "primary": "#15803D",
        "secondary": "#71717A",
        "accent": "#A16207",
        "background": "#F0FDF4",
        "surface": "#FFFFFF",
        "text_primary": "#14532D",
        "text_secondary": "#52525B",
        "text_muted": "#A1A1AA",
        "success": "#15803D",
        "warning": "#A16207",
        "error": "#B91C1C",
        "info": "#0369A1"
    }
}

FONTS = {
    "modern": {
        "name": "Modern Clean",
        "heading": "Inter",
        "body": "Inter",
        "mono": "JetBrains Mono",
        "weights": {"heading": "700", "body": "400"},
        "best_for": ["SaaS", "tech", "startups"]
    },
    "editorial": {
        "name": "Editorial Classic",
        "heading": "Playfair Display",
        "body": "Source Sans 3",
        "mono": "Source Code Pro",
        "weights": {"heading": "600", "body": "400"},
        "best_for": ["news", "magazine", "blog", "editorial"]
    },
    "corporate": {
        "name": "Corporate Trust",
        "heading": "Plus Jakarta Sans",
        "body": "Plus Jakarta Sans",
        "mono": "Fira Code",
        "weights": {"heading": "600", "body": "400"},
        "best_for": ["B2B", "consulting", "finance", "enterprise"]
    },
    "creative": {
        "name": "Creative Bold",
        "heading": "Space Grotesk",
        "body": "DM Sans",
        "mono": "IBM Plex Mono",
        "weights": {"heading": "700", "body": "400"},
        "best_for": ["agency", "portfolio", "creative"]
    },
    "friendly": {
        "name": "Friendly Rounded",
        "heading": "Nunito",
        "body": "Nunito",
        "mono": "Fira Code",
        "weights": {"heading": "700", "body": "400"},
        "best_for": ["education", "healthcare", "kids", "community"]
    },
    "luxury": {
        "name": "Luxury Elegant",
        "heading": "Cormorant Garamond",
        "body": "Lato",
        "mono": "IBM Plex Mono",
        "weights": {"heading": "600", "body": "400"},
        "best_for": ["luxury", "fashion", "high-end", "hospitality"]
    },
    "tech": {
        "name": "Tech Developer",
        "heading": "JetBrains Mono",
        "body": "Inter",
        "mono": "JetBrains Mono",
        "weights": {"heading": "700", "body": "400"},
        "best_for": ["developer tools", "APIs", "documentation", "CLI"]
    },
    "warm": {
        "name": "Warm Humanist",
        "heading": "Lora",
        "body": "Open Sans",
        "mono": "Fira Code",
        "weights": {"heading": "600", "body": "400"},
        "best_for": ["food", "craft", "organic", "boutique"]
    }
}

UX_GUIDELINES = {
    "navigation": [
        "Max 7 items in main navigation",
        "Sticky header on scroll (hide on scroll down, show on scroll up)",
        "Mobile: hamburger menu with full-screen overlay",
        "Active state clearly indicated (underline, color, or bg)",
        "Breadcrumbs for depth > 2 navigation"
    ],
    "forms": [
        "Labels ABOVE inputs (not inside as placeholder)",
        "Inline validation on blur (not on every keystroke)",
        "Error messages below the field, red text, with icon",
        "Submit button matches primary CTA color",
        "Group related fields with visual sections",
        "Autofocus first field on page load"
    ],
    "cards": [
        "Consistent padding (16-24px)",
        "Image aspect ratio 16:9 or 3:2",
        "Max 3 lines of text (truncate with ellipsis)",
        "Hover effect: subtle shadow increase or border color change",
        "Clickable entire card (not just link inside)",
        "Skeleton placeholder while loading"
    ],
    "buttons": [
        "One primary CTA per section",
        "Min touch target 44x44px (mobile), 32px (desktop)",
        "Contrast ratio 4.5:1 minimum",
        "Loading state for async actions (spinner replaces text)",
        "Disabled state: reduced opacity, no pointer events",
        "Icon + text for primary actions, icon-only for secondary"
    ],
    "typography": [
        "Body text: 16px minimum (18px for long-form)",
        "Line height: 1.5-1.6 for body, 1.2-1.3 for headings",
        "Max 75 characters per line for readability",
        "Heading hierarchy: h1 > h2 > h3, never skip levels",
        "Font size scale: 14, 16, 18, 20, 24, 30, 36, 48, 60, 72"
    ],
    "spacing": [
        "Use 4px base grid (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96)",
        "Section padding: 64-96px vertical",
        "Component padding: 16-24px",
        "Element gaps: 8-16px",
        "Consistent vertical rhythm throughout the page"
    ],
    "loading": [
        "Skeleton screens over spinners",
        "Optimistic updates for user actions",
        "Progress bars for long operations (> 3s)",
        "Never block the UI for read operations",
        "Show cached data while fetching fresh data"
    ],
    "errors": [
        "Friendly messages: 'Something went wrong' not 'Error 500'",
        "Clear recovery action: 'Try again' or 'Go back'",
        "Never expose technical details to users",
        "Log errors server-side for debugging",
        "Graceful degradation: show what you can, hide what you can't"
    ],
    "dark_mode": [
        "Not just inverted colors — reduce saturation slightly",
        "Use surface elevation (lighter = higher) for depth",
        "Text: #F5F5F5 (primary), #A1A1AA (secondary)",
        "Background: #18181B (base), #27272A (surface), #3F3F46 (elevated)",
        "Borders: #3F3F46 (subtle), #52525B (prominent)",
        "Test both modes before launching"
    ],
    "mobile": [
        "Thumb-zone friendly: primary actions at bottom of screen",
        "Bottom nav for 3-5 top-level items",
        "Swipe gestures where natural (carousel, dismiss)",
        "No hover-dependent interactions",
        "Tap targets minimum 44x44px",
        "Pinch-to-zoom on images, not on the page"
    ]
}

INDUSTRY_PROFILES = {
    "saas": {"palette": "saas-tech", "style": "professional", "font": "modern"},
    "tech": {"palette": "saas-indigo", "style": "professional", "font": "tech"},
    "healthcare": {"palette": "healthcare-teal", "style": "professional", "font": "friendly"},
    "finance": {"palette": "finance-navy", "style": "professional", "font": "corporate"},
    "fintech": {"palette": "finance-navy", "style": "glassmorphism", "font": "modern"},
    "ecommerce": {"palette": "ecommerce-warm", "style": "flat", "font": "modern"},
    "education": {"palette": "education-blue", "style": "flat", "font": "friendly"},
    "agency": {"palette": "creative-dark", "style": "bold", "font": "creative"},
    "creative": {"palette": "creative-dark", "style": "bold", "font": "creative"},
    "food": {"palette": "organic-green", "style": "artisan", "font": "warm"},
    "luxury": {"palette": "finance-navy", "style": "luxury", "font": "luxury"},
    "portfolio": {"palette": "creative-dark", "style": "minimalist", "font": "modern"},
    "blog": {"palette": "saas-tech", "style": "minimalist", "font": "editorial"},
    "news": {"palette": "saas-tech", "style": "flat", "font": "editorial"}
}


def search_style(name: str):
    key = name.lower().replace(" ", "").replace("-", "")
    for k, v in STYLES.items():
        if key in k or key in v["name"].lower():
            return v
    return None


def search_palette(name: str):
    key = name.lower().replace(" ", "").replace("-", "")
    for k, v in PALETTES.items():
        if key in k or key in v["name"].lower():
            return v
    return None


def search_font(name: str):
    key = name.lower().replace(" ", "").replace("-", "")
    for k, v in FONTS.items():
        if key in k or key in v["name"].lower():
            return v
    return None


def search_ux(topic: str):
    key = topic.lower().replace(" ", "_").replace("-", "_")
    for k, v in UX_GUIDELINES.items():
        if key in k:
            return {"topic": k, "guidelines": v}
    return None


def search_industry(industry: str):
    key = industry.lower().replace(" ", "").replace("-", "")
    profile = INDUSTRY_PROFILES.get(key)
    if not profile:
        return None
    return {
        "industry": industry,
        "palette": PALETTES.get(profile["palette"], {}),
        "style": STYLES.get(profile["style"], {}),
        "font": FONTS.get(profile["font"], {})
    }


def generate_design_system(industry: str, style: str = None):
    profile = INDUSTRY_PROFILES.get(industry.lower().replace(" ", ""))
    if not profile:
        print(f"Unknown industry: {industry}. Available: {', '.join(INDUSTRY_PROFILES.keys())}")
        return None

    palette = PALETTES.get(profile["palette"], {})
    chosen_style = STYLES.get(style or profile["style"], {})
    font = FONTS.get(profile["font"], {})

    return {
        "industry": industry,
        "palette": palette,
        "style": chosen_style,
        "font": font,
        "ux_summary": {
            "navigation": UX_GUIDELINES["navigation"][:3],
            "buttons": UX_GUIDELINES["buttons"][:3],
            "typography": UX_GUIDELINES["typography"][:3]
        }
    }


def main():
    parser = argparse.ArgumentParser(description="UI/UX Design Search Tool")
    parser.add_argument("--style", help="Search for a UI style")
    parser.add_argument("--palette", help="Search for a color palette")
    parser.add_argument("--font", help="Search for a font pairing")
    parser.add_argument("--ux", help="Search UX guidelines by topic")
    parser.add_argument("--industry", help="Get industry-specific design profile")
    parser.add_argument("--generate", action="store_true", help="Generate a complete design system (use with --industry)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = None
    if args.generate and args.industry:
        result = generate_design_system(args.industry, args.style)
    elif args.style:
        result = search_style(args.style)
    elif args.palette:
        result = search_palette(args.palette)
    elif args.font:
        result = search_font(args.font)
    elif args.ux:
        result = search_ux(args.ux)
    elif args.industry:
        result = search_industry(args.industry)
    else:
        parser.print_help()
        return

    if result is None:
        print("Not found.")
        return

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
