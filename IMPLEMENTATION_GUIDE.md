# Thea Senior Engineering Team: Cross-Platform Implementation Guide

This guide details how to install, synchronize, and monitor the autonomous **Thea Senior Engineering Team** across **Linux, macOS, and Windows** environments, with direct connections to **Google Antigravity** and the **ThutaCortex Second Brain**.

---

## 1. System Architecture & Interconnections

The framework operates across three tightly integrated layers:

```text
+-----------------------------------------------------------------------------------+
|                            GOOGLE ANTIGRAVITY ENGINE                              |
|   (CLI & IDE Sessions / Authenticated Gemini 2.0 / Zero Separate API Keys Needed)  |
+-----------------------------------------------------------------------------------+
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
+---------------------------------+             +----------------------------------+
|    AUTONOMOUS SUBAGENT TEAM     |             |     THUTACORTEX SECOND BRAIN     |
|   11 Senior/Staff Subagents     |<----------->|    (/Documents/ThutaCortex)      |
|  - academic_researcher          | search_     |  - Projects/ (System Schemas)    |
|  - rnd_researcher               | cortex      |  - Resources/Concepts/ (Zettels) |
|  - system_architect             | read_note   |  - Areas/Thea-Solutions/ (MOCs)  |
|  - uiux_designer                | ingest_     |  - Invariant: Zero Emojis        |
|  - frontend_engineer            | concept     |  - Linter: lint_vault.py         |
|  - backend_engineer             |             +----------------------------------+
|  - devops_engineer              |                              │
|  - ai_ml_engineer               |                     CouchDB Sync (VPS)
|  - qa_engineer                  |                              │
|  - code_reviewer                |                              ▼
|  - software_engineer            |             +----------------------------------+
+---------------------------------+             | https://thutacortex.theasolutions|
                 ▲                              +----------------------------------+
                 │
+-----------------------------------------------------------------------------------+
|                       CROSS-PLATFORM OPERATIONAL CLI & DASHBOARD                  |
|        Linux / macOS: ./thea dashboard    |    Windows: .\thea.ps1 dashboard      |
|   - Real-Time Token Telemetry (Input, Output, Cached Reads, Total Processed)      |
|   - Tool Execution Frequency & Subagent Dispatch Counters                         |
|   - Second Brain Vault Ingestion Stats & Git VCS Synchronization                  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Linux & macOS: 1-Command Installation

### Single-Command Setup
Open your terminal and run:

```bash
git clone https://github.com/ctxthuta/thea-engineering-team.git && cd thea-engineering-team && ./install.sh
```

### What `install.sh` Does Under the Hood:
1. Validates `python3` (Python 3.10+) and initializes the isolated virtual environment (`.venv/`).
2. Installs required production dependencies (`google-antigravity`, `pydantic`, `httpx`, `beautifulsoup4`, `pypdf`).
3. Links the global Antigravity plugin:
   ```bash
   ln -sfn "$PWD/plugin" "$HOME/.gemini/config/plugins/thea-engineering-team"
   ```
4. Verifies all 11 subagents and tests connectivity to ThutaCortex at `~/Documents/ThutaCortex`.

---

## 3. Windows (PowerShell): 1-Command Installation

### Single-Command Setup
Open PowerShell and run:

```powershell
git clone https://github.com/ctxthuta/thea-engineering-team.git; cd thea-engineering-team; .\install.ps1
```

*(If PowerShell script execution is restricted, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### What `install.ps1` Does Under the Hood:
1. Validates Python and initializes `.venv\Scripts\python.exe`.
2. Upgrades `pip` and installs `requirements.txt`.
3. Creates a native NTFS Directory Junction linking the plugin to Antigravity without requiring administrator rights:
   ```powershell
   cmd /c "mklink /J `"$env:USERPROFILE\.gemini\config\plugins\thea-engineering-team`" `"$PWD\plugin`""
   ```
4. Detects ThutaCortex at `$env:USERPROFILE\Documents\ThutaCortex`.
5. Executes `verify_agents.py` to confirm all 11 subagents are live.

---

## 4. Operational CLI & Token Telemetry Dashboard

The framework includes a cross-platform dashboard that reads Antigravity session transcripts and displays live token consumption, tool execution statistics, second brain health, and agent statuses.

### Command Quick Reference

| Action | Linux / macOS | Windows PowerShell |
| :--- | :--- | :--- |
| **View Dashboard Snapshot** | `./thea dashboard` or `./thea status` | `.\thea.ps1 dashboard` |
| **Live Continuous Monitoring** | `./thea watch` | `.\thea.ps1 watch` |
| **Verify Agents & Plugins** | `./thea verify` | `.\thea.ps1 verify` |
| **Re-Run Installer** | `./thea install` | `.\thea.ps1 install` |
| **Clean Uninstall** | `./thea uninstall` | `.\thea.ps1 uninstall` |
| **Dispatch Multi-Agent Goal** | `./thea run "<prompt>"` | `.\thea.ps1 run "<prompt>"` |

### Dashboard Output Example

```text
======================================================================================
 THEA SENIOR ENGINEERING TEAM - OPERATIONAL STATUS & TELEMETRY DASHBOARD
 OS: Linux 7.0.0-42-generic (x86_64) | Python: 3.12.3 | Antigravity: Connected
======================================================================================

[1] SYSTEM CONNECTIONS & VCS
  * Git Branch: main (Commit: a1f460e)
  * Antigravity Global Plugin: ENABLED (Symlinked)
  * Antigravity Active Session: 5f654337-e598-4c53-86bd-dc3f0f8bccad
  * ThutaCortex Second Brain: CONNECTED
    - Vault Root: /home/lenovo/Documents/ThutaCortex
    - Total Notes: 33 (Concepts: 7, Projects: 9, Areas: 6)

[2] ANTIGRAVITY TOKEN CONSUMPTION & TELEMETRY
  * Interaction Turns:       548
  * Prompt Input Tokens:     3,500,149
  * Candidate Output Tokens: 319,660
  * Cached Read Tokens:      67,153,389
  * Total Processed Tokens:  70,973,198
  * Last Turn Activity:      2026-11-09T09:40:20Z

  Tool Invocations Breakdown:
    - run_command            :  304 calls | ##############################
    - write_file             :   92 calls | #########
    - read_file              :   46 calls | ####
    - edit_file              :   30 calls | ###
    - manage_task            :   13 calls | #
    - define_subagent        :   10 calls | #
    - invoke_subagent        :    1 calls | #

[3] AUTONOMOUS SUBAGENT ROSTER (11 Verified Senior Roles)
  ROLE / SUBAGENT          | STATUS               | PRIMARY DOMAIN & RESPONSIBILITY
  ----------------------------------------------------------------------------------
  academic_researcher      | ONLINE (Registered)  | Principal Academic Research Scientist ...
  ai_ml_engineer           | ONLINE (Registered)  | Staff AI/ML Engineer. Designs prompt s...
  backend_engineer         | ONLINE (Registered)  | Senior Backend Engineer. Builds high-t...
  code_reviewer            | ONLINE (Registered)  | Staff Security & Code Reviewer. Audits...
  devops_engineer          | ONLINE (Registered)  | Senior DevOps & SRE. Authors multi-sta...
  frontend_engineer        | ONLINE (Registered)  | Senior Frontend Engineer. Builds React...
  qa_engineer              | ONLINE (Registered)  | Senior QA & Evaluation Engineer. Execu...
  rnd_researcher           | ONLINE (Registered)  | Staff R&D Research Engineer. Researche...
  software_engineer        | ONLINE (Registered)  | Senior Software Engineer. Implements p...
  system_architect         | ONLINE (Registered)  | Principal Systems Architect. Formulate...
  uiux_designer            | ONLINE (Registered)  | Senior UI/UX Engineer & Design Technol...
======================================================================================
```

---

## 5. Working with Subagents Inside Antigravity

When working in Antigravity (IDE or CLI), all 11 subagents are pre-mounted. You can delegate directly:

* **Academic Research & Manuscripts:**  
  `@academic_researcher Draft an experimental methodology and LaTeX section comparing our streaming anomaly detection model against OmniAnomaly on the GAIA benchmark.`
* **Microservices & Backend Systems:**  
  `@backend_engineer Implement a high-throughput Go Gin REST endpoint with row-level locking for table orders in Dineo.`
* **Frontend, UI/UX & SEO/GEO:**  
  `@frontend_engineer Build the responsive Next.js booking summary component for Nimbus using shadcn/ui and inject Schema.org JSON-LD structured data.`
* **UI/UX Design Tokens & Wireframes:**  
  `@uiux_designer Generate the design token schema and ASCII layout wireframe for the Specimen X clinical accessioning screen.`
* **DevOps & Containers:**  
  `@devops_engineer Author a multi-stage Dockerfile and Nginx reverse proxy configuration with Cloudflare edge caching for our microservices.`
* **Quality Assurance & Verification:**  
  `@qa_engineer Execute our test suites with race detector enabled and triage any failing tests.`
* **Security & Code Review:**  
  `@code_reviewer Audit the latest commit for OWASP Top 10 vulnerabilities and concurrency hazards.`

---

## 6. ThutaCortex Second Brain Integration

Agents query and update ThutaCortex using dedicated tools in `src/tools/cortex_tools.py`:

* `search_cortex(query)`: Finds relevant notes, architectures, and past decisions across `Projects/`, `Resources/Concepts/`, and `Areas/`.
* `read_cortex_note(relative_path)`: Reads full note content (e.g. `Projects/Specimen-X.md`).
* `ingest_concept_to_cortex(title, content, domain_tag, up_link, related)`: Validates zero-emoji compliance and saves atomic concept notes into `Resources/Concepts/`.

### Vault Linting
To verify vault integrity and zero-emoji compliance:

```bash
python3 ~/.gemini/config/skills/thutacortex/scripts/lint_vault.py
```

---

## 7. Clean Uninstallation (Linux, macOS, and Windows)

If you ever wish to unregister the subagents and remove installed artifacts, the framework provides a clean, automated uninstaller:

### On Linux & macOS
```bash
# Standard clean uninstall (unlinks Antigravity plugin, removes .venv and caches)
./thea uninstall

# Non-interactive mode
./thea uninstall -y

# Full purge (uninstalls and deletes the local repository folder)
./thea uninstall -y --purge
```

### On Windows (PowerShell)
```powershell
# Standard clean uninstall
.\thea.ps1 uninstall

# Non-interactive mode
.\thea.ps1 uninstall -Force

# Full purge
.\thea.ps1 uninstall -Force -Purge
```

### What Uninstallation Cleans Up:
1. **Unlinks Antigravity Plugin:** Deletes the global symlink or NTFS directory junction (`~/.gemini/config/plugins/thea-engineering-team`), immediately unregistering all 11 subagents.
2. **Removes Python Virtual Environment:** Purges `.venv/` to reclaim storage.
3. **Deletes Caches and Artifacts:** Cleans up `__pycache__/`, `*.pyc`, and scratch workspace files.
4. **Preserves Second Brain Notes:** Notes in `~/Documents/ThutaCortex` remain untouched and safe.

---

## 8. Troubleshooting & Verification

1. **Subagents Not Visible in Antigravity:**  
   Check the plugin symlink:
   - Linux: `ls -la ~/.gemini/config/plugins/thea-engineering-team`
   - Windows: `dir "$env:USERPROFILE\.gemini\config\plugins\thea-engineering-team"`
   If missing, run `./install.sh` (Linux) or `.\install.ps1` (Windows).
2. **Missing Token Telemetry in Dashboard:**  
   The dashboard automatically parses the most recent transcript in `~/.gemini/antigravity-cli/brain/`. If running on a new machine with no conversations yet, it displays 0 turns until the first turn occurs.
3. **Strict Zero-Emoji Rule:**  
   Enforced across all repository files, commits, and Obsidian notes. If `lint_vault.py` reports any emoji, replace it with ASCII text (`->`, `*`, `[x]`).
