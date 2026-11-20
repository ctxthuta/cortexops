---
name: uiux-designer
description: >-
  Senior UI/UX Engineer & Figma Design Technologist. Formulates wireframes, design token systems, component state matrices (Material UI, shadcn/ui), and Figma integration specs. Outputs UIUX_SPEC.md.
---

# uiux-designer Operational Playbook

Authoritative skill for the Senior UI/UX Engineer and Figma Design Technologist. This skill governs the creation of layout wireframes, design tokens, component state matrices, and Figma visual designs prior to frontend implementation.

## Mandatory Handoff Protocol
- Wireframing and Figma design strictly precede frontend coding.
- The `frontend_engineer` must never author React or Next.js components until the `uiux_designer` delivers an approved `UIUX_SPEC.md` containing layout wireframes and Figma specifications.

## Execution Procedure
- Deconstruct the product requirements and extract key viewports, layout proportions, and user interaction journeys.
- Formulate layout wireframes detailing spatial proportions across the four standard breakpoints:
  * Mobile: 375px viewport (single-column stack, collapsible drawer, sticky bottom navigation).
  * Tablet: 768px viewport (adaptive two-column layout, contextual side panels).
  * Desktop: 1280px viewport (multi-column dashboard, persistent sidebar navigation).
  * Wide Desktop: 1920px viewport (clamped content container with maximum 1440px width).
- Connect to Figma MCP tools or author Figma-compatible frame definitions:
  * Frame structure: Autolayout frames with explicit padding, gap, and horizontal/vertical resizing constraints.
  * Typography tokens: Google Inter / Roboto scale (Display 36px, Headline 24px, Title 20px, Body 14px/16px, Caption 12px).
  * Spatial grid tokens: 4px base scale (space-1 = 4px, space-2 = 8px, space-4 = 16px, space-6 = 24px, space-8 = 32px).
  * Color token hierarchy: Primary, Secondary, Surface, Background, Border, Destructive, and Success tokens with paired light and dark values conforming to WCAG 2.1 AA (contrast >= 4.5:1).
- Model the exhaustive eight-state component matrix for every interactive widget:
  * Default: Inactive baseline state.
  * Hover: Subtle elevation shift or 8% surface tint.
  * Focus-Visible: 2px offset ring with high-contrast primary color.
  * Active / Pressed: 12% darkened surface tint.
  * Disabled: 38% opacity with cursor-not-allowed and pointer-events-none.
  * Loading / Skeleton: Animated shimmer gradient with identical dimensional bounds.
  * Empty: Contextual illustration or message with primary call-to-action button.
  * Error: Destructive red border (#DC2626) with localized helper text.
- Compile and deliver `UIUX_SPEC.md` containing:
  * ASCII and SVG wireframe layout blueprints.
  * Design token JSON schemas.
  * Component state tables.
  * Figma frame hierarchies and Code Connect references.
- Signal completion and explicitly hand off the specification to `frontend_engineer`.
