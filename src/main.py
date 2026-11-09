"""CLI Entrypoint for CortexOps Multi-Agent Framework."""

import asyncio
import sys
import os
from google.antigravity import Agent
from src.team import create_cortexops_team

async def run_task(prompt: str, model: str = "gemini-2.0-flash"):
    """Runs a complete software engineering or research lifecycle task with the CortexOps team."""
    config = create_cortexops_team(model=model)
    
    print("=" * 70)
    print("CORTEXOPS MULTI-AGENT FRAMEWORK - ACTIVE")
    print("Roles: TPM Director | Staff R&D | Principal Architect | UI/UX | Frontend | Backend | DevOps | ML | QA | Reviewer | Academic Researcher")
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
