# CortexOps Multi-Agent Framework

An autonomous, multi-agent engineering and scientific research operating system built for high-throughput software delivery and academic research, operating both as **Native Google Antigravity Subagents** and as a **Standalone Python Multi-Agent Framework** (`google-antigravity` SDK).

Integrated with the [ThutaCortex](file:///home/lenovo/Documents/ThutaCortex) second brain for institutional memory, architectural pattern retrieval, and automated knowledge ingestion.

---

## 1. Team Hierarchy & Roles

```text
[Lead Technical Product Manager & Engineering Director] (Root Agent)
  │
  ├── [@cxagents]                             ── Multi-agent collective swarm orchestrator
  ├── [Principal Academic Researcher]         ── Literature synthesis, experiment design, story-arc manuscripts
  ├── [Staff R&D Research Engineer]           ── Academic search (arXiv), PDF analysis, web blogs
  ├── [Principal Systems Architect]           ── Microservices, DDD, PostgreSQL DDL, API contracts
  ├── [Senior UI/UX Engineer & Technologist]  ── Wireframes, design tokens, Figma maps, WCAG AA
  ├── [Senior Frontend Engineer]              ── Next.js, Material UI, TanStack, shadcn, SEO/GEO
  ├── [Senior Backend Engineer]               ── Go Gin, Bun Express, Fastify, NestJS, Python AI
  ├── [Staff AI / ML Engineer]                ── Prompt schemas, RAG parameters, eval test suites
  ├── [Senior DevOps & SRE]                   ── Multi-stage Docker, Compose, Nginx, CI/CD, probes
  ├── [Senior QA & Evaluation Engineer]       ── Compilers, linters, exit-code-0 test runners
  ├── [Senior Software Engineer]              ── Production implementation, integration layers, clean code
  └── [Staff Security & Code Reviewer]        ── OWASP Top 10, concurrency hazards, clean code
```

---

## 2. Directory Structure & Architecture

```text
cortexops/
├── bin/                       # Universal cross-platform Node.js CLI executable (cxops)
├── .agents/                   # Workspace agent definitions (auto-discovered by Antigravity)
├── plugin/                    # Antigravity global plugin package
│   ├── plugin.json            # Plugin manifest
│   ├── agents/                # Standalone subagent definitions (.md with YAML frontmatter)
│   └── rules/AGENTS.md        # Global engineering guidelines & manuscript authoring rules
├── src/                       # Standalone Python framework
│   ├── dashboard.py           # Cross-platform live status & token telemetry dashboard
│   ├── main.py                # CLI runner and interactive driver
│   ├── team.py                # LocalAgentConfig assembler & orchestration policies
│   ├── agents/personas.py     # SubagentConfig definitions for all 12 specialized roles
│   └── tools/                 # Custom tool definitions (arXiv, web, cortex, code, runner)
├── package.json               # npm package manifest (@ctxthuta/cxops)
├── cx                         # Linux / macOS CLI executable wrapper script
├── cx.ps1                     # Windows PowerShell CLI wrapper script
├── install.sh                 # Linux / macOS 1-click automated installer
├── install.ps1                # Windows PowerShell 1-click automated installer
├── uninstall.sh               # Linux / macOS clean uninstaller
├── uninstall.ps1              # Windows PowerShell clean uninstaller
├── verify_agents.py           # Verification script for agents, tools, and links
├── IMPLEMENTATION_GUIDE.md    # Complete cross-platform installation and operation guide
├── requirements.txt           # Python dependency manifest
├── AGENTS.md                  # Senior engineering standards (zero emojis, deterministic gates)
└── README.md                  # System documentation
```

---

## 3. Quick Start & Execution Modes

### Universal Cross-Platform 1-Command Setup (via npm)
```bash
npx @ctxthuta/cxops setup
```
Or install globally:
```bash
npm install -g @ctxthuta/cxops
cxops doctor
cxops status
```

---

## 4. Two Modes of Execution

### Mode A: Native Antigravity Subagents (No External API Key Required)
When working inside Google Antigravity (IDE or CLI):
- All 12 agents are loaded globally via the linked plugin (`~/.gemini/config/plugins/cortexops`) and locally in `.agents/`.
- Subagents execute directly through Antigravity's authenticated session.
- Mention individual specialists directly (`@backend_engineer`, `@system_architect`, `@code_reviewer`), or mention `@cxagents` to mobilize the entire relevant team concurrently.

### Mode B: Standalone Python Framework (Terminal / CI / Headless)
When running outside Antigravity as an automated background process:
- Configure your Gemini API key:
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key"
  ```
- Run tasks via the Python driver:
  ```bash
  ./cx run "Research streaming anomaly detection on arXiv, produce an architecture design, and implement an in-memory streaming detector in Python with passing unit tests."
  ```

---

## 4. Cross-Laptop Setup & GitHub Synchronization

To replicate CortexOps on any workstation:

### On the Primary Workstation (Git Remote):
```bash
cd /home/lenovo/cortexops
git remote set-url origin https://github.com/ctxthuta/cortexops.git
git push -u origin main
```

### On Any New Laptop (1-Click Restoration):

#### Linux / macOS:
```bash
git clone https://github.com/ctxthuta/cortexops.git
cd cortexops
./install.sh
```

#### Windows (PowerShell):
```powershell
git clone https://github.com/ctxthuta/cortexops.git
cd cortexops
.\install.ps1
```

The installer automatically bootstraps the virtual environment, installs dependencies, and creates the global Antigravity plugin link.

---

## 5. CLI Command Reference

Execute commands via `./cx [command]` (Linux/macOS) or `.\cx.ps1 [command]` (Windows):

```bash
# View live operational & token telemetry dashboard with ANSI colors
./cx status

# Continuously monitor session telemetry (auto-refresh)
./cx watch

# Verify all 11 declarative subagents and plugin junction
./cx verify

# Re-run installation and link global plugin
./cx install

# Cleanly unregister subagents and remove local environment
./cx uninstall
```
