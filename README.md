# CortexOps Multi-Agent Framework

An autonomous, multi-agent engineering and scientific research operating system built for high-throughput software delivery and academic research, operating as **Native Google Antigravity Subagents**.

Integrated with the [ThutaCortex](file:///home/lenovo/Documents/ThutaCortex) second brain for institutional memory, architectural pattern retrieval, and automated knowledge ingestion.

---

## 1. Team Hierarchy & Roles

```text
[Lead Technical Product Manager & Engineering Director] (Root Agent)
  │
  ├── [Collective Swarm Orchestrator (@cxagents)]                      ── Multi-agent collective swarm orchestrator (25 specialists)
  ├── [Principal Academic Researcher (@academic_researcher)]           ── Literature synthesis, experiment design, story-arc manuscripts
  ├── [Staff R&D Research Engineer (@rnd_researcher)]                  ── Academic search (arXiv), PDF analysis, web blogs
  ├── [Principal Systems Architect (@system_architect)]                ── Microservices, DDD, PostgreSQL DDL, Rust crate/FFI ABI contracts
  ├── [Senior UI/UX Engineer & Technologist (@uiux_designer)]          ── Wireframes, design tokens, Figma maps, WCAG AA
  ├── [Senior Frontend Engineer (@frontend_engineer)]                  ── Next.js, Material UI, TanStack, shadcn, SEO/GEO
  ├── [Senior Mobile Application Engineer (@mobile_engineer)]          ── Flutter & Dart, offline-first sync (Drift/Isar), platform channels
  ├── [Senior Backend Engineer (@backend_engineer)]                    ── Go Gin, Rust (Tokio/Axum/Tower/sqlx), Bun Express, Fastify, NestJS, Python
  ├── [Staff Rust Systems & Backend Engineer (@rust_engineer)]         ── Memory-safe Rust, Tokio/Axum, sqlx, C FFI, Aya/libbpf-rs
  ├── [Senior Software Engineer (@software_engineer)]                  ── Production implementation, Rust ownership/borrowing, integration, clean code
  ├── [Senior Business Central & AL Developer (@al_developer)]         ── Modern AL, event subscribers, ControlAddIns, telemetry
  ├── [Staff AI / ML Engineer (@ai_ml_engineer)]                       ── Prompt schemas, RAG parameters, eval test suites
  ├── [Staff MLOps & Inference Engineer (@mlops_engineer)]             ── vLLM, TensorRT-LLM, Triton, AWQ/FP8 quantization, KV-cache
  ├── [Staff AI Red Team & Safety Engineer (@ai_redteam_engineer)]     ── Prompt injection, tool hijacking fuzzing, multi-turn jailbreaks
  ├── [Staff Synthetic Data & Sim Engineer (@synthetic_data_engineer)] ── Telemetry simulation, fault cascades, differential privacy
  ├── [Staff Data Platform Engineer (@data_engineer)]                  ── Kafka, Flink, Spark 3.5.0, Rust Arrow/DataFusion/Polars, Iceberg, dbt
  ├── [Principal Database Administrator (@database_engineer)]          ── EXPLAIN ANALYZE BUFFERS, zero-downtime DDL, PgBouncer, TimescaleDB
  ├── [Senior DevOps & SRE (@devops_engineer)]                         ── Multi-stage Docker, Compose, Nginx, CI/CD, probes
  ├── [Principal Platform Engineer (@platform_engineer)]               ── Internal Developer Platforms, OpenTofu/Terraform, ArgoCD, Istio
  ├── [Staff Cloud FinOps Engineer (@finops_engineer)]                 ── Cloud unit economics, K8s workload rightsizing, spot fallback
  ├── [Staff Systems & eBPF Kernel Engineer (@ebpf_engineer)]          ── CO-RE C (libbpf) & Rust (Aya, libbpf-rs, bpf-linker), XDP/TC, lock tracing
  ├── [Staff Performance & Reliability Eng (@perf_engineer)]           ── k6/Locust, Rust Criterion (cargo bench), cargo-flamegraph, OpenTelemetry
  ├── [Staff Application Security Engineer (@appsec_engineer)]         ── STRIDE/DREAD, OAuth 2.1, KMS, cargo audit/cargo deny, unsafe/FFI gating
  ├── [Staff Compliance & Governance Eng (@compliance_engineer)]       ── SOC 2, HIPAA, GDPR, WORM audit logs, OPA/Rego compliance-as-code
  ├── [Senior QA & Evaluation Engineer (@qa_engineer)]                 ── Compilers, linters (cargo clippy/test, go test -race, pytest), exit-code-0
  └── [Staff Security & Code Reviewer (@code_reviewer)]                ── OWASP Top 10, Rust unsafe // SAFETY: & FFI audits, concurrency, clean code
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
│   ├── skills/                # Operational playbooks (SKILL.md) for all specialist roles
│   └── rules/AGENTS.md        # Global engineering guidelines & manuscript authoring rules
├── src/                       # Standalone Python framework
│   ├── dashboard.py           # Cross-platform live status & token telemetry dashboard
│   ├── main.py                # CLI runner and interactive driver
│   ├── team.py                # LocalAgentConfig assembler & orchestration policies
│   ├── agents/personas.py     # SubagentConfig definitions for all specialist roles and cxagents orchestrator
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

## 3. Multi-Platform Installation Runbooks

### Option 1: Native Plugin Installation Across AI Engines

CortexOps provides declarative plugin manifests for Anthropic Claude Code, OpenAI Codex, and Google Antigravity.

#### A. Anthropic Claude Code (`claude plugin install`)
To install CortexOps into Claude Code:
* **From GitHub (Recommended)**:
  ```bash
  claude plugin install ctxthuta/cortexops
  # or using the repository URL:
  claude plugin install https://github.com/ctxthuta/cortexops
  ```
* **From Local Directory / Workspace**:
  ```bash
  claude plugin install /path/to/cortexops
  # or inside the repository root:
  claude plugin install .
  ```
* **Via Marketplace Registry**:
  ```bash
  claude plugin marketplace add ctxthuta/cortexops
  claude plugin install cortexops
  ```
* **Verify & Update**:
  ```bash
  claude plugin list
  claude plugin update cortexops
  ```

#### B. OpenAI Codex (`codex plugin install`)
To install CortexOps into OpenAI Codex:
* **From GitHub (Recommended)**:
  ```bash
  codex plugin install ctxthuta/cortexops
  # or using the repository URL:
  codex plugin install https://github.com/ctxthuta/cortexops
  ```
* **From Local Directory / Workspace**:
  ```bash
  codex plugin install /path/to/cortexops
  # or inside the repository root:
  codex plugin install .
  ```
* **Verify Installation**:
  ```bash
  codex plugin list
  ```

#### C. Google Antigravity (`agy plugin install`)
* **macOS & Linux (Git URL or Local Folder)**:
  ```bash
  agy plugin install https://github.com/ctxthuta/cortexops/tree/main/plugin
  # or from local folder:
  agy plugin install ./plugin
  agy plugin list
  ```
* **Windows PowerShell (Release Archive Extraction)**:
  Because `agy` on Windows treats remote ZIP URLs as repository subfolders, download and expand the release archive before installation:
  ```powershell
  $cxopsDir = Join-Path $Env:Temp "cortexops-v1.1.7"
  Invoke-WebRequest -Uri "https://github.com/ctxthuta/cortexops/releases/download/v1.1.7/cortexops-1.1.7.zip" -OutFile "$cxopsDir.zip"
  Expand-Archive -Path "$cxopsDir.zip" -DestinationPath $cxopsDir -Force
  agy plugin install "$cxopsDir"
  agy plugin list
  ```
  Then restart VS Code / Antigravity.

---

### Option 2: Universal Node.js / NPM Package (`@ctxthuta/cxops`)
Works identically on Windows PowerShell, macOS, and Linux:
```bash
npm install -g @ctxthuta/cxops@latest
cxops link
cxops doctor
```
In any project folder open in your editor:
```bash
npx @ctxthuta/cxops@latest init
```

---

### Updating CortexOps on Windows (Upgrade Runbook)

When a new version of CortexOps is published, choose one of these verified update methods in Windows PowerShell:

#### Method 1: Global NPM Update (Recommended, 1-Liner)
If installed via npm, update globally and refresh the junction link:
```powershell
npm install -g @ctxthuta/cxops@latest
cxops link
cxops doctor
```
Then restart Google Antigravity / VS Code. The global link immediately points to the latest release assets.

#### Method 2: Direct Release Archive Update via Antigravity CLI
If updating using the GitHub release ZIP archive without npm:
```powershell
# Fetch and expand the latest release archive
$tag = (Invoke-RestMethod -Uri "https://api.github.com/repos/ctxthuta/cortexops/releases/latest").tag_name
$version = $tag.TrimStart("v")
$cxopsDir = Join-Path $Env:Temp "cortexops-$tag"
Invoke-WebRequest -Uri "https://github.com/ctxthuta/cortexops/releases/download/$tag/cortexops-$version.zip" -OutFile "$cxopsDir.zip"
Expand-Archive -Path "$cxopsDir.zip" -DestinationPath $cxopsDir -Force

# Re-install into Antigravity
agy plugin install "$cxopsDir"
agy plugin list
```
Then fully restart Google Antigravity / VS Code.

#### Method 3: Automated 1-Click Update CLI
If you have the `cxops` or `cx.ps1` CLI on your path:
```powershell
cxops update
# or in local repository:
.\cx.ps1 update
```

#### Method 4: Local Git Repository Pull (For Developer Workspaces)
If you cloned the repository locally:
```powershell
cd path\to\cortexops
git pull origin main
.\install.ps1
cxops verify
```

---

### macOS & Linux (Terminal / zsh / bash)

Because macOS and Linux use POSIX filesystem permissions, both methods work seamlessly without UAC or junction restrictions:

#### Method A: Global NPM Package + Symlink
```bash
npm install -g @ctxthuta/cxops@latest
cxops link
cxops doctor
```

#### Method B: Native Antigravity Git Install
```bash
agy plugin install https://github.com/ctxthuta/cortexops/tree/main/plugin
agy plugin list
```

---

### Automated Dual Release Pipeline
Every release is published simultaneously to both npm and GitHub Releases with binary assets in a single command:
```bash
npm run release [patch|minor|major]
```

---

## 4. Two Modes of Execution

### Mode A: Native Antigravity Subagents (No External API Key Required)
When working inside Google Antigravity (IDE or CLI):
- All 36 agents (35 specialists plus `@cxagents`) are loaded globally via the linked plugin (`~/.gemini/config/plugins/cortexops`) and locally in `.agents/`.
- Subagents execute directly through Antigravity's authenticated session.
- Mention individual specialists directly (`@rust_engineer`, `@backend_engineer`, `@system_architect`, `@code_reviewer`), or mention `@cxagents` to mobilize the entire relevant team concurrently.

```text
@rust_engineer Build a Tokio + Axum + Tower microservice with parameterized sqlx persistence, C FFI bindings, and Aya/libbpf-rs telemetry verified with cargo clippy -- -D warnings, cargo test, cargo audit, and cargo deny check.
```

<!--
### Mode B: Standalone Multi-Engine Framework (Terminal / CI / Headless)
When running outside Antigravity as an automated background process:
- Configure your preferred engine (default: antigravity):
  # Antigravity (Google DeepMind SDK, default)
  export GEMINI_API_KEY="your-gemini-api-key"

  # Claude (Anthropic)
  export ANTHROPIC_API_KEY="your-anthropic-api-key"

  # Codex (OpenAI)
  export OPENAI_API_KEY="your-openai-api-key"

- Run tasks with your preferred execution harness:
  # Default Antigravity engine (Gemini 3.8 models)
  cxops run "Research streaming anomaly detection and implement an in-memory detector with unit tests."

  # Anthropic Claude engine (Claude 3.7 / 3.5 Sonnet)
  cxops run -e claude "Design high-throughput event sourcing microservice."

  # OpenAI Codex engine (GPT-4o / o3-mini)
  cxops run -e codex "Generate relational PostgreSQL DDL with composite indexes."
-->

---

## 5. Cross-Laptop Setup & GitHub Synchronization

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

## 6. CLI Command Reference

Execute commands via `./cx [command]` (Linux/macOS) or `.\cx.ps1 [command]` (Windows):

```bash
# View live operational & token telemetry dashboard with ANSI colors
./cx status

# Continuously monitor session telemetry (auto-refresh)
./cx watch

# Verify all 26 declarative subagents and plugin link
./cx verify

# Re-run installation and link global plugin
./cx install

# Cleanly unregister subagents and remove local environment
./cx uninstall
```
