---
name: ui-ux-design
description: Design system intelligence for the DESIGNER agent. 67 UI styles, 161 industry-specific color palettes, 57 font pairings, 119 UX guidelines, and a design system generator. Use when creating visual designs, choosing styles, selecting palettes, or generating design systems for client websites.
license: MIT
metadata:
  author: ai-agency
  category: design
  version: "1.0.0"
governance_phases: [design, build]
organ_affinity: [organ-ii]
triggers: [user-asks-about-design, user-asks-about-style, user-asks-about-colors, user-asks-about-fonts, user-asks-about-ux, context:design-system]
complements: [scaffold-react-app, generate-website]
inputs: [industry, brand preferences, target audience, content type]
outputs: [design system spec, color palette, typography, component styles]
tier: core
---

# UI/UX Design Skill

Design system intelligence for creating professional, industry-appropriate websites.

## How to Use

1. **Look up** design decisions using `scripts/search.py`:
   ```bash
   python3 skills/agency/ui-ux-design/scripts/search.py --style glassmorphism
   python3 skills/agency/ui-ux-design/scripts/search.py --palette "saas-tech"
   python3 skills/agency/ui-ux-design/scripts/search.py --font "modern"
   python3 skills/agency/ui-ux-design/scripts/search.py --ux "navigation"
   python3 skills/agency/ui-ux-design/scripts/search.py --industry "healthcare"
   ```

2. **Generate** a complete design system:
   ```bash
   python3 skills/agency/ui-ux-design/scripts/search.py --generate --industry "fintech" --style "professional"
   ```

3. **Apply** the results to your component design in `create_component` or `scaffold_react_app`.

## Design System Generator (v2.0)

When generating a design system for a client, follow this process:

### Step 1: Determine Industry
Ask or infer the client's industry. Use `scripts/search.py --industry <name>` to get industry-specific palettes and guidelines.

### Step 2: Choose UI Style
Select from 67 styles based on the industry and brand:

| Category | Styles |
|----------|--------|
| **Corporate** | Professional, Minimalist, Corporate, Executive, Enterprise |
| **Creative** | Artistic, Playful, Bold, Experimental, Brutalist |
| **Tech** | Glassmorphism, Neumorphism, Futuristic, Cyberpunk, Terminal |
| **Elegant** | Luxury, Refined, Classic, Art Deco, Bauhaus |
| **Friendly** | Warm, Organic, Rounded, Soft, Handmade |
| **Modern** | Clean, Geometric, Flat, Material, Fluent |

### Step 3: Select Color Palette
Each industry has 3-5 recommended palettes. Use the search script to get palettes with:
- Primary, secondary, accent colors
- Background and surface colors
- Text colors (primary, secondary, muted)
- Semantic colors (success, warning, error, info)

### Step 4: Choose Typography
Select from 57 font pairings. Match to the style:
- **Serif + Sans-serif** = Classic, editorial
- **Sans-serif + Monospace** = Tech, developer-focused
- **Display + Sans-serif** = Bold, creative
- **Single family** = Clean, modern

### Step 5: Apply UX Guidelines
Use `scripts/search.py --ux <topic>` for specific UX patterns:
- Navigation patterns
- Form design
- Card layouts
- Mobile-first patterns
- Accessibility (WCAG 2.1 AA)
- Loading states
- Error handling
- Dark/light mode

### Step 6: Output Design System
Generate a complete design system spec:
```
design_system/
├── colors.json        # Color tokens
├── typography.json    # Font sizes, weights, line heights
├── spacing.json       # Spacing scale
├── components.json    # Component style overrides
└── DESIGN_SYSTEM.md   # Human-readable overview
```

## Industry-Specific Palettes

### Technology / SaaS
- **Primary**: Blue (#2563EB) or Indigo (#4F46E5)
- **Secondary**: Slate (#475569)
- **Accent**: Cyan (#06B6D4) or Violet (#7C3AED)
- **Background**: White (#FFFFFF) or Slate-50 (#F8FAFC)

### Healthcare
- **Primary**: Teal (#0D9488) or Blue (#0284C7)
- **Secondary**: Gray (#6B7280)
- **Accent**: Green (#059669) for positive, Rose (#E11D48) for alerts
- **Background**: White with subtle warm tint

### Finance / Fintech
- **Primary**: Navy (#1E3A5F) or Dark Blue (#1E40AF)
- **Secondary**: Gray (#64748B)
- **Accent**: Gold (#D97706) or Emerald (#059669)
- **Background**: White, high contrast for trust

### E-commerce
- **Primary**: Brand color (varies)
- **Secondary**: Neutral (#525252)
- **Accent**: Orange (#EA580C) or Red (#DC2626) for CTAs
- **Background**: White, product images dominate

### Education
- **Primary**: Blue (#2563EB) or Purple (#7C3AED)
- **Secondary**: Slate (#475569)
- **Accent**: Green (#16A34A) for success, Amber (#D97706) for warnings
- **Background**: Light, friendly, high readability

### Creative / Agency
- **Primary**: Bold accent (varies by brand)
- **Secondary**: Dark (#18181B)
- **Accent**: Vibrant (Fuchsia #D946EF, Lime #84CC16, etc.)
- **Background**: Dark mode common, or clean white

## UX Guidelines (Key Rules)

1. **Navigation**: Max 7 items in main nav. Sticky header on scroll. Mobile: hamburger menu.
2. **Cards**: Consistent padding (16-24px). Image aspect ratio 16:9 or 3:2. Max 3 lines of text.
3. **Forms**: Label above input. Inline validation. Clear error messages. Submit button matches CTA color.
4. **CTAs**: One primary CTA per section. Contrast ratio 4.5:1 minimum. Min touch target 44x44px.
5. **Typography**: Body 16px minimum. Line height 1.5-1.6. Max 75 characters per line.
6. **Spacing**: Use 4px base grid (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96).
7. **Loading**: Skeleton screens over spinners. Optimistic updates for actions.
8. **Error states**: Friendly messages, clear recovery actions, never expose technical details.
9. **Dark mode**: Not just inverted colors. Reduce saturation slightly. Use surface elevation.
10. **Mobile**: Thumb-zone friendly. Bottom nav for 3-5 items. Swipe gestures where natural.

## Anti-Patterns (Avoid)

- Centered hero with purple gradient (AI slop)
- Excessive rounded corners on everything
- Inter font on every page
- Stock photos of handshakes/laptops
- "Revolutionary" / "Game-changing" copy
- Floating chat widgets that cover content
- Auto-playing videos/carousels
- Pop-ups on first visit
