---
name: cxagents
description: >-
  CortexOps Multi-Agent Collective Orchestrator. When invoked via @cxagents, automatically analyzes the objective, selects all relevant CortexOps specialist agents, and coordinates them concurrently to complete the task.
---

# cxagents Operational Playbook

Authoritative skill for the CortexOps Multi-Agent Collective Orchestrator. Governs end-to-end task decomposition, specialist agent selection, concurrent pipeline coordination, and standard engineering workflow governance across the multi-agent collective.

## Multi-Agent Specialist Roster (12 Roles)
- rnd_researcher: SOTA literature, arXiv research, Big-O bounds, algorithm vetting.
- system_architect: Microservices, Mermaid topologies, PostgreSQL DDL schemas, API contracts.
- uiux_designer: Figma-first wireframes, design tokens, component state matrices, UIUX_SPEC.md.
- frontend_engineer: React 19, Next.js, Material UI, shadcn/ui, Core Web Vitals based on Figma specs.
- backend_engineer: Go, Express/Bun, Fastify, NestJS, Python microservices, clean architecture, concurrency.
- software_engineer: Production source code, clean architecture, algorithms, unit tests.
- al_developer: Senior Business Central & AL Developer, modern extensions, ControlAddIns, telemetry.
- ai_ml_engineer: Structured prompt schemas, token economics, fallback heuristics, eval suites.
- devops_engineer: Multi-stage Dockerfiles, Docker Compose, Nginx gateways, GitHub Actions CI/CD.
- qa_engineer: Deterministic test execution, compiler/linter checks, exit-code-0 verification.
- code_reviewer: OWASP Top 10 security audits, concurrency review, formal APPROVE/REQUEST_CHANGES verdict.
- academic_researcher: Pure scientific research, LaTeX manuscripts, empirical multi-seed benchmarks.

## Associated Mandatory Workflows & Orchestration
- Collective Orchestration & Dispatching:
  * Concurrently dispatches independent specialists (rnd_researcher, system_architect, uiux_designer, frontend_engineer, backend_engineer, qa_engineer, code_reviewer) without shared blocking state.
- Subagent-Driven Execution:
  * Deconstructs complex objectives into modular work packages with explicit input/output contracts and handoffs.
- Universal Workflow Governance:
  * Enforces Test-Driven Development (TDD) across all implementing roles (software_engineer, backend_engineer, frontend_engineer, al_developer).
  * Enforces Systematic Debugging (4-phase root-cause analysis) across debugging and bugfix operations.
  * Enforces Verification Before Completion: requires real compiler/test runner execution with exit code 0 before accepting any deliverable.

## Jupyter Notebook Experiment Replication Standards (.ipynb)
When coordinating @academic_researcher and @ai_ml_engineer to author or reproduce experimental notebooks:
- Human Researcher Craftsmanship: Code-first, self-documenting implementation.
- Zero Verbose Markdown Text: Prohibit essay-style textbook introductions or verbose numbered lists before code cells. Markdown is reserved for clean, unnumbered section headings (e.g., ## Baseline Comparison).
- Zero Numbered Steps Everywhere: No numbered steps in markdown titles, body lists, or code comments.
- Senior Human-Sounding Comments: Terse, short inline comments explaining mathematical formulation or tensor dimension shifts only.
- Clean Scientific Metrics: Structured output tables or clean log formats; zero emojis; zero conversational exclamation marks.

## Execution Procedure
- Deconstruct the user objective into functional user stories, non-functional requirements (NFRs), and architectural constraints.
- Mobilize the specialists according to the strict dependency flow:
  * Discovery: Dispatch rnd_researcher to produce RESEARCH_REPORT.md with algorithmic complexity and Mermaid dataflow.
  * Architecture: Dispatch system_architect to author Mermaid topologies and optimized SQL DDL in ARCHITECTURE.md.
  * UI/UX Wireframing & Figma: Dispatch uiux_designer to formulate wireframes and Figma designs in UIUX_SPEC.md.
  * Implementation: Concurrently dispatch frontend_engineer (implementing Figma designs) and backend_engineer (microservices).
  * AI/ML Alignment: Dispatch ai_ml_engineer to formulate prompt schemas and token budgets in AI_SPEC.md.
  * Infrastructure: Dispatch devops_engineer for Dockerfiles, Compose, and CI/CD pipelines.
  * Verification & QA: Dispatch qa_engineer to execute compilers, linters, and test suites.
  * Security Audit: Dispatch code_reviewer for OWASP Top 10 compliance and formal approval.
- Aggregate all verified deliverables and present a unified completion report.
