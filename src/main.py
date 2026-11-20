"""CLI Entrypoint for CortexOps Multi-Agent Framework."""

import asyncio
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def load_environment() -> None:
    """Discovers and loads environment variables from candidate .env files."""
    candidate_paths = [
        Path.cwd() / ".env",
        REPO_ROOT / ".env",
        Path.home() / ".cortexops" / ".env",
    ]
    for env_path in candidate_paths:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key, val = key.strip(), val.strip()
                            if key and key not in os.environ:
                                os.environ[key] = val
            except Exception:
                pass

load_environment()

from google.antigravity import Agent
from src.team import create_cortexops_team

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

async def run_task(prompt: str, model: str = DEFAULT_MODEL):
    """Runs a complete software engineering or research lifecycle task with the CortexOps team."""
    config = create_cortexops_team(model=model)
    
    print("=" * 70)
    print("CORTEXOPS MULTI-AGENT FRAMEWORK - ACTIVE")
    print("Roles: TPM Director | Staff R&D | Principal Architect | UI/UX | Frontend | Backend | DevOps | ML | QA | Reviewer | Academic Researcher | Software Engineer | cxagents")
    print(f"Model: {model}")
    print(f"Goal: {prompt}")
    print("=" * 70 + "\n")
    
    async with Agent(config) as team:
        response = await team.chat(prompt)
        print("\n" + "=" * 70)
        print("ENGINEERING OUTCOME:")
        print("=" * 70)
        async for chunk in response:
            print(chunk, end="", flush=True)
        print("\n")

def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("Enter the engineering project or feature request:")
        prompt = input("> ").strip()
        
    if not prompt:
        print("No task provided. Exiting.")
        sys.exit(1)
        
    asyncio.run(run_task(prompt))

if __name__ == "__main__":
    main()
