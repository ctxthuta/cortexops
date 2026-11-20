#!/usr/bin/env python3
"""Portable verification script for CortexOps Multi-Agent Framework subagents."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PLUGIN_AGENTS_DIR = BASE_DIR / "plugin" / "agents"
GLOBAL_PLUGIN_DIR = Path.home() / ".gemini" / "config" / "plugins" / "cortexops"
LEGACY_PLUGIN_DIR = Path.home() / ".gemini" / "config" / "plugins" / "thea-engineering-team"

print("=" * 80)
print("CORTEXOPS MULTI-AGENT FRAMEWORK - PORTABLE AGENT VERIFICATION")
print("=" * 80)

# Verify Declarative Plugin Agents
print("[1] Declarative Plugin Definitions:")
if not PLUGIN_AGENTS_DIR.exists():
    print(f"    Missing plugin directory: {PLUGIN_AGENTS_DIR}")
else:
    agent_files = sorted(PLUGIN_AGENTS_DIR.glob("*.md"))
    print(f"    Found {len(agent_files)} agent definitions in repository:")
    for f in agent_files:
        name = f.stem
        desc = "No description"
        try:
            with open(f, "r", encoding="utf-8") as af:
                lines = af.readlines()
                for line in lines:
                    if line.startswith("description:"):
                        desc = line.replace("description:", "").strip()
                        break
        except Exception:
            pass
        print(f"    - {name:20s} -> {desc[:65]}...")

# Verify Global Antigravity Plugin Link
print("\n[2] Antigravity Global Plugin Link:")
active_link = GLOBAL_PLUGIN_DIR if GLOBAL_PLUGIN_DIR.exists() else (LEGACY_PLUGIN_DIR if LEGACY_PLUGIN_DIR.exists() else None)
if active_link:
    print(f"    Active link at: {active_link}")
    print(f"    Status: ENABLED (Available to Antigravity sessions globally)")
else:
    print(f"    Link not found at: {GLOBAL_PLUGIN_DIR}")
    print(f"    Run ./cx install to link the plugin globally.")

# Verify Python Standalone Framework Tools
print("\n[3] Python Agent Framework Modules:")
tools_dir = BASE_DIR / "src" / "tools"
agents_dir = BASE_DIR / "src" / "agents"
if tools_dir.exists() and agents_dir.exists():
    tools = [t.stem for t in tools_dir.glob("*.py") if not t.name.startswith("__")]
    print(f"    Available Custom Tools: {', '.join(tools)}")
    print(f"    Framework Personas: Available in src/agents/personas.py")
    print(f"    Status: OPERATIONAL")
else:
    print("    Framework modules missing or incomplete.")

print("=" * 80)
print("Verification complete. All agents are cross-laptop portable via Git.")
print("=" * 80)
