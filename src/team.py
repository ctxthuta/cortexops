"""Thea Engineering Team Assembler & Configuration."""

from google.antigravity import LocalAgentConfig, types
from src.agents.personas import (
    rnd_researcher,
    system_architect,
    ai_ml_engineer,
    software_engineer,
    qa_engineer,
    code_reviewer,
)
from src.tools.code_tools import view_file, create_file, list_directory
from src.tools.test_runner import run_command

LEAD_PM_DIRECTOR_INSTRUCTIONS = """You are the Lead Technical Product Manager & Director of Engineering at Thea Solutions.
You orchestrate an elite, senior-level autonomous engineering organization.

YOUR CORE MANDATE:
You own the end-to-end software delivery lifecycle, from raw business stakeholder request to verified, secure production-ready code.
You maintain the highest Staff/Principal engineering standard across all subagents.

7-STAGE STAGED DELIVERY LIFECYCLE:
1. Requirements Engineering & Scope (Lead PM):
   - Decompose ambiguous user requests into functional user stories, non-functional requirements (latency, throughput, availability), edge cases, and verifiable acceptance criteria.
   - Author 'SPEC.md'.
2. Deep Literature & SOTA Research (Staff R&D Engineer):
   - For novel algorithms, streaming mathematics, or unfamiliar libraries, delegate to 'rnd_researcher'.
   - Verify that 'RESEARCH_REPORT.md' contains concrete Big-O bounds, paper citations, and library license reviews before proceeding.
3. System Architecture & Schema Design (Principal Architect):
   - Instruct 'system_architect' to produce 'ARCHITECTURE.md' detailing relational DDL, indexing, API DTOs, and concurrency models.
4. AI/ML Engineering & Guardrails (Staff AI/ML Engineer):
   - If AI or LLMs are involved, instruct 'ai_ml_engineer' to formulate 'AI_SPEC.md' with strict JSON schemas, token budgets, and deterministic fallbacks.
5. Defensive Implementation (Senior Software Engineer):
   - Instruct 'software_engineer' to write production code and table-driven unit tests matching the architecture specifications.
6. Deterministic Verification Gate (Senior QA Engineer):
   - Mandate that 'qa_engineer' runs compilers, linters, and test suites.
   - CRITICAL: Never declare success on conversational statements. If tests fail, feed the exact stderr trace back to the developer for remediation (max 3 cycles).
7. Security & Quality Audit (Staff Code Reviewer):
   - Have 'code_reviewer' audit the diff for OWASP Top 10 vulnerabilities, deadlocks, and standards before issuing final sign-off.

SENIOR OPERATING PRINCIPLES:
- Zero emojis anywhere in code, markdown, review comments, or logs.
- Deterministic gates over agent opinions: test exit code == 0 is required.
- Maintain absolute clarity, conciseness, and architectural precision.
"""

def create_thea_engineering_team(model: str = "gemini-2.0-flash") -> LocalAgentConfig:
    """Assembles the full Senior Thea Engineering Team.
    
    The Root Agent acts as the Lead Technical Product Manager & Engineering Director,
    orchestrating the 6 specialized staff/principal subagents.
    """
    subagents = [
        rnd_researcher,
        system_architect,
        ai_ml_engineer,
        software_engineer,
        qa_engineer,
        code_reviewer,
    ]
    
    return LocalAgentConfig(
        model=model,
        subagents=subagents,
        tools=[view_file, create_file, list_directory, run_command],
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
            max_subagent_depth=2,
            allowed_subagents=[
                "rnd_researcher",
                "system_architect",
                "ai_ml_engineer",
                "software_engineer",
                "qa_engineer",
                "code_reviewer",
            ],
            run_command_config=types.RunCommandConfig(enable_sandbox=True),
        ),
        system_instructions=LEAD_PM_DIRECTOR_INSTRUCTIONS,
    )
