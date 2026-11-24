"""Deterministic self-validation of the 4-tier E2E suite using synthetic fixtures."""

from __future__ import annotations

import io
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.e2e import common
from tests.e2e import run_e2e
from tests.e2e import tier1_features
from tests.e2e import tier2_boundaries
from tests.e2e import tier3_combinations
from tests.e2e import tier4_scenarios


_ROLE_SPECIFIC_BODY: dict[str, str] = {
    "rust_engineer": (
        "Covers ownership, borrowing, lifetimes, Tokio, Axum, Tower, "
        'extern "C" FFI with bindgen/cbindgen and // SAFETY: invariants, '
        "Aya and libbpf-rs eBPF, sqlx parameterized binds ($1, $2), "
        "cargo clippy -- -D warnings, cargo test, cargo audit, cargo deny."
    ),
    "backend_engineer": (
        "Multi-language microservices: Go (Gin), Bun (Express, Fastify, NestJS), "
        "Python (FastAPI), and Rust (Tokio, Axum, Tower). Enforce sqlx parameterized "
        "queries ($1, $2) with zero raw format! SQL interpolation, "
        "cargo clippy -- -D warnings, and cargo test."
    ),
    "software_engineer": (
        "Production implementation in Rust covering ownership, borrowing, lifetimes, "
        "Result error propagation without .unwrap(), Send and Sync thread safety, "
        "cargo check, cargo clippy -- -D warnings, and cargo test."
    ),
    "ebpf_engineer": (
        "Linux kernel observability with CO-RE C/libbpf, XDP, TC, Verifier compliance, "
        "clang -target bpf, plus Rust eBPF via Aya, libbpf-rs, bpf-linker, and ringbuf maps."
    ),
    "perf_engineer": (
        "Load testing with k6, Locust, OpenTelemetry, p95/p99 latency, PERF_REPORT.md, "
        "and Rust profiling with Criterion (cargo bench), cargo-flamegraph, pprof-rs, "
        "and Tokio contention / zero-GC allocation analysis."
    ),
    "data_engineer": (
        "Distributed pipelines with Kafka, Flink, Spark 3.5.0, Iceberg, dbt, plus "
        "Rust analytical engines using Apache Arrow (arrow-rs), Apache DataFusion, and Polars."
    ),
    "system_architect": (
        "ARCHITECTURE.md, PostgreSQL DDL, RFC 7807, flowchart TD, sequenceDiagram, "
        "erDiagram, stateDiagram-v2, Rust crate and trait boundaries, FFI C ABI "
        'extern "C" contracts, Tokio/Tower resilience, and sqlx ($1, $2).'
    ),
    "code_reviewer": (
        "OWASP Top 10 audits, APPROVED / REQUEST_CHANGES verdicts, auditing Rust unsafe "
        "blocks with // SAFETY: invariants, FFI soundness, mutex across .await, "
        "cargo clippy -- -D warnings, cargo audit, and cargo deny."
    ),
    "qa_engineer": (
        "Deterministic exit code 0 verification across go test -race, pytest, npm test, "
        "and Rust (cargo check, cargo clippy -- -D warnings, cargo test --all-targets), plus TEST_REPORT.md."
    ),
    "appsec_engineer": (
        "STRIDE/DREAD, OAuth 2.1, Argon2id, KMS, THREAT_MODEL.md, plus Rust supply-chain "
        "gating with cargo audit, cargo deny (deny.toml), and unsafe/FFI trust boundaries."
    ),
    "cxagents": (
        "Orchestrates all 25 SPECIALIST ROLES including Rust engineering and Test-Driven "
        "Development, Systematic Debugging, and Verification Before Completion."
    ),
}


def _agent_tools_for(role: str) -> tuple[str, ...]:
    if role in ("system_architect", "code_reviewer", "qa_engineer", "ai_ml_engineer"):
        return common.EXTENDED_9_TOOLS
    return common.STANDARD_7_TOOLS


def _build_agent_markdown(role: str) -> str:
    tools_yaml = "\n".join(f"    - {t}" for t in _agent_tools_for(role))
    desc = f"Synthetic specialist description for {role}."
    body = _ROLE_SPECIFIC_BODY.get(role, f"Standard capabilities for {role}.")
    extra_body = ""
    if role == "al_developer":
        extra_body = "\n- ControlAddIn Bridge:\n    - AL to JS: invoke method.\n    - JS to AL: callback.\n"
    if role == "cxagents":
        roster = "\n".join(
            f"  * `{r}`: Specialist role {r}." for r in common.ALL_SPECIALIST_ROLES
        )
        extra_body = (
            "\nMULTI-AGENT SPECIALIST ROSTER (25 SPECIALIST ROLES):\n"
            f"{roster}\n"
            "- Workflows: Test-Driven Development, Systematic Debugging, Verification Before Completion.\n"
        )
    return (
        f"---\n"
        f"name: {role}\n"
        f"description: {desc}\n"
        f"tools:\n{tools_yaml}\n"
        f"inheritCustomizations: false\n"
        f"inheritMcp: true\n"
        f"mainAgent: true\n"
        f"subagent: true\n"
        f"commandExecutionPolicy: auto\n"
        f"---\n\n"
        f"# Agent System Instructions\n\n"
        f"{body}\n"
        f"{extra_body}\n"
        f"STANDARDS: Zero emojis.\n"
    )


def _build_skill_markdown(role: str) -> str:
    kebab = common.snake_to_kebab(role)
    desc = f"Synthetic specialist description for {role}."
    body = _ROLE_SPECIFIC_BODY.get(role, f"Standard operational guidance for {role}.")
    extra_sections = ""
    if role == "rust_engineer":
        extra_sections = (
            "\n## Associated Mandatory Workflows\n- TDD\n\n"
            "## Deliverables\n- Rust crate source (`.rs`)\n\n"
            "```rust\n"
            "pub fn add_values(a: i32, b: i32) -> i32 {\n"
            "    a + b\n"
            "}\n\n"
            "#[cfg(test)]\n"
            "mod tests {\n"
            "    use super::add_values;\n\n"
            "    #[test]\n"
            "    fn adds_correctly() {\n"
            "        assert_eq!(add_values(2, 3), 5);\n"
            "    }\n"
            "}\n"
            "```\n"
        )
    elif role == "software_engineer":
        extra_sections = (
            "\n## Associated Mandatory Workflows\n"
            "- Test-Driven Development\n"
            "- Systematic Debugging: 1) Isolate and reproduce. 2) Trace root cause. "
            "3) Apply fix. 4) Verify suite.\n"
            "- Verification Before Completion\n"
        )
    elif role in ("ebpf_engineer", "data_engineer"):
        extra_sections = "\n## Deliverables\n- Rust artifacts (`.rs`)\n"
    elif role in ("perf_engineer", "appsec_engineer"):
        extra_sections = "\n## Deliverables\n- Diagnostic report (`.md`)\n"
    elif role in ("code_reviewer", "qa_engineer"):
        extra_sections = "\n## Associated Mandatory Workflows\n- Verification Before Completion\n"
    elif role == "cxagents":
        roster = "\n".join(
            f"  * `{r}`: Specialist role {r}." for r in common.ALL_SPECIALIST_ROLES
        )
        extra_sections = (
            "\n## Multi-Agent Specialist Roster (25 Specialist Roles)\n"
            f"{roster}\n"
            "\n## Jupyter Notebook Experiment Replication Standards\n- Clean output.\n"
        )

    return (
        f"---\n"
        f"name: {kebab}\n"
        f"description: >-\n"
        f"  {desc}\n"
        f"---\n\n"
        f"# {kebab} Operational Playbook\n\n"
        f"## Execution Procedure\n"
        f"- {body}\n"
        f"{extra_sections}"
    )


def _build_agents_md() -> str:
    other_roles = [r for r in common.ALL_ROLES if r != "rust_engineer"]
    ordered_roles = other_roles[:25] + ["rust_engineer"] + other_roles[25:]
    sections = [
        "### 1. Lead Technical Product Manager & Engineering Director (Root Agent)\n"
        "Translates stakeholder inputs into SPEC.md.\n"
    ]
    for idx, role in enumerate(ordered_roles, 2):
        rust_note = (
            " Supports Rust, Cargo, clippy, and FFI."
            if role in (*common.M2_ROLES, "rust_engineer")
            else ""
        )
        sections.append(f"### {idx}. Specialist Role (`{role}`)\nMandate for `{role}`.{rust_note}\n")

    return (
        "# CortexOps Standards\n\n"
        "## 3. Mandatory Mermaid Diagramming Standard\n"
        "Quote node labels like `id[\"Label (Extra Info)\"]`.\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        "    api[\"Gateway (HTTP)\"] --> db[\"Postgres\"]\n"
        "```\n\n"
        "## 5. Database Schema & Query Optimization Standard\n"
        "Use parameterized bindings (`$1, $2` in `pgx` and `sqlx`).\n\n"
        "## 6. Detailed Senior-Level Role Specifications\n\n"
        + "\n".join(sections)
        + "\n### Role-to-Workflow Association Matrix\n"
        "* `rust_engineer`: TDD and Cargo gates.\n"
        "* `cxagents`: Coordinates all 25 specialist roles across the team.\n\n"
        "## 7. Second Brain & Institutional Memory Integration\n"
        "Query ThutaCortex.\n\n"
        "## 8. Academic Research & Scientific Manuscript Authoring Rules\n"
        "### 1. Scientific Integrity\n"
        "Ground truth: 2844 windows, 1440 minutes, 0.9251, 0.9971, 0.9961, 11,046, 15(11).\n"
    )


def _build_personas_py() -> str:
    blocks = ['"""Synthetic CortexOps personas."""\n\nfrom google.antigravity import types\n']
    for role in common.ALL_ROLES:
        upper = role.upper()
        if role == "cxagents":
            roster_lines = "\n".join(
                f"- {r}: Specialist {r}." for r in common.ALL_SPECIALIST_ROLES
            )
            instr = (
                f"You are cxagents. Supports Rust orchestration.\n"
                f"ROSTER OF SPECIALISTS:\n{roster_lines}\n"
            )
        else:
            instr = f"You are {role}. {_ROLE_SPECIFIC_BODY.get(role, 'Standard engineer.')}"
        blocks.append(f'{upper}_INSTRUCTIONS = """{instr}"""\n')
        blocks.append(
            f"{role} = types.SubagentConfig(\n"
            f'    name="{role}",\n'
            f'    description="Single-line description for {role}.",\n'
            f"    system_instructions={upper}_INSTRUCTIONS,\n"
            f"    tools=[],\n"
            f"    capabilities=types.SubagentCapabilities(\n"
            f"        agent_behavior=types.AgentBehavior.AUTONOMOUS,\n"
            f"    ),\n"
            f")\n"
        )
    return "\n".join(blocks)


def _build_team_py() -> str:
    imports = ",\n    ".join(common.ALL_ROLES)
    sub_list = ",\n        ".join(common.ALL_ROLES)
    allowed_list = ",\n                ".join(f'"{r}"' for r in common.ALL_ROLES)
    return (
        '"""Synthetic team assembler."""\n\n'
        "from google.antigravity import LocalAgentConfig, types\n"
        f"from src.agents.personas import (\n    {imports},\n)\n\n"
        'LEAD_PM_DIRECTOR_INSTRUCTIONS = """Orchestrates all 25 specialist roles including rust_engineer."""\n\n'
        "def create_cortexops_team(model: str = 'gemini-3.8-flash') -> LocalAgentConfig:\n"
        f"    subagents = [\n        {sub_list},\n    ]\n"
        "    return LocalAgentConfig(\n"
        "        model=model,\n"
        "        subagents=subagents,\n"
        "        tools=[],\n"
        "        capabilities=types.CapabilitiesConfig(\n"
        "            enable_subagents=True,\n"
        "            max_subagent_depth=2,\n"
        f"            allowed_subagents=[\n                {allowed_list},\n            ],\n"
        "        ),\n"
        "        system_instructions=LEAD_PM_DIRECTOR_INSTRUCTIONS,\n"
        "    )\n"
    )


def _build_compliant_fixture(root: Path) -> None:
    for role in common.ALL_ROLES:
        agent_md = _build_agent_markdown(role)
        skill_md = _build_skill_markdown(role)
        p_agent = root / "plugin" / "agents" / f"{role}.md"
        p_skill = root / "plugin" / "skills" / common.snake_to_kebab(role) / "SKILL.md"
        p_dot = root / ".agents" / "agents" / role / "agent.md"
        for p, content in ((p_agent, agent_md), (p_skill, skill_md), (p_dot, agent_md)):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    # Upstream workflow with emojis (must be excluded by zero-emoji check)
    wf_dir = root / "plugin" / "workflows" / "sample-flow"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "SKILL.md").write_text("# Workflow\nStatus: \u2705 \u274c\n", encoding="utf-8")

    host_assets = common.HOST_REPO_ROOT / "plugin" / "assets"
    if host_assets.is_dir():
        shutil.copytree(host_assets, root / "plugin" / "assets", dirs_exist_ok=True)

    agents_md = _build_agents_md()
    (root / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    (root / "plugin" / "rules").mkdir(parents=True, exist_ok=True)
    (root / "plugin" / "rules" / "AGENTS.md").write_text(agents_md, encoding="utf-8")

    plugin_json = {
        "name": "cortexops",
        "displayName": "CortexOps Multi-Agent Framework",
        "version": "1.1.7",
        "description": "Autonomous multi-agent engineering operating system across 25 specialist roles.",
        "logo": "assets/antigravity-logo.png",
        "category": "Developer Tools",
        "keywords": ["cortexops", "rust", "rust-engineer", "cargo"],
    }
    plugin_json_text = json.dumps(plugin_json, indent=2) + "\n"
    (root / "plugin" / "plugin.json").write_text(plugin_json_text, encoding="utf-8")
    (root / ".antigravity-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".antigravity-plugin" / "plugin.json").write_text(plugin_json_text, encoding="utf-8")

    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "name": "cortexops",
                "version": "1.1.7",
                "description": "26 Staff/Principal personas including rust_engineer.",
                "keywords": ["cortexops", "rust"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(
            {
                "name": "cortexops-marketplace",
                "plugins": [
                    {
                        "name": "cortexops",
                        "description": "26 Staff/Principal personas.",
                        "version": "1.1.7",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "name": "cortexops",
                "version": "1.1.7",
                "description": "26 Staff/Principal personas with Rust support.",
                "keywords": ["cortexops", "rust"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "package.json").write_text(
        json.dumps(
            {
                "name": "@ctxthuta/cxops",
                "version": "1.1.7",
                "keywords": ["cortexops", "rust"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (root / "CLAUDE.md").write_text(
        "# CortexOps for Claude Code\nAdopt any of the 26 CortexOps personas including @rust_engineer for Rust.\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# CortexOps\nTeam Hierarchy includes rust_engineer.\nAll 26 agents are loaded.\n",
        encoding="utf-8",
    )
    (root / "cx").write_text("#!/usr/bin/env bash\necho 'Verify all 26 subagent definitions'\n", encoding="utf-8")
    (root / "cx.ps1").write_text("Write-Host 'Verify all 26 subagent definitions'\n", encoding="utf-8")

    host = common.HOST_REPO_ROOT
    shutil.copy2(host / "verify_agents.py", root / "verify_agents.py")
    (root / "bin").mkdir(parents=True, exist_ok=True)
    cxops_js = (host / "bin" / "cxops.js").read_text(encoding="utf-8").replace(
        "Verify all 12 subagent definitions",
        "Verify all 26 subagent definitions",
    )
    (root / "bin" / "cxops.js").write_text(cxops_js, encoding="utf-8")

    (root / "src" / "agents").mkdir(parents=True, exist_ok=True)
    (root / "src" / "tools").mkdir(parents=True, exist_ok=True)
    (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "agents" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "agents" / "personas.py").write_text(_build_personas_py(), encoding="utf-8")
    (root / "src" / "team.py").write_text(_build_team_py(), encoding="utf-8")
    shutil.copy2(host / "src" / "dashboard.py", root / "src" / "dashboard.py")
    (root / "src" / "engines.py").write_text(
        "def resolve_engine(name):\n    return None\n\ndef get_default_model(name):\n    return 'gemini-3.8-flash'\n",
        encoding="utf-8",
    )
    main_py = (host / "src" / "main.py").read_text(encoding="utf-8").replace(
        "Software Engineer | cxagents",
        "Software Engineer | Rust Engineer | cxagents",
    )
    (root / "src" / "main.py").write_text(main_py, encoding="utf-8")

    # Copy tests/e2e into synthetic fixture so S8 self-hygiene passes there too
    dst_e2e = root / "tests" / "e2e"
    dst_e2e.mkdir(parents=True, exist_ok=True)
    for pyf in (host / "tests" / "e2e").glob("*.py"):
        shutil.copy2(pyf, dst_e2e / pyf.name)


def _create_shim_rust_toolchain(bin_dir: Path) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    cargo = bin_dir / "cargo"
    rustc = bin_dir / "rustc"
    cargo.write_text("#!/usr/bin/env bash\necho 'cargo 1.80.0 (shim)'\nexit 0\n", encoding="utf-8")
    rustc.write_text("#!/usr/bin/env bash\necho 'rustc 1.80.0 (shim)'\nexit 0\n", encoding="utf-8")
    cargo.chmod(cargo.stat().st_mode | stat.S_IEXEC)
    rustc.chmod(rustc.stat().st_mode | stat.S_IEXEC)


class TestSelfE2EValidation(unittest.TestCase):
    """Self-tests proving E2E suite accuracy on compliant and mutated fixtures."""

    def test_compliant_fixture_passes_tiers_1_to_3_and_applicable_tier_4(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_pass_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)

            orig_path = os.environ.get("PATH", "")
            has_real_cargo = common.find_cargo_binary() is not None
            try:
                if not has_real_cargo:
                    shim_bin = Path(tmp) / "shim_bin"
                    _create_shim_rust_toolchain(shim_bin)
                    os.environ["PATH"] = f"{shim_bin}{os.pathsep}{orig_path}"

                for tier_id in (1, 2, 3):
                    res = run_e2e.run_tier_quiet(tier_id, root)
                    self.assertTrue(
                        res.wasSuccessful(),
                        f"Tier {tier_id} failed on compliant fixture: "
                        f"failures={res.failures}, errors={res.errors}",
                    )
            finally:
                os.environ["PATH"] = orig_path

            # Run applicable Tier 4 scenarios individually on compliant fixture
            applicable = [
                "test_s1_verify_agents_py",
                "test_s2_cxops_verify",
                "test_s5_dashboard_agent_roster",
                "test_s7_cxops_doctor_help_and_main_help",
                "test_s8_e2e_self_hygiene",
            ]
            if common.find_agy_binary() is not None:
                applicable.append("test_s3_agy_plugin_validate")
            if (common.HOST_REPO_ROOT / ".venv" / "bin" / "python3").is_file():
                applicable.append("test_s4_python_team_instantiation")

            prev_root = common.get_repo_root()
            common.set_repo_root(root)
            try:
                suite = unittest.TestSuite(
                    tier4_scenarios.TestRealWorldScenarios(name) for name in applicable
                )
                res4 = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                self.assertTrue(
                    res4.wasSuccessful(),
                    f"Applicable Tier 4 scenarios failed: failures={res4.failures}, errors={res4.errors}",
                )
            finally:
                common.set_repo_root(prev_root)

    def test_mutation_folded_agent_description_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            p = root / "plugin" / "agents" / "rust_engineer.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "description: Synthetic specialist description for rust_engineer.",
                    "description: >-\n  Folded scalar line.",
                ),
                encoding="utf-8",
            )
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Folded agent description must fail Tier 2")

    def test_mutation_emoji_in_rust_engineer_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            p = root / "plugin" / "agents" / "rust_engineer.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n\U0001F680\n", encoding="utf-8")
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Emoji in rust_engineer.md must fail Tier 2")

    def test_mutation_mermaid_unquoted_parens_and_html_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            bad_mermaid = (
                "```mermaid\n"
                "flowchart TD\n"
                "    api[Gateway (HTTP)<br/>Node] --> db[Postgres]\n"
                "```\n"
            )
            for rel in ("AGENTS.md", "plugin/rules/AGENTS.md"):
                p = root / rel
                txt = p.read_text(encoding="utf-8")
                txt = txt.replace(
                    '```mermaid\nflowchart TD\n    api["Gateway (HTTP)"] --> db["Postgres"]\n```\n',
                    bad_mermaid,
                )
                p.write_text(txt, encoding="utf-8")
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Invalid Mermaid block must fail Tier 2")

    def test_mutation_numbered_step_comment_in_code_block_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            p = root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "    a + b",
                    "    // Step 1: add numbers\n    a + b",
                ),
                encoding="utf-8",
            )
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Numbered step comment must fail Tier 2")

    def test_mutation_duplicate_lines_in_cxagents_instructions_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            p = root / "src" / "agents" / "personas.py"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "- backend_engineer: Specialist backend_engineer.",
                    "- backend_engineer: Specialist backend_engineer.\n- backend_engineer: Specialist backend_engineer.",
                ),
                encoding="utf-8",
            )
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Duplicate CXAGENTS_INSTRUCTIONS lines must fail Tier 2")

    def test_mutation_stale_role_counts_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            for rel in ("AGENTS.md", "plugin/rules/AGENTS.md"):
                p = root / rel
                p.write_text(
                    p.read_text(encoding="utf-8").replace(
                        "25 specialist roles", "12 specialist roles"
                    ),
                    encoding="utf-8",
                )
            cx_p = root / "plugin" / "agents" / "cxagents.md"
            cx_p.write_text(
                cx_p.read_text(encoding="utf-8").replace(
                    "25 SPECIALIST ROLES", "24 SPECIALIST ROLES"
                ),
                encoding="utf-8",
            )
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Stale role counts must fail Tier 2")

    def test_mutation_agents_md_drift_and_missing_dot_agents_mirror_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            (root / "plugin" / "rules" / "AGENTS.md").write_text(
                (root / "AGENTS.md").read_text(encoding="utf-8") + "\n# drift\n",
                encoding="utf-8",
            )
            (root / ".agents" / "agents" / "rust_engineer" / "agent.md").unlink()
            res = run_e2e.run_tier_quiet(3, root)
            self.assertFalse(res.wasSuccessful(), "AGENTS.md drift & missing mirror must fail Tier 3")

    def test_mutation_rust_snippet_hygiene_violations_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_mut_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            p = root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
            bad_rust = (
                "```rust\n"
                "pub fn bad() {\n"
                "    let x = Some(1).unwrap();\n"
                "    unsafe { let _ = x; }\n"
                "    ...\n"
                "}\n"
                "```\n"
            )
            p.write_text(p.read_text(encoding="utf-8") + "\n" + bad_rust, encoding="utf-8")
            res = run_e2e.run_tier_quiet(2, root)
            self.assertFalse(res.wasSuccessful(), "Unsafe/unwrap/ellipsis violations must fail Tier 2")

    def test_s6_fails_loudly_when_cargo_missing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_nocargo_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            orig_path = os.environ.get("PATH", "")
            orig_home = os.environ.get("HOME", "")
            orig_cargo_home = os.environ.get("CARGO_HOME")
            prev_root = common.get_repo_root()
            try:
                empty_home = Path(tmp) / "empty_home"
                empty_home.mkdir()
                os.environ["PATH"] = "/usr/bin:/bin"
                os.environ["HOME"] = str(empty_home)
                os.environ.pop("CARGO_HOME", None)
                common.set_repo_root(root)
                if common.find_cargo_binary() is None:
                    suite = unittest.TestSuite(
                        [tier4_scenarios.TestRealWorldScenarios("test_s6_rust_snippets_cargo_check_clippy_test")]
                    )
                    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                    self.assertFalse(res.wasSuccessful(), "S6 must fail loudly when cargo is missing")
                    self.assertEqual(len(res.skipped), 0, "S6 must never skip when cargo is missing")
            finally:
                common.set_repo_root(prev_root)
                os.environ["PATH"] = orig_path
                os.environ["HOME"] = orig_home
                if orig_cargo_home is not None:
                    os.environ["CARGO_HOME"] = orig_cargo_home

    def test_zero_false_positives_on_legitimate_patterns(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_zfp_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            prev_root = common.get_repo_root()
            common.set_repo_root(root)
            try:
                suite = unittest.TestSuite(
                    [
                        tier4_scenarios.TestRealWorldScenarios("test_s8_e2e_self_hygiene"),
                    ]
                )
                res_s8 = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                self.assertTrue(res_s8.wasSuccessful())
            finally:
                common.set_repo_root(prev_root)

            res2 = run_e2e.run_tier_quiet(2, root)
            self.assertTrue(
                res2.wasSuccessful(),
                f"Legitimate patterns triggered Tier 2 false positives: "
                f"failures={res2.failures}, errors={res2.errors}",
            )

    def test_cargo_workspace_materialization_and_error_mapping(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_ws_") as tmp:
            ws = Path(tmp) / "ws"
            src_doc = Path(tmp) / "skill.md"
            blocks = [
                common.FencedBlock(
                    file=src_doc,
                    start_line=42,
                    end_line=46,
                    info="rust",
                    lang="rust",
                    code="pub fn helper() -> i32 { 7 }",
                ),
                common.FencedBlock(
                    file=src_doc,
                    start_line=50,
                    end_line=54,
                    info="rust",
                    lang="rust",
                    code="fn main() { println!(\"ok\"); }",
                ),
            ]
            crate_map = common.materialize_rust_workspace(blocks, [], ws)
            self.assertTrue((ws / "Cargo.toml").is_file())
            self.assertTrue((ws / "crates" / "s001" / "src" / "lib.rs").is_file())
            self.assertTrue((ws / "crates" / "s002" / "src" / "main.rs").is_file())
            mapped = tier4_scenarios._map_cargo_errors(
                "error[E0308]: --> crates/s001/src/lib.rs:3:5",
                crate_map,
            )
            self.assertIn(f"{src_doc}:45", mapped)

    def test_regression_stale_role_counts_without_all_prefix(self) -> None:
        stale_samples = (
            "12 specialist roles",
            "13 CortexOps specialist personas",
            "13 Staff and Principal engineering specialists",
            "24 SPECIALIST ROLES",
        )
        for sample in stale_samples:
            self.assertTrue(
                bool(common.find_stale_role_counts(sample)),
                f"Expected stale count match for {sample!r}",
            )

        clean_samples = (
            "### 11. Staff Security & Code Reviewer",
            "### 24. Staff Systems & eBPF Kernel Engineer",
            "Ground truth 11,046 and 15(11) citation.",
            "12. `@rnd_researcher`",
        )
        for sample in clean_samples:
            self.assertEqual(
                common.find_stale_role_counts(sample),
                [],
                f"Unexpected false positive for {sample!r}",
            )

        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_stale_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            claude_p = root / "CLAUDE.md"
            claude_p.write_text(
                claude_p.read_text(encoding="utf-8").replace(
                    "26 CortexOps personas",
                    "13 CortexOps specialist personas",
                ),
                encoding="utf-8",
            )
            codex_p = root / ".codex-plugin" / "plugin.json"
            codex_p.write_text(
                codex_p.read_text(encoding="utf-8").replace(
                    "26 Staff/Principal personas",
                    "13 Staff and Principal engineering specialists",
                ),
                encoding="utf-8",
            )
            self.assertFalse(run_e2e.run_tier_quiet(2, root).wasSuccessful())
            self.assertFalse(run_e2e.run_tier_quiet(3, root).wasSuccessful())

    def test_regression_rust_hygiene_unsafe_extern_and_cfg_test_semicolon(self) -> None:
        self.assertTrue(
            bool(common.find_rust_hygiene_violations('pub unsafe extern "C" fn f() {}')),
            "Unannotated unsafe extern fn must fail",
        )
        documented_ffi = (
            "/// # Safety\n"
            "/// Caller guarantees valid pointer.\n"
            'pub unsafe extern "C" fn f(p: *const i32) -> i32 {\n'
            "    // SAFETY: pointer is non-null and aligned.\n"
            "    unsafe { *p }\n"
            "}\n"
        )
        self.assertEqual(common.find_rust_hygiene_violations(documented_ffi), [])

        semicolon_cfg = (
            "#[cfg(test)]\n"
            "mod external_tests;\n\n"
            "pub fn prod_panic() -> i32 {\n"
            "    Some(1).unwrap()\n"
            "}\n"
        )
        self.assertTrue(
            bool(common.find_rust_hygiene_violations(semicolon_cfg)),
            "#[cfg(test)] mod external_tests; must not suppress subsequent .unwrap()",
        )

        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_ffi_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            skill = root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + f"\n```rust\n{semicolon_cfg}```\n",
                encoding="utf-8",
            )
            self.assertFalse(run_e2e.run_tier_quiet(2, root).wasSuccessful())

    def test_regression_personas_short_constants_and_unbackticked_cxagents_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_compat_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)

            personas_p = root / "src" / "agents" / "personas.py"
            ptxt = personas_p.read_text(encoding="utf-8")
            ptxt = ptxt.replace("BACKEND_ENGINEER_INSTRUCTIONS", "BACKEND_INSTRUCTIONS")
            ptxt = ptxt.replace("SYSTEM_ARCHITECT_INSTRUCTIONS", "ARCHITECT_INSTRUCTIONS")
            ptxt = ptxt.replace("QA_ENGINEER_INSTRUCTIONS", "QA_INSTRUCTIONS")
            personas_p.write_text(ptxt, encoding="utf-8")

            cx_skill = root / "plugin" / "skills" / "cxagents" / "SKILL.md"
            stxt = cx_skill.read_text(encoding="utf-8")
            for role in common.ALL_SPECIALIST_ROLES:
                stxt = stxt.replace(f"  * `{role}`:", f"  * {role}:")
            cx_skill.write_text(stxt, encoding="utf-8")

            prev_root = common.get_repo_root()
            common.set_repo_root(root)
            try:
                suite = unittest.TestSuite(
                    [
                        tier1_features.TestF14PythonRuntime("test_f14_02_personas_updates_rust_specialists"),
                        tier2_boundaries.TestBoundaryF12Cxagents("test_t2_f12_04_no_duplicate_roster_entries"),
                        tier3_combinations.TestCrossFeatureCombinations(
                            "test_t3_07_cxagents_agent_and_skill_cover_all_25_specialists"
                        ),
                        tier3_combinations.TestCrossFeatureCombinations(
                            "test_t3_12_m2_rust_roles_synced_between_plugin_and_personas"
                        ),
                    ]
                )
                res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                self.assertTrue(
                    res.wasSuccessful(),
                    f"Compatibility checks failed: failures={res.failures}, errors={res.errors}",
                )
            finally:
                common.set_repo_root(prev_root)

    def test_regression_software_engineer_cfg_test_unwrap_allowed_and_prod_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_sw_unwrap_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            sw_skill = root / "plugin" / "skills" / "software-engineer" / "SKILL.md"
            base_txt = sw_skill.read_text(encoding="utf-8")

            with_cfg_test = (
                base_txt
                + "\n```rust\n"
                + "pub fn parse_num(raw: &str) -> Result<i32, std::num::ParseIntError> {\n"
                + "    raw.parse()\n"
                + "}\n\n"
                + "#[cfg(test)]\n"
                + "mod tests {\n"
                + "    use super::parse_num;\n\n"
                + "    #[test]\n"
                + "    fn parses_ok() {\n"
                + '        assert_eq!(parse_num("42").unwrap(), 42);\n'
                + "    }\n"
                + "}\n"
                + "```\n"
            )
            sw_skill.write_text(with_cfg_test, encoding="utf-8")
            prev_root = common.get_repo_root()
            common.set_repo_root(root)
            try:
                suite = unittest.TestSuite(
                    [
                        tier2_boundaries.TestBoundaryF04SoftwareEngineer(
                            "test_t2_f04_04_unwrap_mentioned_only_as_prohibition_or_in_tests"
                        )
                    ]
                )
                res_ok = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                self.assertTrue(
                    res_ok.wasSuccessful(),
                    f"#[cfg(test)] .unwrap() should be allowed: {res_ok.failures}",
                )

                sw_skill.write_text(
                    base_txt + "\n```rust\npub fn bad() -> i32 { Some(1).unwrap() }\n```\n",
                    encoding="utf-8",
                )
                res_prod = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(
                    unittest.TestSuite(
                        [
                            tier2_boundaries.TestBoundaryF04SoftwareEngineer(
                                "test_t2_f04_04_unwrap_mentioned_only_as_prohibition_or_in_tests"
                            )
                        ]
                    )
                )
                self.assertFalse(res_prod.wasSuccessful(), "Production .unwrap() in code block must fail")

                sw_skill.write_text(
                    base_txt + "\nCall .unwrap() freely in handlers.\n",
                    encoding="utf-8",
                )
                res_prose = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(
                    unittest.TestSuite(
                        [
                            tier2_boundaries.TestBoundaryF04SoftwareEngineer(
                                "test_t2_f04_04_unwrap_mentioned_only_as_prohibition_or_in_tests"
                            )
                        ]
                    )
                )
                self.assertFalse(res_prose.wasSuccessful(), "Non-prohibition .unwrap() prose must fail")
            finally:
                common.set_repo_root(prev_root)

    def test_regression_emoji_misc_blocks_and_mixed_multiline_mermaid(self) -> None:
        self.assertTrue(bool(common.find_emojis("Alert \u2b50")))
        self.assertTrue(bool(common.find_emojis("Timer \u23f0")))

        self.assertTrue(
            bool(common.validate_mermaid_block('flowchart TD\n    a["Gateway" (HTTP)] --> b["DB"]')),
            "Mixed-quoted Mermaid label with trailing unquoted parens must fail",
        )
        self.assertTrue(
            bool(common.validate_mermaid_block("flowchart TD\n    a[Gateway\n(HTTP)] --> b[DB]")),
            "Multiline unquoted Mermaid label with parens must fail",
        )
        self.assertEqual(
            common.validate_mermaid_block('flowchart TD\n    a["Gateway\n(HTTP)"] --> b["DB"]'),
            [],
        )

        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_edge_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            agent_p = root / "plugin" / "agents" / "rust_engineer.md"
            agent_p.write_text(agent_p.read_text(encoding="utf-8") + "\n\u2b50\n", encoding="utf-8")
            self.assertFalse(run_e2e.run_tier_quiet(2, root).wasSuccessful())

    def test_regression_plain_multiline_agent_desc_and_cxagents_nonbullet_dup(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_plain_wrap_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)

            devops_p = root / "plugin" / "agents" / "devops_engineer.md"
            devops_p.write_text(
                devops_p.read_text(encoding="utf-8").replace(
                    "description: Synthetic specialist description for devops_engineer.",
                    "description: Synthetic specialist description\n  wrapped across second line.",
                ),
                encoding="utf-8",
            )
            self.assertFalse(
                run_e2e.run_tier_quiet(2, root).wasSuccessful(),
                "Plain multiline wrapped description on unmodified agent must fail Tier 2",
            )

        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_cx_nonbullet_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)
            personas_p = root / "src" / "agents" / "personas.py"
            personas_p.write_text(
                personas_p.read_text(encoding="utf-8").replace(
                    "ROSTER OF SPECIALISTS:",
                    "ROSTER OF SPECIALISTS:\nROSTER OF SPECIALISTS:",
                ),
                encoding="utf-8",
            )
            self.assertFalse(
                run_e2e.run_tier_quiet(1, root).wasSuccessful(),
                "Duplicate non-bullet line in CXAGENTS_INSTRUCTIONS must fail Tier 1",
            )
            self.assertFalse(
                run_e2e.run_tier_quiet(2, root).wasSuccessful(),
                "Duplicate non-bullet line in CXAGENTS_INSTRUCTIONS must fail Tier 2",
            )

    def test_regression_pre_m2_ebpf_and_perf_fail_tightened_checks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cortexops_e2e_prem2_") as tmp:
            root = Path(tmp) / "repo"
            _build_compliant_fixture(root)

            for p in (
                root / "plugin" / "agents" / "ebpf_engineer.md",
                root / "plugin" / "skills" / "ebpf-engineer" / "SKILL.md",
            ):
                p.write_text(
                    "High performance kernel eBPF tracing with Aya and libbpf-rs.\n",
                    encoding="utf-8",
                )
            for p in (
                root / "plugin" / "agents" / "perf_engineer.md",
                root / "plugin" / "skills" / "perf-engineer" / "SKILL.md",
            ):
                p.write_text(
                    "Captures CPU flamegraphs and runs Criterion cargo bench.\n",
                    encoding="utf-8",
                )

            prev_root = common.get_repo_root()
            common.set_repo_root(root)
            try:
                for cls_obj, test_name in (
                    (tier1_features.TestF05EbpfEngineerRust, "test_f05_02_rust_ebpf_tooling_and_maps"),
                    (tier1_features.TestF06PerfEngineerRust, "test_f06_02_flamegraph_or_pprof_rs"),
                ):
                    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(
                        unittest.TestSuite([cls_obj(test_name)])
                    )
                    self.assertFalse(
                        res.wasSuccessful(),
                        f"{test_name} must fail on pre-M2 keywords",
                    )
            finally:
                common.set_repo_root(prev_root)
