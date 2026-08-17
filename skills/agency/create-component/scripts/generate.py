#!/usr/bin/env python3
"""
React Component Generator
=========================
Generates individual React + TypeScript + Tailwind components.

Usage:
    python3 generate.py --type hero --name "LandingHero" --output src/components/
    python3 generate.py --type feature-card --name "Features" --items 3 --output src/components/
    python3 generate.py --type custom --name "StatsBar" --output src/components/
"""

import argparse
import sys
from pathlib import Path


# ── Component Templates ──────────────────────────────────────────────

HERO = r"""interface HeroProps {
  title: string
  subtitle?: string
  primaryCta?: { label: string; href: string }
  secondaryCta?: { label: string; href: string }
}

export default function __NAME__({
  title,
  subtitle,
  primaryCta,
  secondaryCta,
}: HeroProps) {
  return (
    <section className="relative py-20 sm:py-28 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-gray-900 mb-6">
          {title}
        </h1>
        {subtitle && (
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
            {subtitle}
          </p>
        )}
        <div className="flex justify-center gap-4">
          {primaryCta && (
            <a
              href={primaryCta.href}
              className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              {primaryCta.label}
            </a>
          )}
          {secondaryCta && (
            <a
              href={secondaryCta.href}
              className="px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:border-gray-400 transition-colors"
            >
              {secondaryCta.label}
            </a>
          )}
        </div>
      </div>
    </section>
  )
}
"""

FEATURE_CARD = r"""interface Feature {
  icon: string
  title: string
  description: string
}

interface FeatureCardProps {
  title?: string
  subtitle?: string
  items: Feature[]
}

export default function __NAME__({
  title,
  subtitle,
  items,
}: FeatureCardProps) {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-12">{subtitle}</p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {items.map((item) => (
            <div key={item.title} className="bg-white p-6 rounded-xl shadow-sm">
              <div className="text-3xl mb-4">{item.icon}</div>
              <h3 className="font-heading font-semibold text-lg mb-2">{item.title}</h3>
              <p className="text-gray-600 text-sm">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

PRICING = r"""interface Plan {
  name: string
  price: number
  description?: string
  features: string[]
  highlighted?: boolean
  cta?: string
}

interface PricingProps {
  title?: string
  subtitle?: string
  plans: Plan[]
}

export default function __NAME__({
  title,
  subtitle,
  plans,
}: PricingProps) {
  return (
    <section className="py-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-12">{subtitle}</p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`p-8 rounded-xl border ${
                plan.highlighted
                  ? 'border-primary shadow-lg scale-105'
                  : 'border-gray-200'
              }`}
            >
              <h3 className="font-heading font-bold text-xl mb-2">{plan.name}</h3>
              <p className="text-3xl font-bold mb-1">${plan.price}</p>
              {plan.description && (
                <p className="text-sm text-gray-500 mb-4">{plan.description}</p>
              )}
              <ul className="space-y-2 text-sm text-gray-600 mb-6">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-2 rounded-lg font-medium hover:opacity-90 transition-opacity ${
                  plan.highlighted
                    ? 'bg-primary text-white'
                    : 'border border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {plan.cta || 'Get Started'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

TESTIMONIAL = r"""interface Testimonial {
  quote: string
  author: string
  role?: string
  company?: string
  avatar?: string
}

interface TestimonialProps {
  title?: string
  subtitle?: string
  items: Testimonial[]
}

export default function __NAME__({
  title,
  subtitle,
  items,
}: TestimonialProps) {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-12">{subtitle}</p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {items.map((t) => (
            <div key={t.author} className="bg-white p-6 rounded-xl shadow-sm">
              <p className="text-gray-600 mb-4 italic">"{t.quote}"</p>
              <div className="flex items-center gap-3">
                {t.avatar ? (
                  <img src={t.avatar} alt={t.author} className="w-10 h-10 rounded-full" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                    {t.author[0]}
                  </div>
                )}
                <div>
                  <p className="font-medium text-sm">{t.author}</p>
                  {t.role && (
                    <p className="text-xs text-gray-500">
                      {t.role}{t.company ? ` at ${t.company}` : ''}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

CTA = r"""interface CtaProps {
  title: string
  subtitle?: string
  buttonText?: string
  buttonHref?: string
}

export default function __NAME__({
  title,
  subtitle,
  buttonText = 'Get Started',
  buttonHref = '/contact',
}: CtaProps) {
  return (
    <section className="py-16 bg-primary">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-heading font-bold text-white mb-4">{title}</h2>
        {subtitle && (
          <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">{subtitle}</p>
        )}
        <a
          href={buttonHref}
          className="inline-flex items-center px-8 py-3 bg-white text-primary rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          {buttonText}
        </a>
      </div>
    </section>
  )
}
"""

SECTION = r"""interface SectionProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
  className?: string
}

export default function __NAME__({
  title,
  subtitle,
  children,
  className = '',
}: SectionProps) {
  return (
    <section className={`py-16 ${className}`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-12">{subtitle}</p>
        )}
        {children}
      </div>
    </section>
  )
}
"""

STATS = r"""interface Stat {
  value: string
  label: string
}

interface StatsProps {
  items: Stat[]
  className?: string
}

export default function __NAME__({ items, className = '' }: StatsProps) {
  return (
    <section className={`py-16 ${className}`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {items.map((stat) => (
            <div key={stat.label}>
              <p className="text-4xl font-heading font-bold text-primary mb-2">{stat.value}</p>
              <p className="text-sm text-gray-600">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

FAQ = r"""interface FaqItem {
  question: string
  answer: string
}

interface FaqProps {
  title?: string
  subtitle?: string
  items: FaqItem[]
}

export default function __NAME__({
  title,
  subtitle,
  items,
}: FaqProps) {
  return (
    <section className="py-16">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center mb-12">{subtitle}</p>
        )}
        <div className="space-y-4">
          {items.map((item) => (
            <details key={item.question} className="group border border-gray-200 rounded-lg">
              <summary className="flex items-center justify-between px-6 py-4 cursor-pointer font-medium">
                {item.question}
                <svg className="w-5 h-5 text-gray-500 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-4 text-gray-600 text-sm">{item.answer}</div>
            </details>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

TEAM = r"""interface Member {
  name: string
  role: string
  bio?: string
  avatar?: string
}

interface TeamProps {
  title?: string
  subtitle?: string
  items: Member[]
}

export default function __NAME__({
  title,
  subtitle,
  items,
}: TeamProps) {
  return (
    <section className="py-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold text-center mb-4">{title}</h2>
        )}
        {subtitle && (
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-12">{subtitle}</p>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {items.map((m) => (
            <div key={m.name} className="text-center">
              {m.avatar ? (
                <img src={m.avatar} alt={m.name} className="w-24 h-24 rounded-full mx-auto mb-4" />
              ) : (
                <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4 text-primary font-bold text-2xl">
                  {m.name[0]}
                </div>
              )}
              <h3 className="font-heading font-semibold text-lg">{m.name}</h3>
              <p className="text-sm text-primary mb-2">{m.role}</p>
              {m.bio && <p className="text-sm text-gray-600">{m.bio}</p>}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
"""

CONTACT_FORM = r"""interface Field {
  name: string
  label: string
  type?: 'text' | 'email' | 'textarea' | 'tel'
  placeholder?: string
  required?: boolean
}

interface ContactFormProps {
  title?: string
  fields?: Field[]
  submitText?: string
}

const DEFAULT_FIELDS: Field[] = [
  { name: 'name', label: 'Name', type: 'text', placeholder: 'Your name', required: true },
  { name: 'email', label: 'Email', type: 'email', placeholder: 'you@example.com', required: true },
  { name: 'message', label: 'Message', type: 'textarea', placeholder: 'How can we help?', required: true },
]

export default function __NAME__({
  title,
  fields = DEFAULT_FIELDS,
  submitText = 'Send Message',
}: ContactFormProps) {
  return (
    <section className="py-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {title && (
          <h2 className="text-3xl font-heading font-bold mb-8">{title}</h2>
        )}
        <form className="space-y-6">
          {fields.map((field) => (
            <div key={field.name}>
              <label htmlFor={field.name} className="block text-sm font-medium mb-1">
                {field.label}
              </label>
              {field.type === 'textarea' ? (
                <textarea
                  id={field.name}
                  name={field.name}
                  rows={5}
                  placeholder={field.placeholder}
                  required={field.required}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"
                />
              ) : (
                <input
                  type={field.type || 'text'}
                  id={field.name}
                  name={field.name}
                  placeholder={field.placeholder}
                  required={field.required}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                />
              )}
            </div>
          ))}
          <button
            type="submit"
            className="w-full py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            {submitText}
          </button>
        </form>
      </div>
    </section>
  )
}
"""

NAV = r"""import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface NavItem {
  label: string
  href: string
}

interface NavProps {
  logo?: string
  links: NavItem[]
}

export default function __NAME__({ logo, links }: NavProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="font-heading font-bold text-xl text-gray-900">
            {logo || 'Brand'}
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {links.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`text-sm font-medium transition-colors ${
                  location.pathname === item.href
                    ? 'text-primary'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>

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

        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            {links.map((item) => (
              <Link
                key={item.href}
                to={item.href}
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

FOOTER = r"""interface FooterColumn {
  title: string
  links: { label: string; href: string }[]
}

interface FooterProps {
  columns: FooterColumn[]
  copyright?: string
}

export default function __NAME__({ columns, copyright }: FooterProps) {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {columns.map((col) => (
            <div key={col.title}>
              <h4 className="font-medium text-white text-sm mb-4">{col.title}</h4>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.href}>
                    <a href={link.href} className="text-sm hover:text-white transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
          <p>{copyright || `© ${new Date().getFullYear()} All rights reserved.`}</p>
        </div>
      </div>
    </footer>
  )
}
"""

CUSTOM = r"""interface __NAME__Props {
  className?: string
  children?: React.ReactNode
}

export default function __NAME__({ className = '', children }: __NAME__Props) {
  return (
    <div className={className}>
      {children || '<!-- Add content here -->'}
    </div>
  )
}
"""


# ── Registry ─────────────────────────────────────────────────────────

COMPONENTS = {
    "hero": HERO,
    "feature-card": FEATURE_CARD,
    "pricing": PRICING,
    "testimonial": TESTIMONIAL,
    "cta": CTA,
    "section": SECTION,
    "stats": STATS,
    "faq": FAQ,
    "team": TEAM,
    "contact-form": CONTACT_FORM,
    "nav": NAV,
    "footer": FOOTER,
    "custom": CUSTOM,
}


def generate(component_type: str, name: str, output_dir: Path) -> Path:
    template = COMPONENTS.get(component_type)
    if not template:
        print("Unknown type: {}. Available: {}".format(
            component_type, ", ".join(sorted(COMPONENTS.keys()))
        ))
        sys.exit(1)

    content = template.replace("__NAME__", name)
    out_file = output_dir / "{}.tsx".format(name)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(content)
    return out_file


def main():
    parser = argparse.ArgumentParser(description="Generate React + Tailwind components")
    parser.add_argument("--type", required=True, choices=sorted(COMPONENTS.keys()),
                        help="Component type to generate")
    parser.add_argument("--name", required=True, help="Component name (PascalCase)")
    parser.add_argument("--output", default="src/components", help="Output directory")
    args = parser.parse_args()

    output = Path(args.output)
    path = generate(args.type, args.name, output)
    print("Generated: {}".format(path))
    print("  Type: {}".format(args.type))
    print("  Import: import {} from './{}'".format(args.name, args.name))


if __name__ == "__main__":
    main()
