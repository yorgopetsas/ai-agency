---
name: create-component
description: Generate individual React components with Tailwind CSS styling. Supports hero sections, feature cards, pricing tables, testimonials, CTAs, navigation, footers, forms, and layout primitives. Use when building pages for a client website after scaffolding.
license: MIT
metadata:
  author: ai-agency
  category: development
  version: "1.0.0"
governance_phases: [build]
organ_affinity: [organ-iii]
triggers: [user-asks-about-component, user-asks-about-ui, context:component-creation]
complements: [scaffold-react-app, ui-ux-design, responsive-design-patterns]
inputs: [component_type, props, style_override]
outputs: [React TypeScript component file]
tier: core
---

# Create Component

Generate individual React + TypeScript + Tailwind components for client websites.

## Quick Start

```bash
python3 skills/agency/create-component/scripts/generate.py \
    --type hero \
    --name "LandingHero" \
    --output src/components/

python3 skills/agency/create-component/scripts/generate.py \
    --type feature-card \
    --name "FeatureGrid" \
    --items 3 \
    --output src/components/

python3 skills/agency/create-component/scripts/generate.py \
    --type custom \
    --name "StatsBar" \
    --output src/components/
```

## Component Types

| Type | Description | Props |
|------|-------------|-------|
| `hero` | Full-width hero with heading, subtitle, CTA buttons | title, subtitle, primaryCta, secondaryCta, backgroundImage |
| `feature-card` | Grid of feature cards with icon, title, description | items (icon, title, description) |
| `pricing` | Pricing table with plan cards | plans (name, price, features, highlighted) |
| `testimonial` | Testimonial carousel or grid | items (quote, author, role, company, avatar) |
| `cta` | Call-to-action banner | title, subtitle, buttonText, buttonHref |
| `section` | Generic content section with heading | title, subtitle, children |
| `stats` | Statistics/metrics bar | items (value, label) |
| `faq` | Accordion FAQ section | items (question, answer) |
| `team` | Team member grid | items (name, role, bio, avatar) |
| `contact-form` | Contact form with fields | fields (name, email, message) |
| `nav` | Navigation bar | links (label, href), logo |
| `footer` | Site footer | columns (title, links), copyright |
| `custom` | Empty component shell | — |

## Workflow

1. **Look up design system** using `ui-ux-design` skill:
   ```bash
   python3 skills/agency/ui-ux-design/scripts/search.py --industry saas
   ```

2. **Generate component** using this skill:
   ```bash
   python3 skills/agency/create-component/scripts/generate.py \
       --type hero --name "HomeHero" --output src/components/
   ```

3. **Import into page** (edit the page file):
   ```tsx
   import HomeHero from '../components/HomeHero'

   export default function HomePage() {
     return (
       <div>
         <HomeHero />
         {/* ... */}
       </div>
     )
   }
   ```

## Customization

After generating, edit the component to:
- Adjust colors (use design system tokens: `text-primary`, `bg-primary`, etc.)
- Change spacing (`py-20`, `px-4`, `gap-8`)
- Modify responsive breakpoints (`sm:`, `md:`, `lg:`)
- Add animations or interactions
- Connect to real data (props or API calls)
