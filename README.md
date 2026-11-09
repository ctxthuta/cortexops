# Thea Senior Engineering Team

An autonomous, multi-agent AI software development organization built for **Thea Solutions**, operating both as **Native Google Antigravity Subagents** and as a **Standalone Python Multi-Agent Framework** (`google-antigravity` SDK).

The framework models a complete senior-level product and engineering organization operating with strict deterministic verification, isolated sandboxing, and zero emojis.

---

## 1. Team Hierarchy & Roles

```text
[Lead Technical Product Manager & Engineering Director] (Root Agent)
  │
  ├── [Principal Academic Researcher]         ── Literature synthesis, experiment design, story-arc manuscripts
  ├── [Staff R&D Research Engineer]           ── Academic search (arXiv), PDF analysis, web blogs
  ├── [Principal Systems Architect]           ── Microservices, DDD, PostgreSQL DDL, API contracts
  ├── [Senior UI/UX Engineer & Technologist]  ── Wireframes, design tokens, Figma maps, WCAG AA
  ├── [Senior Frontend Engineer]              ── Next.js, Material UI, TanStack, shadcn, SEO/GEO
  ├── [Senior Backend Engineer]               ── Go Gin, Bun Express, Fastify, NestJS, Python AI
  ├── [Staff AI / ML Engineer]                ── Prompt schemas, RAG parameters, eval test suites
  ├── [Senior DevOps & SRE]                   ── Multi-stage Docker, Compose, Nginx, CI/CD, probes
  ├── [Senior QA & Evaluation Engineer]       ── Compilers, linters, exit-code-0 test runners
  └── [Staff Security & Code Reviewer]        ── OWASP Top 10, concurrency hazards, clean code
```

---

## 2. Directory Structure & Architecture

```text
thea-engineering-team/
├── .agents/                   # Workspace agent definitions (auto-discovered by Antigravity)
├── plugin/                    # Antigravity global plugin package
│   ├── plugin.json            # Plugin manifest
│   ├── agents/                # Standalone subagent definitions (.md with YAML frontmatter)
│   └── rules/AGENTS.md        # Global engineering guidelines & manuscript authoring rules
├── src/                       # Standalone Python framework
│   ├── dashboard.py           # Cross-platform live status & token telemetry dashboard
│   ├── main.py                # CLI runner and interactive driver
│   ├── team.py                # LocalAgentConfig assembler & orchestration policies
│   ├── agents/personas.py     # SubagentConfig definitions for all 11 specialized roles
│   └── tools/                 # Custom tool definitions (arXiv, web, cortex, code, runner)
├── thea                       # Linux / macOS CLI wrapper script
├── thea.ps1                   # Windows PowerShell CLI wrapper script
├── install.sh                 # Linux / macOS 1-click automated installer
├── install.ps1                # Windows PowerShell 1-click automated installer
├── verify_agents.py           # Verification script for agents, tools, and links
├── IMPLEMENTATION_GUIDE.md    # Complete cross-platform installation and operation guide
├── requirements.txt           # Python dependency manifest
├── AGENTS.md                  # Senior engineering standards (zero emojis, deterministic gates)
└── README.md                  # System documentation
```

---

## 3. Two Modes of Execution

### Mode A: Native Antigravity Subagents (No API Key Required)
When working inside Google Antigravity (IDE or CLI):
- All 6 agents are loaded globally via the linked plugin (`~/.gemini/config/plugins/thea-engineering-team`) and locally in `.agents/`.
- No separate `GEMINI_API_KEY` is required because the subagents execute directly through Antigravity's authenticated session.
- You can delegate tasks directly to `@rnd_researcher`, `@system_architect`, `@software_engineer`, etc.

### Mode B: Standalone Python Framework (Terminal / CI / Headless)
When running outside Antigravity as an automated background process:
- Set your Google AI Studio API key:
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key"
  ```
- Run tasks via the Python driver:
  ```bash
  .venv/bin/python src/main.py "Research streaming anomaly detection on arXiv, produce an architecture design, and implement an in-memory streaming detector in Python with passing unit tests."
  ```

---

## 4. Cross-Laptop Setup & GitHub Synchronization

To replicate this entire team on another laptop:

### On the First Laptop (Initial Push):
1. Initialize git and commit:
   ```bash
   cd /home/lenovo/thea-engineering-team
   git init
   git add .
   git commit -m "feat: initial commit for thea-engineering-team framework"
   ```
2. Create a repository on GitHub (e.g. `thea-engineering-team`).
3. Push to your GitHub remote:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-username>/thea-engineering-team.git
   git push -u origin main
   ```

### On Any New Laptop (1-Click Restoration):
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/thea-engineering-team.git
   cd thea-engineering-team
   ```
2. Run the automated installer:
   ```bash
   ./install.sh
   ```
   This automatically:
   - Creates the Python `.venv` and installs all dependencies.
   - Links the Antigravity plugin into `~/.gemini/config/plugins/thea-engineering-team`.
   - Runs `verify_agents.py` to confirm all 6 agents are active.

---

## 5. Engineering Standards & Guardrails

* **Zero Emojis:** Strictly enforced across all generated code, markdown, reviews, and logs.
* **Deterministic Verification:** No deliverable is accepted based on agent conversational agreement. Code must pass actual compiler checks and test suites.
* **Sandboxed Execution:** Terminal commands run under isolated execution boundaries with timeouts.
