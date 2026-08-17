---
name: scaffold-react-app
description: Create a production-ready React + Vite + Tailwind project following the amanita-solutions pattern. Use when starting a new client website. Generates project structure, routing, layout, shared components, and page templates.
license: MIT
metadata:
  author: ai-agency
  category: development
  version: "1.0.0"
governance_phases: [design, build]
organ_affinity: [organ-iii]
triggers: [user-asks-about-scaffold, user-asks-about-new-site, user-asks-about-react, context:website-creation]
complements: [ui-ux-design, generate-website]
inputs: [project_name, industry, style, palette, pages]
outputs: [scaffolded React project, ready for component development]
tier: core
---

# Scaffold React App

Creates a production-ready React + Vite + Tailwind project following the amanita-solutions pattern.

## Quick Start

```bash
python3 skills/agency/scaffold-react-app/scripts/scaffold.py \
    --name "client-site" \
    --industry "saas" \
    --style "professional" \
    --pages "home,about,pricing,contact"
```

## What Gets Created

```
client-site/
├── public/
│   └── favicon.svg
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Router setup
│   ├── index.css             # Global styles + Tailwind
│   ├── lib/
│   │   └── utils.ts          # cn() helper, utility functions
│   ├── components/
│   │   ├── Layout.tsx        # Page wrapper (nav + content + footer)
│   │   ├── SiteNav.tsx       # Navigation bar
│   │   ├── SiteFooter.tsx    # Footer
│   │   └── Seo.tsx           # Meta tags
│   ├── pages/
│   │   ├── HomePage.tsx      # Landing page
│   │   ├── AboutPage.tsx     # About page
│   │   ├── PricingPage.tsx   # Pricing
│   │   ├── ContactPage.tsx   # Contact form
│   │   └── NotFound.tsx      # 404 page
│   └── data/
│       └── site.ts           # Site configuration (name, nav, colors)
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── .gitignore
└── README.md
```

## Architecture Pattern (from amanita-solutions)

### Component-per-Page
Each route has its own file in `src/pages/`. Pages are simple React components that export a default function.

### Layout Wrapper
`Layout.tsx` wraps all pages with:
- `SiteNav.tsx` (navigation)
- `<main>` content area
- `SiteFooter.tsx`

### Data Files
Site configuration, content, and structured data live in `src/data/`. This makes it easy to update content without touching components.

### Routing
React Router v6 with a catch-all `*` route for 404. Routes are defined in `App.tsx`.

## Step-by-Step Process

### Step 1: Generate Project Structure
Run `scripts/scaffold.py` with the desired options. It creates all files with sensible defaults.

### Step 2: Customize Design
Use the `ui-ux-design` skill to set colors, fonts, and styles in:
- `tailwind.config.ts` (theme extension)
- `src/index.css` (CSS variables)
- `src/data/site.ts` (site metadata)

### Step 3: Build Pages
Edit the generated page files. Each page is a standalone component:
```tsx
export default function HomePage() {
  return (
    <div>
      {/* Hero section */}
      {/* Features section */}
      {/* CTA section */}
    </div>
  )
}
```

### Step 4: Add Routing
New pages get added to `App.tsx`:
```tsx
<Route element={<Layout />}>
  <Route path="/" element={<HomePage />} />
  <Route path="/new-page" element={<NewPage />} />
  <Route path="*" element={<NotFound />} />
</Route>
```

### Step 5: Deploy
```bash
npm run build  # Output in dist/
# Deploy dist/ to GitHub Pages, Vercel, Netlify, or Docker
```

## Generated Files Detail

### package.json
- React 18, React Router 6, Tailwind CSS 4, Vite 6
- TypeScript, ESLint, Prettier
- Scripts: dev, build, preview, lint

### vite.config.ts
- Base URL configurable
- React plugin
- Path aliases (@/)

### tailwind.config.ts
- Extended theme with design system tokens
- Custom colors from palette
- Font families from typography

### Layout.tsx
- Responsive nav with mobile menu
- Main content area with min-height
- Footer with links and copyright

### SiteNav.tsx
- Logo/brand name
- Navigation links (from site data)
- Mobile hamburger menu
- Sticky on scroll

### SiteFooter.tsx
- Multi-column layout
- Social links placeholder
- Copyright with dynamic year
