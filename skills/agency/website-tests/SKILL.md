---
name: website-tests
description: Validate generated websites with Python smoke tests (file structure, TypeScript syntax, design tokens) and Playwright browser tests (rendering, navigation, responsiveness). Use after generate-website or create-component to verify correctness.
license: MIT
metadata:
  author: ai-agency
  category: testing
  version: "1.0.0"
governance_phases: [prove, ship]
organ_affinity: [organ-iii]
triggers: [user-asks-about-tests, user-asks-about-validation, context:website-testing]
complements: [generate-website, scaffold-react-app, create-component]
inputs: [project_path]
outputs: [test results, pass/fail report]
tier: core
---

# Website Tests

Validate generated websites for correctness and quality.

## Quick Start

```bash
# Python smoke tests (no Node.js required)
python3 skills/agency/website-tests/scripts/smoke_test.py --project /path/to/site

# Playwright browser tests (requires Node.js + npm)
cd skills/agency/website-tests && npm install && npx playwright test
```

## Smoke Tests (Python)

Validates generated files without running the app:

| Test | What it checks |
|------|---------------|
| `structure` | Required files exist (package.json, vite.config.ts, etc.) |
| `typescript` | No obvious syntax errors (unclosed braces, missing imports) |
| `routing` | App.tsx has routes for all generated pages |
| `components` | Generated components are imported in pages |
| `design_tokens` | Tailwind config has primary/secondary/accent colors |
| `docker` | Dockerfile exists and has multi-stage build pattern |
| `responsive` | Components use responsive Tailwind classes (sm:, md:, lg:) |
| `accessibility` | Form inputs have labels, buttons have text |

## Playwright Tests (Node.js)

Browser-based tests that render the site and verify:

- Pages load without errors
- Navigation works between all routes
- Mobile menu toggles correctly
- Forms have proper structure
- Responsive breakpoints work
- No console errors

### Setup

```bash
cd skills/agency/website-tests
npm init -y
npm install -D @playwright/test
npx playwright install chromium
```

### Run against a running dev server

```bash
# Terminal 1: start the dev server
cd /path/to/site && npm run dev

# Terminal 2: run tests
cd skills/agency/website-tests
npx playwright test --project=chromium
```
