---
name: generate-website
description: End-to-end website generation. Chains ui-ux-design → scaffold-react-app → create-component → containerize-docker into a single workflow. Produces a complete, containerized React + Tailwind website for a given industry.
license: MIT
metadata:
  author: ai-agency
  category: orchestration
  version: "1.0.0"
governance_phases: [build, ship]
organ_affinity: [organ-iii]
triggers: [user-asks-about-website, user-asks-about-generate, context:website-creation]
complements: [ui-ux-design, scaffold-react-app, create-component, containerize-docker]
inputs: [project_name, industry, pages, style_override]
outputs: [complete website project with Docker support]
tier: core
---

# Generate Website

One command to generate a complete, containerized website.

## Quick Start

```bash
python3 skills/agency/generate-website/scripts/generate.py \
    --name "acme-saas" \
    --industry "saas" \
    --pages "home,about,pricing,contact"
```

## What It Does

1. **Design system** → looks up industry palette, fonts, style via `ui-ux-design`
2. **Scaffold** → creates React + Vite + Tailwind project via `scaffold-react-app`
3. **Components** → generates hero, features, pricing, testimonials, CTA via `create-component`
4. **Docker** → adds Dockerfile + docker-compose.yml via `containerize-docker`
5. **Summary** → prints what was created and next steps

## Output Structure

```
acme-saas/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .dockerignore
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── lib/utils.ts
    ├── components/
    │   ├── Layout.tsx
    │   ├── SiteNav.tsx
    │   ├── SiteFooter.tsx
    │   ├── Seo.tsx
    │   ├── HomeHero.tsx        ← generated
    │   ├── HomeFeatures.tsx    ← generated
    │   ├── HomeTestimonials.tsx← generated
    │   └── HomeCta.tsx         ← generated
    ├── pages/
    │   ├── HomePage.tsx        ← imports generated components
    │   ├── AboutPage.tsx
    │   ├── PricingPage.tsx
    │   └── ContactPage.tsx
    └── data/site.ts
```

## Customization

After generation, edit components to:
- Replace placeholder content with real copy
- Adjust colors using design system tokens (`text-primary`, `bg-primary`)
- Connect forms to a backend API
- Add more pages or components as needed

## Deploy

```bash
cd acme-saas
docker compose up --build
# Open http://localhost:3000
```
