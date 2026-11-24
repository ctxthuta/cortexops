# Invariant Ledger: Global Agent Monitor (`agentmon`)

**Author:** Principal Systems Integrator & Context Broker (`systems_integrator`)  
**Context:** CortexOps Multi-Agent Collective (`cxagents`)  
**Specification Traceability:** `Global_Agent_Monitor_BRD.docx` & `Global_Agent_Monitor_FRD.docx`  
**Date:** 24 November 2026  

---

## 1. System Invariant Master Catalog

The Invariant Ledger maintains hard contracts across all specialist engineering handoffs, eliminating semantic drift and ensuring compliance with the BRD and FRD.

| Invariant ID | Domain | Invariant Definition | Enforcement Mechanism |
| :--- | :--- | :--- | :--- |
| **INV-01** | User Isolation | The collector operates as an unprivileged, single-user daemon. Sockets, journals, and spool files must have POSIX mode `0600`. Cross-user IPC requests are rejected immediately. | Transport-level `SO_PEERCRED` check on Unix domain sockets; file system DAC permissions. |
| **INV-02** | Zero Tool Impact | When the collector daemon is offline or degraded, native client operations (Antigravity, Codex, Claude Code) must proceed unimpeded. Hook execution overhead must not exceed 100 ms P95. | Non-blocking socket connect with immediate fallback to local disk spooling (`spool.jsonl`). |
| **INV-03** | Data Privacy | Prompts, user messages, model thoughts, tool argument parameters, command execution outputs, and secrets are strictly forbidden from ingestion and persistence. | Strict compile-time and runtime field allowlist filter; payloads violating allowlists are stripped or rejected. |
| **INV-04** | ANSI Neutralization | All string fields displayed in the terminal UI must be stripped of terminal escape sequences to prevent cursor hijacking or command injection. | Regular expression ANSI escape sequence neutralizer executed on all string inputs prior to rendering. |
| **INV-05** | Deterministic Deduplication | Replaying identical events must produce an idempotent state projection. Duplicate event deliveries add zero to counts and totals. | Sliding 10,000-entry event hash set with sequence index verification. |
| **INV-06** | Out-of-Order DAG Safety | Child agent events arriving before their parent registration must be buffered and attached deterministically upon parent arrival without creating false root nodes. | Two-tier buffered adjacency map with orphan resolution queue. |
| **INV-07** | Honest Token Accounting | Missing token telemetry must be recorded as `unreported`. Coercing missing telemetry to `0` is strictly prohibited. An explicit `0` is accepted only when reported by the provider. | Scoped token ledger tracking `input`, `output`, `cached`, `reasoning`, scope type, and reporting status. |
| **INV-08** | Memory Footprint Ceiling | Collector daemon and terminal viewer combined must remain strictly below 200 MiB RSS under sustained load (100 agents, 20 events/sec). | In-memory compact sliding windows, virtualized viewport slicing, zero memory leaks. |
| **INV-09** | 80x24 Terminal Usability | The terminal dashboard must remain completely usable on standard 80 columns by 24 lines displays in monochrome mode without color dependencies. | Responsive single-pane / dual-pane layout switch with explicit text status labels. |
| **INV-10** | Replay & Purge Consistency | Purging a project permanently deletes all associated events from memory and disk. Subsequent replays or retries must never resurrect purged records. | Tombstone indexing with atomic WAL rewriting. |

---

## 2. Requirements Traceability Matrix

Mapping BRD Outcomes and FRD Functional Requirements to Acceptance Verification Tests:

| BRD Outcome | FRD Requirements | Acceptance Test ID | Verification Target |
| :--- | :--- | :--- | :--- |
| **B01** (Global View) / **B02** (Native Launch) | F01–F08, F20, F32 | **T01**, **T02**, **T07** | Native session discovery across 5 concurrent sessions in 3 projects; one viewer attaches to all. |
| **B03** (Collaboration) / **B05** (Attention) | F09–F14, F20–F24 | **T03**, **T05** | Parent-child tree resolution, handoff tracking, and waiting-for-input attention surfacing in < 10 seconds. |
| **B04** (Usage Attribution) | F09, F15–F19 | **T04**, **T09** | Scoped token accumulation, cache separation, reasoning deduplication, and honest `unreported` states. |
| **B06** (Framework Activation) | F03–F04, F31–F32 | **T03**, **T07** | CortexOps framework dispatches reflect real skill, agent, and tool lifecycles immediately. |
| **B07** (Continuity & Restarts) | F02, F10, F13–F14, F27–F30 | **T06**, **T10** | Closing/reopening viewer preserves state; collector restarts restore from WAL in < 1.5 seconds. |
| **B08** (Privacy & Responsiveness) | F25–F31 | **T07**, **T08**, **T10** | Zero sensitive data persistence; hook overhead < 100 ms; total RSS < 200 MiB under sustained load. |
| **B09** (Coverage Transparency) | F05–F08, F13, F30, F33 | **T01**, **T09**, **T10** | Capabilities displayed with explicit Verified, Partial, Unsupported, or Untested badges. |

---

## 3. Second Brain Integration (ThutaCortex)

In accordance with institutional memory standards, architectural patterns and data models established in `agentmon` are synchronized with `/home/lenovo/Documents/ThutaCortex`:
- Concept note reference: `Resources/Concepts/Global Agent Monitor Telemetry Architecture.md`.
- Architectural conventions adhere strictly to zero emojis, valid YAML frontmatter, and non-empty wikilinks.
