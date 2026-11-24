"""CLI Entrypoint for CortexOps Multi-Agent Framework."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

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

from src.engines import resolve_engine, get_default_model


def parse_arguments():
    """Parses command-line arguments for engine, model, and task prompt."""
    parser = argparse.ArgumentParser(
        description="CortexOps Multi-Agent Framework Task Runner",
        add_help=False,
    )
    parser.add_argument(
        "-e",
        "--engine",
        dest="engine",
        default=os.environ.get("CORTEXOPS_ENGINE", "antigravity"),
        help="Target execution harness: antigravity (default), claude, codex",
    )
    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        default=None,
        help="Model identifier override for selected execution engine",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Display this task runner help reference and exit",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Engineering task prompt or project goal",
    )
    return parser.parse_args()


async def run_task(prompt: str, engine_name: str, model_override: Optional[str] = None):
    """Executes a complete engineering or research lifecycle task via the selected engine."""
    engine = resolve_engine(engine_name)
    resolved_model = model_override or get_default_model(engine_name)
    normalized_engine = "antigravity"
    if engine_name.lower() in ("claude", "anthropic"):
        normalized_engine = "claude"
    elif engine_name.lower() in ("codex", "openai", "chatgpt"):
        normalized_engine = "codex"

    engine_tag = normalized_engine.upper()
    is_default = normalized_engine == "antigravity"

    print("=" * 70)
    print(f"CORTEXOPS MULTI-AGENT FRAMEWORK - ACTIVE [{engine_tag} ENGINE]")
    print("Roles: TPM Director | 25 Specialists (Rust, Backend, Software, System Architect, eBPF, Perf, Data, AppSec, QA, Reviewer, R&D, UI/UX, Frontend, Mobile, AI/ML, MLOps, Red Team, Synthetic Data, Database, DevOps, Platform, FinOps, Compliance, Academic, AL) | cxagents")
    print(f"Engine: {normalized_engine} {'(Default)' if is_default else ''}")
    print(f"Model:  {resolved_model}")
    print(f"Goal:   {prompt}")
    print("=" * 70 + "\n")

    print("=" * 70)
    print("ENGINEERING OUTCOME:")
    print("=" * 70)

    await engine.run(prompt=prompt, model=resolved_model)
    print("\n")


def main():
    args = parse_arguments()
    prompt = " ".join(args.prompt).strip() if args.prompt else ""

    if not prompt:
        print("Enter the engineering project or feature request:")
        try:
            prompt = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

    if not prompt:
        print("No task prompt provided. Exiting.")
        sys.exit(1)

    try:
        asyncio.run(run_task(
            prompt=prompt,
            engine_name=args.engine,
            model_override=args.model,
        ))
    except (ValueError, RuntimeError) as err:
        sys.stderr.write(f"\n[ERROR] {err}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
