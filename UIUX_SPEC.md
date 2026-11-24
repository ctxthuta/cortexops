# UI/UX Specification: Global Agent Monitor (`agentmon`)

**Author:** Senior UI/UX Engineer & Figma Design Technologist (`uiux_designer`)  
**Context:** CortexOps Multi-Agent Collective (`cxagents`)  
**Specification Reference:** `Global_Agent_Monitor_BRD.docx` & `Global_Agent_Monitor_FRD.docx`  
**Date:** 24 November 2026  

---

## 1. Terminal Layout Wireframes

The Global Agent Monitor terminal dashboard dynamically adapts to two distinct viewport profiles: Wide Viewport ($\ge 120$ columns) and Standard Viewport ($80 \times 24$).

### 1.1 Wide Terminal Layout ($\ge 120 \times 30$ columns)

On wide screens, the interface partitions into a two-pane split: the Left Pane renders the Hierarchical Agent & Conversation Tree, while the Right Pane displays the Timestamped Chronological Timeline and Usage Breakdown.

```
+----------------------------------------------------------------------------------------------------------------------+
| GLOBAL AGENT MONITOR v1.2.1                       [Filter: All Projects]               Collector: HEALTHY (UDS 0.2ms)|
| Sessions: 5 Active | Running Agents: 7 | Attention Required: 1 | Token Usage: 3,450 reported (2 partial)            |
+----------------------------------------------------------------------------------------------------------------------+
| [1] OVERVIEW  |  [2] ATTENTION (1)  |  [3] CONVERSATIONS (5)  |  [4] USAGE  |  [5] SOURCES (4)                       |
+--------------------------------------------------------------------------+-------------------------------------------+
| HIERARCHICAL AGENT TOPOLOGY (Left Pane)                                  | ACTIVITY TIMELINE & CONTEXT (Right Pane)  |
+--------------------------------------------------------------------------+-------------------------------------------+
| [!] ATTENTION REQUIRED                                                   | Selected: Inventory Sync / Mapper         |
|   * Inventory Sync [Codex / CLI]                                         | Task: Schema Review & Migration           |
|     `-- [!] tester (Waiting for approval: write fixture) [2m 14s]        | Handoff from: planner                     |
|                                                                          | Status: RUNNING (Reading spec)            |
| [*] ACTIVE WORK                                                          |                                           |
|   v Inventory Sync [Antigravity / App]                                   | TIMELINE:                                 |
|     * planner (Idle - Delegated to Mapper)                               | 09:40:12 [START] Session initialized      |
|       `-- mapper (Running: reading mapping spec) [45s]                   | 09:40:18 [TOOL]  read_file (schema.sql)   |
|   v Billing API [Antigravity / VS Code]                                  | 09:41:05 [DELEG] Delegated to Mapper      |
|     `-- reviewer (Running: cargo test) [1m 02s]                          | 09:41:20 [TOOL]  read_file (mapping.spec) |
|   v Client Portal [Claude Code / CLI]                                    |                                           |
|     * lead_agent (Running)                                               | TOKEN ACCOUNTING:                         |
|       `-- forked_auditor (Turn completed) [Returned]                     | Agent Input:     1,200 tokens             |
|                                                                          | Agent Output:      350 tokens             |
| [-] UNASSIGNED / STANDALONE                                              | Cache Read:        400 tokens             |
|   `-- script_runner [agy CLI] (Idle)                                     | Scope:           Agent Turn (Verified)    |
+--------------------------------------------------------------------------+-------------------------------------------+
| [Enter] Inspect Row  |  [A] Jump to Attention  |  [/] Filter  |  [Space] Pause Scroll  |  [?] Help  |  [Q] Exit      |
+----------------------------------------------------------------------------------------------------------------------+
```

### 1.2 Standard 80x24 Viewport Layout (Single-Pane Responsive)

At $80 \times 24$, the interface automatically collapses to a clean single-pane viewport. The operator toggles between the Overview and Detail modes using `Enter` and `Esc`.

```
+------------------------------------------------------------------------------+
| AGENTMON v1.2.1             [All Projects]               Collector: HEALTHY  |
| Active: 5  |  Running: 7  |  Attention: 1  |  Usage: 3,450 tok               |
+------------------------------------------------------------------------------+
| ATTENTION (1)                                                                |
| ! Inventory Sync / Codex     | tester: Waiting approval (fixture)   | 2m 14s |
|                                                                              |
| ACTIVE RUNS (4)                                                              |
| * Inventory Sync / Antigrav  | mapper: reading mapping.spec         |    45s |
| * Billing API / VS Code      | reviewer: running cargo test         | 1m 02s |
| * Client Portal / Claude     | lead_agent: coordinating audit       | 3m 40s |
| - Unassigned / agy CLI       | script_runner: idle                  | 8m 10s |
|                                                                              |
| COVERAGE: Antigravity (OK) | Codex (OK) | Claude (OK) | Framework (OK)       |
+------------------------------------------------------------------------------+
| [A] Attention  [Enter] Detail  [/] Filter  [Space] Pause  [?] Help  [Q] Exit |
+------------------------------------------------------------------------------+
```

---

## 2. Component State Matrix

Every interactive element conforms to explicit visual specifications across all 8 standard component states:

| Component State | Visual Indicator (ANSI Color) | Monochrome / Reduced Motion Indicator | Interaction Behavior |
| :--- | :--- | :--- | :--- |
| **Default** | Normal text, muted grey separators | Plain text `[ ]`, standard indentation | Navigable via Up/Down arrow keys. |
| **Hover / Selected** | Inverted background (White on Dark Blue) | Angle bracket prefix `> ` or bold border | Cursor parked on row; `Enter` opens detail. |
| **Focus-Visible** | Highlighted cyan border around active pane | Double line border `║ ═` | Active pane for keyboard inputs. |
| **Active / Running** | Cyan / Green status badge | Asterisk prefix `* [RUNNING]` | Real-time elapsed time ticker updating every second. |
| **Attention / Waiting** | High-contrast Yellow / Amber badge | Exclamation prefix `! [ATTENTION]` | Automatically pinned to the top of overview. |
| **Disabled / Idle** | Dim grey text | Dash prefix `- [IDLE]` | Inactive session, retained for turn continuity. |
| **Loading / Spooling** | Pulsing cyan dot (wide) / `[SYNC]` | Text badge `[SYNCING]` (no pulsing) | Synchronizing buffered spool records. |
| **Error / Failed** | Bold Red badge `[FAILED]` | Cross prefix `x [FAILED]` | Detailed error message visible in right detail pane. |

---

## 3. Keyboard Shortcuts & Interaction Design

- **Navigation:** `Up` / `Down` arrows or `j` / `k` (Vim navigation) move row selection.
- **Drill Down / Inspect:** `Enter` switches from Overview to Conversation detail view.
- **Return / Back:** `Esc` or `Backspace` returns to the previous view with filter and selection preserved.
- **Attention Shortcut:** `A` jumps directly to the first row requiring user intervention.
- **Filter / Search:** `/` opens an interactive search input bar in the footer.
- **Scroll Pause:** `Space` toggles real-time scroll pausing without dropping background events.
- **View Toggles:** `1` (Overview), `2` (Attention), `3` (Conversations), `4` (Usage), `5` (Sources).
- **Executive Briefing:** `B` renders a pop-up factual briefing summarizing active work.
- **Command Palette:** `?` opens a searchable action palette.
- **Exit:** `q` or `Ctrl+C` exits cleanly, leaving the background collector daemon running.

---

## 4. Accessibility & Design Tokens

- **Monochrome & High Contrast:** All visual states include explicit textual badges (`!`, `*`, `-`, `x`), ensuring full operational clarity even on black-and-white serial terminals or colorblind setups.
- **Reduced Motion:** Configurable via `--no-motion` or auto-detected terminal capabilities; replaces pulsing indicators with static labels.
- **Spatial Grid:** Strict 2-line header, 1-line tab bar, expandable body, and 2-line footer status bar.
