"""CortexOps Multi-Engine Execution Dispatcher.

Provides polymorphic engine runners for Antigravity (default), Claude, and Codex.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Optional
import httpx

from src.team import LEAD_PM_DIRECTOR_INSTRUCTIONS, create_cortexops_team

DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
DEFAULT_CLAUDE_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
DEFAULT_CODEX_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")


class BaseEngine(ABC):
    """Abstract execution harness interface for CortexOps tasks."""

    @abstractmethod
    async def run(self, prompt: str, model: Optional[str] = None) -> None:
        """Executes the task prompt and streams the engineering outcome to stdout."""
        pass


class AntigravityEngine(BaseEngine):
    """Native Google Antigravity SDK engine harness utilizing Gemini models."""

    async def run(self, prompt: str, model: Optional[str] = None) -> None:
        from google.antigravity import Agent

        target_model = model or DEFAULT_GEMINI_MODEL
        config = create_cortexops_team(model=target_model)

        async with Agent(config) as team:
            response = await team.chat(prompt)
            async for chunk in response:
                print(chunk, end="", flush=True)


class ClaudeEngine(BaseEngine):
    """Anthropic Claude execution harness with real-time SSE streaming."""

    async def run(self, prompt: str, model: Optional[str] = None) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured.\n"
                "Please set ANTHROPIC_API_KEY in your environment, .env file, or run 'cxops setup'."
            )

        target_model = model or DEFAULT_CLAUDE_MODEL
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": target_model,
            "max_tokens": 4096,
            "system": LEAD_PM_DIRECTOR_INSTRUCTIONS,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    sys.stderr.write(
                        f"[ERROR] Anthropic API returned HTTP {response.status_code}: "
                        f"{err_body.decode('utf-8', errors='replace')}\n"
                    )
                    sys.exit(1)

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        try:
                            event = json.loads(data_str)
                            if event.get("type") == "content_block_delta":
                                text = event.get("delta", {}).get("text", "")
                                print(text, end="", flush=True)
                        except json.JSONDecodeError:
                            pass


class CodexEngine(BaseEngine):
    """OpenAI Codex / ChatGPT execution harness with real-time SSE streaming."""

    async def run(self, prompt: str, model: Optional[str] = None) -> None:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured.\n"
                "Please set OPENAI_API_KEY in your environment, .env file, or run 'cxops setup'."
            )

        target_model = model or DEFAULT_CODEX_MODEL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": LEAD_PM_DIRECTOR_INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    sys.stderr.write(
                        f"[ERROR] OpenAI API returned HTTP {response.status_code}: "
                        f"{err_body.decode('utf-8', errors='replace')}\n"
                    )
                    sys.exit(1)

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        try:
                            event = json.loads(data_str)
                            choices = event.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            pass


def resolve_engine(engine_name: Optional[str]) -> BaseEngine:
    """Normalizes and instantiates the target execution engine harness."""
    normalized = (engine_name or "").strip().lower()

    if normalized in ("claude", "anthropic"):
        return ClaudeEngine()
    if normalized in ("codex", "openai", "chatgpt"):
        return CodexEngine()

    return AntigravityEngine()


def get_default_model(engine_name: str) -> str:
    """Returns the default model identifier for the selected engine harness."""
    normalized = (engine_name or "").strip().lower()

    if normalized in ("claude", "anthropic"):
        return DEFAULT_CLAUDE_MODEL
    if normalized in ("codex", "openai", "chatgpt"):
        return DEFAULT_CODEX_MODEL

    return DEFAULT_GEMINI_MODEL
