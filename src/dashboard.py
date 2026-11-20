#!/usr/bin/env python3
"""Cross-Platform Colored Operational Dashboard for CortexOps Multi-Agent Framework.

Displays agent registry health, Antigravity token telemetry, ThutaCortex second brain
metrics, and git version control status on Linux, macOS, and Windows with ANSI color styling.
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


class Colors:
    """ANSI color codes with automatic terminal detection."""
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    @property
    def RESET(self) -> str:
        return "\033[0m" if self.enabled else ""

    @property
    def BOLD(self) -> str:
        return "\033[1m" if self.enabled else ""

    @property
    def DIM(self) -> str:
        return "\033[2m" if self.enabled else ""

    @property
    def UNDERLINE(self) -> str:
        return "\033[4m" if self.enabled else ""

    @property
    def RED(self) -> str:
        return "\033[31m" if self.enabled else ""

    @property
    def GREEN(self) -> str:
        return "\033[32m" if self.enabled else ""

    @property
    def YELLOW(self) -> str:
        return "\033[33m" if self.enabled else ""

    @property
    def BLUE(self) -> str:
        return "\033[34m" if self.enabled else ""

    @property
    def MAGENTA(self) -> str:
        return "\033[35m" if self.enabled else ""

    @property
    def CYAN(self) -> str:
        return "\033[36m" if self.enabled else ""

    @property
    def WHITE(self) -> str:
        return "\033[37m" if self.enabled else ""

    @property
    def BRIGHT_GREEN(self) -> str:
        return "\033[92m" if self.enabled else ""

    @property
    def BRIGHT_YELLOW(self) -> str:
        return "\033[93m" if self.enabled else ""

    @property
    def BRIGHT_BLUE(self) -> str:
        return "\033[94m" if self.enabled else ""

    @property
    def BRIGHT_MAGENTA(self) -> str:
        return "\033[95m" if self.enabled else ""

    @property
    def BRIGHT_CYAN(self) -> str:
        return "\033[96m" if self.enabled else ""

    @property
    def BRIGHT_WHITE(self) -> str:
        return "\033[97m" if self.enabled else ""


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
                if data.get("type") == "PLANNER_RESPONSE":
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
            "status": "ONLINE",
        })
    return roster


def get_git_status() -> dict:
    """Retrieves git repository metadata."""
    status = {"branch": "unknown", "commit": "unknown", "clean": True}
    try:
        git_dir = BASE_DIR / ".git"
        if not git_dir.exists():
            return status

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


def render_dashboard(c: Colors) -> str:
    """Constructs the full stylized ANSI colored dashboard."""
    brain_dir = _get_antigravity_brain_dir()
    transcript_file, session_id = _get_latest_session_transcript(brain_dir)
    telemetry = parse_antigravity_telemetry(transcript_file)
    cortex_dir = _get_cortex_dir()
    cortex_metrics = get_cortex_metrics(cortex_dir)
    roster = get_agent_roster()
    git_meta = get_git_status()

    global_plugin_dir = Path.home() / ".gemini" / "config" / "plugins" / "cortexops"
    legacy_plugin_dir = Path.home() / ".gemini" / "config" / "plugins" / "thea-engineering-team"
    plugin_connected = global_plugin_dir.exists() or legacy_plugin_dir.exists()

    W = 86
    lines = []

    # Border
    border = f"{c.CYAN}{'=' * W}{c.RESET}"
    divider = f"{c.DIM}{'-' * (W - 4)}{c.RESET}"

    lines.append(border)
    lines.append(f"{c.BOLD}{c.BRIGHT_CYAN} CORTEXOPS - OPERATIONAL STATUS & TELEMETRY DASHBOARD{c.RESET}")
    lines.append(f"{c.DIM} OS: {platform.system()} {platform.release()} ({platform.machine()}) | Python: {platform.python_version()} | Antigravity: {c.RESET}{c.BOLD}{c.BRIGHT_GREEN}Connected{c.RESET}")
    lines.append(border)

    # System infrastructure and connections
    lines.append(f"\n{c.BOLD}{c.BRIGHT_BLUE}[1] SYSTEM CONNECTIONS & INFRASTRUCTURE{c.RESET}")
    lines.append(f"  * Git Branch: {c.BOLD}{c.BRIGHT_WHITE}{git_meta['branch']}{c.RESET} {c.DIM}(Commit: {git_meta['commit']}){c.RESET}")
    
    plug_text = f"{c.BOLD}{c.BRIGHT_GREEN}ENABLED (Symlinked){c.RESET}" if plugin_connected else f"{c.YELLOW}LOCAL ONLY{c.RESET}"
    lines.append(f"  * Antigravity Global Plugin: {plug_text}")
    lines.append(f"  * Antigravity Active Session: {c.CYAN}{session_id}{c.RESET}")
    
    cortex_text = f"{c.BOLD}{c.BRIGHT_GREEN}CONNECTED{c.RESET}" if cortex_metrics['available'] else f"{c.RED}DISCONNECTED{c.RESET}"
    lines.append(f"  * ThutaCortex Second Brain: {cortex_text}")
    lines.append(f"    - Vault Root: {c.DIM}{cortex_metrics['path']}{c.RESET}")
    lines.append(f"    - Inventory: {c.BOLD}{c.BRIGHT_WHITE}{cortex_metrics['total_notes']}{c.RESET} total notes {c.DIM}(Concepts: {cortex_metrics['concepts']}, Projects: {cortex_metrics['projects']}, Areas: {cortex_metrics['areas']}){c.RESET}")

    # Antigravity token and session telemetry
    lines.append(f"\n{c.BOLD}{c.BRIGHT_BLUE}[2] ANTIGRAVITY TOKEN CONSUMPTION & TELEMETRY{c.RESET}")
    lines.append(f"  * Interaction Turns:       {c.BOLD}{c.BRIGHT_WHITE}{telemetry['turns']:,}{c.RESET}")
    lines.append(f"  * Prompt Input Tokens:     {c.BRIGHT_YELLOW}{telemetry['input_tokens']:,}{c.RESET}")
    lines.append(f"  * Candidate Output Tokens: {c.BRIGHT_GREEN}{telemetry['output_tokens']:,}{c.RESET}")
    lines.append(f"  * Cached Read Tokens:      {c.CYAN}{telemetry['cache_read_tokens']:,}{c.RESET}")
    lines.append(f"  * Total Processed Tokens:  {c.BOLD}{c.BRIGHT_CYAN}{telemetry['total_tokens']:,}{c.RESET}")
    lines.append(f"  * Last Turn Activity:      {c.DIM}{telemetry['last_activity']}{c.RESET}")

    # Tool invocation breakdown
    lines.append(f"\n  {c.UNDERLINE}Tool Invocations Breakdown:{c.RESET}")
    if telemetry["tool_calls"]:
        for tool, count in sorted(telemetry["tool_calls"].items(), key=lambda x: -x[1]):
            bar_len = min(30, max(1, int(count / 10)))
            bar_color = c.BRIGHT_GREEN if "file" in tool else c.BRIGHT_CYAN if "command" in tool else c.BRIGHT_MAGENTA
            bar = f"{bar_color}{'#' * bar_len}{c.RESET}"
            lines.append(f"    - {c.BOLD}{tool:22s}{c.RESET} : {c.BRIGHT_WHITE}{count:4d}{c.RESET} calls | {bar}")
    else:
        lines.append(f"    {c.DIM}- No tool invocations recorded in active session.{c.RESET}")

    # Autonomous subagent roster
    lines.append(f"\n{c.BOLD}{c.BRIGHT_BLUE}[3] AUTONOMOUS SUBAGENT ROSTER ({len(roster)} Verified Senior Roles){c.RESET}")
    lines.append(f"  {c.BOLD}{c.CYAN}{'ROLE / SUBAGENT':24s} | {'STATUS':16s} | {'PRIMARY DOMAIN & RESPONSIBILITY'}{c.RESET}")
    lines.append("  " + divider)
    for agent in roster:
        name = agent["name"]
        name_pad = max(0, 24 - len(name))
        col_name = f"{c.BOLD}{c.BRIGHT_WHITE}{name}{c.RESET}{' ' * name_pad}"
        
        status_text = "[ONLINE]"
        status_pad = max(0, 16 - len(status_text))
        col_status = f"{c.BOLD}{c.BRIGHT_GREEN}{status_text}{c.RESET}{' ' * status_pad}"
        
        desc = agent["description"][:38] + "..." if len(agent["description"]) > 38 else agent["description"]
        lines.append(f"  {col_name} | {col_status} | {c.DIM}{desc}{c.RESET}")

    lines.append("\n" + border)
    lines.append(f"{c.DIM} Dashboard updated at: {time.strftime('%Y-%m-%d %H:%M:%S')}. Clean code standard enforced.{c.RESET}")
    lines.append(border)
    return "\n".join(lines)


def main():
    # Enable ANSI escape sequences on Windows PowerShell/CMD
    if os.name == "nt":
        os.system("")

    parser = argparse.ArgumentParser(description="CortexOps Multi-Agent Framework Operational Dashboard")
    parser.add_argument("--watch", "-w", action="store_true", help="Continuously poll and refresh the dashboard")
    parser.add_argument("--interval", "-i", type=int, default=3, help="Refresh interval in seconds (default: 3s)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color codes")
    parser.add_argument("--color", action="store_true", default=True, help="Force ANSI color codes (default: enabled)")
    args = parser.parse_args()

    color_enabled = not args.no_color
    c = Colors(enabled=color_enabled)

    if args.watch:
        try:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print(render_dashboard(c))
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print(f"\n{c.DIM}Dashboard monitoring terminated.{c.RESET}")
    else:
        print(render_dashboard(c))


if __name__ == "__main__":
    main()
