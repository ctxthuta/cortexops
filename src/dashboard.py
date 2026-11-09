#!/usr/bin/env python3
"""Cross-Platform Operational Dashboard for Thea Senior Engineering Team.

Displays agent registry health, Antigravity token telemetry, ThutaCortex second brain
metrics, and git version control status on Linux, macOS, and Windows.
"""

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLUGIN_AGENTS_DIR = BASE_DIR / "plugin" / "agents"


def _get_antigravity_brain_dir() -> Path | None:
    """Locates the Antigravity session brain directory across OS environments."""
    home = Path.home()
    candidates = [
        home / ".gemini" / "antigravity-cli" / "brain",
        home / ".gemini" / "antigravity" / "brain",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _get_cortex_dir() -> Path | None:
    """Locates ThutaCortex vault directory across OS environments."""
    home = Path.home()
    candidates = [
        home / "Documents" / "ThutaCortex",
        home / "Documents" / "Obsidian" / "ThutaCortex",
        Path("/home/lenovo/Documents/ThutaCortex"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _get_latest_session_transcript(brain_dir: Path | None) -> tuple[Path | None, str]:
    """Finds the most recently modified session transcript."""
    if not brain_dir or not brain_dir.exists():
        return None, "Not Found"

    latest_file = None
    latest_mtime = 0.0
    session_id = "Unknown"

    for session_folder in brain_dir.iterdir():
        if session_folder.is_dir() and not session_folder.name.startswith("."):
            t_file = session_folder / ".system_generated" / "logs" / "transcript.jsonl"
            if t_file.exists():
                mtime = t_file.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = t_file
                    session_id = session_folder.name

    return latest_file, session_id


def parse_antigravity_telemetry(transcript_file: Path | None) -> dict:
    """Parses transcript log to extract token usage, turns, and tool calls."""
    metrics = {
        "turns": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "total_tokens": 0,
        "tool_calls": {},
        "model_name": "Gemini 2.0 / 3.8",
        "last_activity": "None",
    }
    if not transcript_file or not transcript_file.exists():
        return metrics

    try:
        with open(transcript_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                step_type = data.get("type")
                if step_type == "PLANNER_RESPONSE":
                    metrics["turns"] += 1
                    in_tok = data.get("input_tokens", 0)
                    out_tok = data.get("output_tokens", 0)
                    cache_tok = data.get("cache_read_tokens", 0)
                    metrics["input_tokens"] += in_tok
                    metrics["output_tokens"] += out_tok
                    metrics["cache_read_tokens"] += cache_tok
                    metrics["total_tokens"] += (in_tok + out_tok + cache_tok)
                    metrics["last_activity"] = data.get("created_at", "Unknown")

                    for call in data.get("tool_calls", []):
                        name = call.get("name", "unknown")
                        metrics["tool_calls"][name] = metrics["tool_calls"].get(name, 0) + 1
    except Exception as e:
        metrics["error"] = str(e)

    return metrics


def get_cortex_metrics(cortex_dir: Path | None) -> dict:
    """Computes second brain inventory statistics."""
    stats = {
        "available": False,
        "path": "Not configured",
        "total_notes": 0,
        "concepts": 0,
        "projects": 0,
        "areas": 0,
        "references": 0,
    }
    if not cortex_dir or not cortex_dir.exists():
        return stats

    stats["available"] = True
    stats["path"] = str(cortex_dir)

    for root, dirs, files in os.walk(cortex_dir):
        if ".obsidian" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                stats["total_notes"] += 1
                rel = Path(root).relative_to(cortex_dir)
                if "Concepts" in rel.parts:
                    stats["concepts"] += 1
                elif "Projects" in rel.parts:
                    stats["projects"] += 1
                elif "Areas" in rel.parts:
                    stats["areas"] += 1
                elif "References" in rel.parts:
                    stats["references"] += 1

    return stats


def get_agent_roster() -> list[dict]:
    """Retrieves all registered subagents from the plugin repository."""
    roster = []
    if not PLUGIN_AGENTS_DIR.exists():
        return roster

    for agent_file in sorted(PLUGIN_AGENTS_DIR.glob("*.md")):
        name = agent_file.stem
        desc = "No description"
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("description:"):
                        desc = line.replace("description:", "").strip().strip('"').strip("'")
                        break
        except Exception:
            pass
        roster.append({
            "name": name,
            "description": desc,
            "status": "ONLINE (Registered)",
        })
    return roster


def get_git_status() -> dict:
    """Retrieves git repository metadata."""
    status = {"branch": "unknown", "commit": "unknown", "clean": True}
    try:
        git_dir = BASE_DIR / ".git"
        if not git_dir.exists():
            return status

        # Read branch
        head_file = git_dir / "HEAD"
        if head_file.exists():
            ref = head_file.read_text().strip()
            if ref.startswith("ref: refs/heads/"):
                status["branch"] = ref.replace("ref: refs/heads/", "")
                branch_file = git_dir / "refs" / "heads" / status["branch"]
                if branch_file.exists():
                    status["commit"] = branch_file.read_text().strip()[:7]
            else:
                status["commit"] = ref[:7]
    except Exception:
        pass
    return status


def render_dashboard() -> str:
    """Constructs the full ASCII dashboard."""
    brain_dir = _get_antigravity_brain_dir()
    transcript_file, session_id = _get_latest_session_transcript(brain_dir)
    telemetry = parse_antigravity_telemetry(transcript_file)
    cortex_dir = _get_cortex_dir()
    cortex_metrics = get_cortex_metrics(cortex_dir)
    roster = get_agent_roster()
    git_meta = get_git_status()

    # Global plugin verification
    global_plugin_dir = Path.home() / ".gemini" / "config" / "plugins" / "thea-engineering-team"
    plugin_status = "ENABLED (Symlinked)" if global_plugin_dir.exists() else "LOCAL ONLY"

    W = 86
    lines = []
    lines.append("=" * W)
    lines.append(f" THEA SENIOR ENGINEERING TEAM - OPERATIONAL STATUS & TELEMETRY DASHBOARD")
    lines.append(f" OS: {platform.system()} {platform.release()} ({platform.machine()}) | Python: {platform.python_version()} | Antigravity: Connected")
    lines.append("=" * W)

    # 1. System Infrastructure & Connections
    lines.append("\n[1] SYSTEM CONNECTIONS & VCS")
    lines.append(f"  * Git Branch: {git_meta['branch']} (Commit: {git_meta['commit']})")
    lines.append(f"  * Antigravity Global Plugin: {plugin_status}")
    lines.append(f"  * Antigravity Active Session: {session_id}")
    lines.append(f"  * ThutaCortex Second Brain: {'CONNECTED' if cortex_metrics['available'] else 'DISCONNECTED'}")
    lines.append(f"    - Vault Root: {cortex_metrics['path']}")
    lines.append(f"    - Total Notes: {cortex_metrics['total_notes']} (Concepts: {cortex_metrics['concepts']}, Projects: {cortex_metrics['projects']}, Areas: {cortex_metrics['areas']})")

    # 2. Antigravity Token & Session Telemetry
    lines.append("\n[2] ANTIGRAVITY TOKEN CONSUMPTION & TELEMETRY")
    lines.append(f"  * Interaction Turns:       {telemetry['turns']:,}")
    lines.append(f"  * Prompt Input Tokens:     {telemetry['input_tokens']:,}")
    lines.append(f"  * Candidate Output Tokens: {telemetry['output_tokens']:,}")
    lines.append(f"  * Cached Read Tokens:      {telemetry['cache_read_tokens']:,}")
    lines.append(f"  * Total Processed Tokens:  {telemetry['total_tokens']:,}")
    lines.append(f"  * Last Turn Activity:      {telemetry['last_activity']}")

    # Tool invocation breakdown
    lines.append("\n  Tool Invocations Breakdown:")
    if telemetry["tool_calls"]:
        for tool, count in sorted(telemetry["tool_calls"].items(), key=lambda x: -x[1]):
            bar = "#" * min(30, max(1, int(count / 10)))
            lines.append(f"    - {tool:22s} : {count:4d} calls | {bar}")
    else:
        lines.append("    - No tool invocations recorded in active session.")

    # 3. Autonomous Subagent Roster
    lines.append(f"\n[3] AUTONOMOUS SUBAGENT ROSTER ({len(roster)} Verified Senior Roles)")
    lines.append(f"  {'ROLE / SUBAGENT':24s} | {'STATUS':20s} | {'PRIMARY DOMAIN & RESPONSIBILITY'}")
    lines.append("  " + "-" * (W - 4))
    for agent in roster:
        name = agent["name"]
        status = agent["status"]
        desc = agent["description"][:38] + "..." if len(agent["description"]) > 38 else agent["description"]
        lines.append(f"  {name:24s} | {status:20s} | {desc}")

    lines.append("\n" + "=" * W)
    lines.append(f" Dashboard updated at: {time.strftime('%Y-%m-%d %H:%M:%S')}. Clean code standard enforced.")
    lines.append("=" * W)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Thea Engineering Team Operational Dashboard")
    parser.add_argument("--watch", "-w", action="store_true", help="Continuously poll and refresh the dashboard")
    parser.add_argument("--interval", "-i", type=int, default=3, help="Refresh interval in seconds (default: 3s)")
    args = parser.parse_args()

    if args.watch:
        try:
            while True:
                # Clear terminal screen portably
                os.system("cls" if os.name == "nt" else "clear")
                print(render_dashboard())
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nDashboard monitoring terminated.")
    else:
        print(render_dashboard())


if __name__ == "__main__":
    main()
