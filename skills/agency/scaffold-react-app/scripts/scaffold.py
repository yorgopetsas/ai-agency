#!/usr/bin/env python3
"""
React App Scaffolder
====================
Creates a production-ready React + Vite + Tailwind project
following the amanita-solutions pattern.

Usage:
    python3 scaffold.py --name "my-site" --industry "saas" --pages "home,about,pricing,contact"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Templates (raw strings, __PLACEHOLDER__ tokens, .replace() only) ──

PACKAGE_JSON = r"""{
  "name": "__NAME__",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.16",
    "typescript": "~5.6.2",
    "vite": "^6.0.0"
  }
}
"""

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>__TITLE__</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

MAIN_TSX = r"""import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
"""

APP_TSX = r"""import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
__IMPORTS__

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
__ROUTES__
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
"""

INDEX_CSS = r"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: __PRIMARY__;
  --color-secondary: __SECONDARY__;
  --color-accent: __ACCENT__;
}

body {
  font-family: '__FONT_BODY__', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: '__FONT_HEADING__', sans-serif;
}
"""

VITE_CONFIG = r"""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
"""

TAILWIND_CONFIG = r"""import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{tsx,ts}'],
  theme: {
    extend: {
      colors: {
        primary: '__PRIMARY__',
        secondary: '__SECONDARY__',
        accent: '__ACCENT__',
      },
      fontFamily: {
        heading: ['__FONT_HEADING__', 'sans-serif'],
        body: ['__FONT_BODY__', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
"""

POSTCSS_CONFIG = r"""export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

TS_CONFIG = r"""{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
"""

TS_CONFIG_APP = r"""{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
"""

TS_CONFIG_NODE = r"""{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["vite.config.ts"]
}
"""

GITIGNORE = """node_modules
dist
.env
.env.local
"""

UTILS_TS = r"""import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}
"""

LAYOUT_TSX = r"""import { Outlet } from 'react-router-dom'
import SiteNav from './SiteNav'
import SiteFooter from './SiteFooter'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteNav />
      <main className="flex-1">
        <Outlet />
      </main>
      <SiteFooter />
    </div>
  )
}
"""

SITE_NAV_TSX = r"""import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { siteConfig } from '../data/site'

export default function SiteNav() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="font-heading font-bold text-xl text-gray-900">
            {siteConfig.name}
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            {siteConfig.nav.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'text-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            {siteConfig.nav.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="block py-2 text-sm font-medium text-gray-600 hover:text-gray-900"
                onClick={() => setMobileOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}
"""

SITE_FOOTER_TSX = r"""import { siteConfig } from '../data/site'

export default function SiteFooter() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-heading font-bold text-white text-lg mb-4">
              {siteConfig.name}
            </h3>
            <p className="text-sm">{siteConfig.description}</p>
          </div>
          <div>
            <h4 className="font-medium text-white text-sm mb-4">Links</h4>
            <ul className="space-y-2">
              {siteConfig.nav.map((item) => (
                <li key={item.path}>
                  <a href={item.path} className="text-sm hover:text-white transition-colors">
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-white text-sm mb-4">Contact</h4>
            <p className="text-sm">{siteConfig.email}</p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} {siteConfig.name}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
"""

SEO_TSX = r"""interface SeoProps {
  title: string
  description?: string
}

export default function Seo({ title, description }: SeoProps) {
  return (
    <>
      <title>{title} | __SITE_NAME__</title>
      {description && <meta name="description" content={description} />}
    </>
  )
}
"""

NOT_FOUND_TSX = r"""import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-heading font-bold text-gray-900 mb-4">404</h1>
        <p className="text-gray-600 mb-8">Page not found</p>
        <Link
          to="/"
          className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          Go home
        </Link>
      </div>
    </div>
  )
}
"""

SITE_DATA = r"""export const siteConfig = {
  name: '__TITLE__',
  description: '__DESCRIPTION__',
  email: 'hello@__NAME__.com',
  url: 'https://__NAME__.com',
  nav: [
__NAV_ITEMS__
  ],
}
"""

HOME_PAGE = r"""export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="py-20 sm:py-28">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-gray-900 mb-6">
            Welcome to __TITLE__
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
            __DESCRIPTION__
          </p>
          <div className="flex justify-center gap-4">
            <a href="/contact" className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity">
              Get Started
            </a>
            <a href="/about" className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:border-gray-400 transition-colors">
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Features placeholder */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-heading font-bold text-center mb-12">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {['Feature 1', 'Feature 2', 'Feature 3'].map((f) => (
              <div key={f} className="bg-white p-6 rounded-xl shadow-sm">
                <h3 className="font-heading font-semibold text-lg mb-2">{f}</h3>
                <p className="text-gray-600 text-sm">Description of {f.toLowerCase()} goes here.</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
"""

ABOUT_PAGE = r"""export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-heading font-bold mb-6">About Us</h1>
      <p className="text-gray-600 text-lg mb-8">
        Add your about content here.
      </p>
    </div>
  )
}
"""

PRICING_PAGE = r"""export default function PricingPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-heading font-bold text-center mb-12">Pricing</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {['Starter', 'Pro', 'Enterprise'].map((plan, i) => (
          <div key={plan} className={`p-8 rounded-xl border ${
            i === 1 ? 'border-primary shadow-lg scale-105' : 'border-gray-200'
          }`}>
            <h3 className="font-heading font-bold text-xl mb-2">{plan}</h3>
            <p className="text-3xl font-bold mb-4">${(i + 1) * 29}<span className="text-base font-normal text-gray-500">/mo</span></p>
            <ul className="space-y-2 text-sm text-gray-600 mb-6">
              <li>Feature {i + 1}a</li>
              <li>Feature {i + 1}b</li>
            </ul>
            <button className="w-full py-2 rounded-lg bg-primary text-white font-medium hover:opacity-90">
              Choose {plan}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
"""

CONTACT_PAGE = r"""export default function ContactPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-heading font-bold mb-6">Contact</h1>
      <form className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-1">Name</label>
          <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Message</label>
          <textarea rows={5} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"></textarea>
        </div>
        <button type="submit" className="w-full py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity">
          Send Message
        </button>
      </form>
    </div>
  )
}
"""

FAVICON_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="__PRIMARY__"/>
  <text x="50" y="65" font-size="50" text-anchor="middle" fill="white" font-family="sans-serif" font-weight="bold">__INITIAL__</text>
</svg>
"""

README_MD = r"""# __TITLE__

__DESCRIPTION__

## Tech Stack
- React 18 + TypeScript
- Vite 6
- Tailwind CSS 3
- React Router 6

## Getting Started
```bash
npm install
npm run dev
```

## Build
```bash
npm run build
```

Output is in `dist/`.

## Deploy
- GitHub Pages: push `dist/` to `gh-pages` branch
- Vercel: connect repo, auto-deploys
- Netlify: drag & drop `dist/` folder
- Docker: see Dockerfile
"""

# ── Colors by Industry ───────────────────────────────────────────────

INDUSTRY_DEFAULTS = {
    "saas": {"primary": "#2563EB", "secondary": "#475569", "accent": "#06B6D4", "font_heading": "Inter", "font_body": "Inter"},
    "tech": {"primary": "#4F46E5", "secondary": "#64748B", "accent": "#7C3AED", "font_heading": "Space Grotesk", "font_body": "DM Sans"},
    "healthcare": {"primary": "#0D9488", "secondary": "#6B7280", "accent": "#059669", "font_heading": "Nunito", "font_body": "Nunito"},
    "finance": {"primary": "#1E3A5F", "secondary": "#64748B", "accent": "#D97706", "font_heading": "Plus Jakarta Sans", "font_body": "Plus Jakarta Sans"},
    "fintech": {"primary": "#1E40AF", "secondary": "#64748B", "accent": "#06B6D4", "font_heading": "Inter", "font_body": "Inter"},
    "ecommerce": {"primary": "#EA580C", "secondary": "#525252", "accent": "#DC2626", "font_heading": "Inter", "font_body": "Inter"},
    "education": {"primary": "#2563EB", "secondary": "#475569", "accent": "#7C3AED", "font_heading": "Nunito", "font_body": "Nunito"},
    "agency": {"primary": "#D946EF", "secondary": "#A1A1AA", "accent": "#84CC16", "font_heading": "Space Grotesk", "font_body": "DM Sans"},
    "creative": {"primary": "#D946EF", "secondary": "#71717A", "accent": "#84CC16", "font_heading": "Space Grotesk", "font_body": "DM Sans"},
    "food": {"primary": "#15803D", "secondary": "#71717A", "accent": "#A16207", "font_heading": "Lora", "font_body": "Open Sans"},
    "luxury": {"primary": "#C9A96E", "secondary": "#525252", "accent": "#18181B", "font_heading": "Cormorant Garamond", "font_body": "Lato"},
    "portfolio": {"primary": "#2563EB", "secondary": "#71717A", "accent": "#06B6D4", "font_heading": "Inter", "font_body": "Inter"},
    "blog": {"primary": "#2563EB", "secondary": "#64748B", "accent": "#06B6D4", "font_heading": "Playfair Display", "font_body": "Source Sans 3"},
    "news": {"primary": "#2563EB", "secondary": "#64748B", "accent": "#06B6D4", "font_heading": "Playfair Display", "font_body": "Source Sans 3"},
}

PAGE_TEMPLATES = {
    "home": ("HomePage", HOME_PAGE),
    "about": ("AboutPage", ABOUT_PAGE),
    "pricing": ("PricingPage", PRICING_PAGE),
    "contact": ("ContactPage", CONTACT_PAGE),
}

DEFAULT_PAGES = ["home", "about", "pricing", "contact"]


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def scaffold(name: str, industry: str, pages: list, output_dir: Path):
    colors = INDUSTRY_DEFAULTS.get(industry, INDUSTRY_DEFAULTS["saas"])
    title = name.replace("-", " ").replace("_", " ").title()
    description = "A modern {} website built with React, Vite, and Tailwind CSS.".format(industry)
    initial = title[0].upper()

    # Filter valid pages
    valid_pages = [p for p in pages if p in PAGE_TEMPLATES]
    if "home" not in valid_pages:
        valid_pages.insert(0, "home")

    # Generate imports and routes
    imports = "\n".join(
        "import {page} from './pages/{page}'".format(page=PAGE_TEMPLATES[p][0])
        for p in valid_pages
    )
    imports += "\nimport NotFound from './pages/NotFound'"

    nav_items = "\n".join(
        "    {{ label: '{}', path: '/{}' }},".format(
            p.replace("-", " ").title(),
            "" if p == "home" else p
        )
        for p in valid_pages
    )

    routes = "\n".join(
        '        <Route path="/' + ('' if p == 'home' else p) + '" element=<' + PAGE_TEMPLATES[p][0] + ' />} />'
        for p in valid_pages
    )

    # Write files
    src = output_dir / "src"
    write_file(output_dir / "package.json", PACKAGE_JSON.replace("__NAME__", name))
    write_file(output_dir / "index.html", INDEX_HTML.replace("__TITLE__", title))
    write_file(output_dir / ".gitignore", GITIGNORE)
    write_file(output_dir / "tsconfig.json", TS_CONFIG)
    write_file(output_dir / "tsconfig.app.json", TS_CONFIG_APP)
    write_file(output_dir / "tsconfig.node.json", TS_CONFIG_NODE)
    write_file(output_dir / "vite.config.ts", VITE_CONFIG)
    write_file(output_dir / "tailwind.config.ts", TAILWIND_CONFIG
        .replace("__PRIMARY__", colors["primary"])
        .replace("__SECONDARY__", colors["secondary"])
        .replace("__ACCENT__", colors["accent"])
        .replace("__FONT_HEADING__", colors["font_heading"])
        .replace("__FONT_BODY__", colors["font_body"]))
    write_file(output_dir / "postcss.config.js", POSTCSS_CONFIG)
    write_file(output_dir / "README.md", README_MD
        .replace("__TITLE__", title)
        .replace("__DESCRIPTION__", description))

    write_file(src / "main.tsx", MAIN_TSX)
    write_file(src / "App.tsx", APP_TSX.replace("__IMPORTS__", imports).replace("__ROUTES__", routes))
    write_file(src / "index.css", INDEX_CSS
        .replace("__PRIMARY__", colors["primary"])
        .replace("__SECONDARY__", colors["secondary"])
        .replace("__ACCENT__", colors["accent"])
        .replace("__FONT_HEADING__", colors["font_heading"])
        .replace("__FONT_BODY__", colors["font_body"]))
    write_file(src / "lib/utils.ts", UTILS_TS)

    write_file(src / "components/Layout.tsx", LAYOUT_TSX)
    write_file(src / "components/SiteNav.tsx", SITE_NAV_TSX)
    write_file(src / "components/SiteFooter.tsx", SITE_FOOTER_TSX)
    write_file(src / "components/Seo.tsx", SEO_TSX.replace("__SITE_NAME__", title))

    write_file(src / "data/site.ts", SITE_DATA
        .replace("__TITLE__", title)
        .replace("__NAME__", name)
        .replace("__DESCRIPTION__", description)
        .replace("__NAV_ITEMS__", nav_items))

    for page in valid_pages:
        page_name, template = PAGE_TEMPLATES[page]
        content = template.replace("__TITLE__", title).replace("__DESCRIPTION__", description)
        write_file(src / "pages" / "{}.tsx".format(page_name), content)

    write_file(src / "pages/NotFound.tsx", NOT_FOUND_TSX)
    write_file(output_dir / "public/favicon.svg", FAVICON_SVG
        .replace("__PRIMARY__", colors["primary"])
        .replace("__INITIAL__", initial))

    return output_dir


def main():
    parser = argparse.ArgumentParser(description="Scaffold a React + Vite + Tailwind project")
    parser.add_argument("--name", required=True, help="Project name (e.g., 'my-site')")
    parser.add_argument("--industry", default="saas", help="Industry for design defaults")
    parser.add_argument("--pages", default=",".join(DEFAULT_PAGES), help="Comma-separated page names")
    parser.add_argument("--output", default=None, help="Output directory (default: ./<name>)")
    args = parser.parse_args()

    pages = [p.strip() for p in args.pages.split(",")]
    output = Path(args.output) if args.output else Path.cwd() / args.name

    if output.exists():
        print("Error: {} already exists. Remove it or choose a different name.".format(output))
        sys.exit(1)

    scaffold(args.name, args.industry, pages, output)
    print("Scaffolded {} at {}".format(args.name, output))
    print("  Industry: {}".format(args.industry))
    print("  Pages: {}".format(", ".join(pages)))
    print("  Next: cd {} && npm install && npm run dev".format(output.name))


if __name__ == "__main__":
    main()
