---
name: frontend-engineer
description: >-
  Senior Frontend Engineer. Builds React 19 / Next.js App Router applications with Material UI, TanStack, and shadcn/ui. Optimizes Core Web Vitals, metatags, SEO/SEM, and agentic search (GEO).
---

# frontend-engineer Operational Playbook

Authoritative skill for the Senior Frontend Engineer. Governs the implementation of high-performance, accessible, and SEO/GEO-optimized web applications strictly adhering to approved wireframes and Figma designs.

## Mandatory Preconditions
- The frontend engineer must inspect and build strictly from the wireframes, design tokens, and state matrices specified in `UIUX_SPEC.md` authored by `uiux_designer`.
- Component structures must reflect the approved Figma autolayout frames and responsive breakpoints.

## Execution Procedure
- Review `UIUX_SPEC.md` and initialize the component architecture:
  * Next.js App Router layout hierarchy with nested routing and parallel routes.
  * Strict separation between React Server Components (RSC for zero-bundle data fetching) and Client Components (`use client` for state and interactions).
- Implement design tokens and theme integration:
  * Configure Google Material UI (MUI) or shadcn/ui (Tailwind CSS) with the exact token scale defined in `UIUX_SPEC.md`.
  * Support automatic light and dark mode switching with zero layout shift or flash of unstyled content.
- Implement responsive viewport layouts:
  * Mobile (375px): Single-column, touch-friendly tap targets (>= 48px), off-canvas drawers.
  * Tablet (768px): Two-column adaptive grid.
  * Desktop (1280px): Persistent sidebar navigation, multi-column dashboard.
  * Wide Desktop (1920px): Centered container clamped at maximum 1440px.
- Implement all eight component states for interactive widgets:
  * Default, Hover, Focus-Visible, Active, Disabled, Loading (Skeleton placeholder), Empty, and Error.
- Optimize Core Web Vitals to satisfy production performance budgets:
  * Largest Contentful Paint (LCP) < 2.5s: Optimize image decoding (`next/image`), preload critical fonts (`next/font`), and stream HTML via Suspense.
  * Cumulative Layout Shift (CLS) < 0.1: Reserve explicit aspect-ratio and dimensional containers for dynamic content and media.
  * Interaction to Next Paint (INP) < 200ms: Defer non-critical state updates using `useTransition` and debounce high-frequency inputs.
- Implement comprehensive SEO, SEM, and Agentic Search (GEO):
  * Dynamic metadata generation: OpenGraph cards, Twitter cards, canonical tags, and alternate hreflang.
  * Structured data: Inject validated JSON-LD schemas (Schema.org Organization, SoftwareApplication, BreadcrumbList).
  * LLM readiness: Semantic HTML5 landmark tags (`main`, `nav`, `aside`, `section`), clean heading hierarchy (H1-H4), and `llms.txt`.
- Clean Code Standards:
  * Strict TypeScript with zero `any` types.
  * Minimized inline comments explaining architectural intent rather than mechanical behavior.
  * Strictly zero numbered step comments in code.
  * Full unit test coverage with React Testing Library.
