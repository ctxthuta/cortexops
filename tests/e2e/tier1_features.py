"""Tier 1 E2E Feature Coverage Tests (F1-F15, >= 75 opaque-box tests)."""

from __future__ import annotations

import json
import os
import py_compile
import re
import subprocess
import unittest
from pathlib import Path

from . import common


def _role_texts(role: str) -> tuple[str, str, str]:
    root = common.get_repo_root()
    agent_path = root / "plugin" / "agents" / f"{role}.md"
    skill_path = root / "plugin" / "skills" / common.snake_to_kebab(role) / "SKILL.md"
    agent_txt = common.read_text_utf8(agent_path) if agent_path.is_file() else ""
    skill_txt = common.read_text_utf8(skill_path) if skill_path.is_file() else ""
    return agent_txt, skill_txt, f"{agent_txt}\n{skill_txt}"


def _run_tool(tool_path: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    tool_dir = str(tool_path.parent)
    env["PATH"] = f"{tool_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [str(tool_path), *args],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        check=False,
    )


class TestF01RustEngineer(unittest.TestCase):
    """F1: Dedicated rust_engineer agent, skill, and .agents mirror."""

    def test_f01_01_files_exist(self) -> None:
        root = common.get_repo_root()
        for rel in (
            "plugin/agents/rust_engineer.md",
            "plugin/skills/rust-engineer/SKILL.md",
            ".agents/agents/rust_engineer/agent.md",
        ):
            self.assertTrue((root / rel).is_file(), f"Missing F1 artifact: {rel}")

    def test_f01_02_frontmatter_contract(self) -> None:
        root = common.get_repo_root()
        agent_path = root / "plugin" / "agents" / "rust_engineer.md"
        self.assertTrue(agent_path.is_file(), "Missing plugin/agents/rust_engineer.md")
        fm = common.parse_agent_frontmatter(agent_path)
        self.assertEqual(fm["name"], "rust_engineer")
        self.assertFalse(fm["description_folded"], "Agent description must not use >-")
        self.assertTrue(bool(fm["description"]), "Agent description must be non-empty")
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
        self.assertIs(fm.get("inheritCustomizations"), False)
        self.assertIs(fm.get("inheritMcp"), True)
        self.assertIs(fm.get("mainAgent"), True)
        self.assertIs(fm.get("subagent"), True)
        self.assertEqual(fm.get("commandExecutionPolicy"), "auto")

    def test_f01_03_core_rust_and_async_coverage(self) -> None:
        _, _, combined = _role_texts("rust_engineer")
        lowered = combined.lower()
        for kw in ("ownership", "borrowing", "lifetime", "tokio", "axum", "tower"):
            self.assertIn(kw, lowered, f"rust_engineer missing core keyword: {kw}")

    def test_f01_04_ffi_and_ebpf_coverage(self) -> None:
        _, _, combined = _role_texts("rust_engineer")
        self.assertIn('extern "C"', combined, 'rust_engineer missing extern "C" FFI')
        self.assertIn("// SAFETY:", combined, "rust_engineer missing // SAFETY: invariant")
        lowered = combined.lower()
        self.assertTrue(
            "bindgen" in lowered or "cbindgen" in lowered,
            "rust_engineer missing bindgen/cbindgen coverage",
        )
        self.assertIn("aya", lowered, "rust_engineer missing Aya eBPF coverage")
        self.assertIn("libbpf-rs", lowered, "rust_engineer missing libbpf-rs coverage")

    def test_f01_05_verification_security_and_skill_sections(self) -> None:
        _, skill_txt, combined = _role_texts("rust_engineer")
        lowered = combined.lower()
        for kw in ("sqlx", "cargo test", "cargo audit", "cargo deny"):
            self.assertIn(kw, lowered, f"rust_engineer missing verification/security tool: {kw}")
        self.assertRegex(
            lowered,
            r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings",
            "rust_engineer missing cargo clippy ... -- -D warnings",
        )
        for section in (
            "## Associated Mandatory Workflows",
            "## Execution Procedure",
            "## Deliverables",
        ):
            self.assertIn(section, skill_txt, f"rust-engineer/SKILL.md missing section: {section}")


class TestF02RustToolchainAndSnippets(unittest.TestCase):
    """F2: Rust toolchain availability and compilable reference snippets."""

    def test_f02_01_cargo_and_rustc_available(self) -> None:
        cargo = common.find_cargo_binary()
        rustc = common.find_rustc_binary()
        self.assertIsNotNone(
            cargo, "Rust toolchain missing: cargo not found in PATH, CARGO_HOME, or ~/.cargo/bin"
        )
        self.assertIsNotNone(
            rustc, "Rust toolchain missing: rustc not found in PATH, CARGO_HOME, or ~/.cargo/bin"
        )
        assert cargo is not None and rustc is not None
        res_cargo = _run_tool(cargo, ["--version"])
        res_rustc = _run_tool(rustc, ["--version"])
        self.assertEqual(res_cargo.returncode, 0, f"cargo --version failed: {res_cargo.stderr}")
        self.assertEqual(res_rustc.returncode, 0, f"rustc --version failed: {res_rustc.stderr}")

    def test_f02_02_cargo_clippy_available(self) -> None:
        cargo = common.find_cargo_binary()
        self.assertIsNotNone(cargo, "Rust toolchain missing: cargo not found")
        assert cargo is not None
        res = _run_tool(cargo, ["clippy", "--version"])
        self.assertEqual(res.returncode, 0, f"cargo clippy missing or failed: {res.stderr}")

    def test_f02_03_rust_fenced_blocks_present(self) -> None:
        root = common.get_repo_root()
        blocks, unclosed, rs_files = common.extract_rust_blocks(root)
        self.assertEqual(unclosed, [], f"Unclosed markdown fences found: {unclosed}")
        self.assertGreaterEqual(
            len(blocks) + len(rs_files),
            1,
            "No ```rust fenced blocks or .rs files found across target docs/skills/agents",
        )

    def test_f02_04_rust_blocks_have_runnable_or_testable_items(self) -> None:
        root = common.get_repo_root()
        blocks, _, rs_files = common.extract_rust_blocks(root)
        items = [b.code for b in blocks] + [common.read_text_utf8(p) for p in rs_files]
        self.assertGreaterEqual(len(items), 1, "No Rust snippets to inspect")
        has_test_or_main = any(
            "#[test]" in code or "#[cfg(test)]" in code or re.search(r"\bfn\s+main\s*\(", code)
            for code in items
        )
        self.assertTrue(
            has_test_or_main,
            "At least one Rust snippet must include #[test]/#[cfg(test)] or fn main()",
        )

    def test_f02_05_rust_blocks_pass_static_hygiene_check(self) -> None:
        root = common.get_repo_root()
        blocks, _, rs_files = common.extract_rust_blocks(root)
        self.assertGreaterEqual(len(blocks) + len(rs_files), 1, "No Rust snippets found")
        for blk in blocks:
            self.assertTrue(
                bool(blk.code.strip()),
                f"{blk.file}:{blk.start_line}: empty ```rust block",
            )
            violations = common.find_rust_hygiene_violations(blk.code, blk.info)
            self.assertEqual(
                violations,
                [],
                f"{blk.file}:{blk.start_line}: hygiene violations: {violations}",
            )


class TestF03BackendEngineerRust(unittest.TestCase):
    """F3: backend_engineer Rust microservices and sqlx integration."""

    def test_f03_01_tokio_axum_tower_microservices(self) -> None:
        _, _, combined = _role_texts("backend_engineer")
        lowered = combined.lower()
        for kw in ("rust", "tokio", "axum", "tower"):
            self.assertIn(kw, lowered, f"backend_engineer missing {kw}")

    def test_f03_02_sqlx_parameterized_bindings(self) -> None:
        _, _, combined = _role_texts("backend_engineer")
        self.assertIn("sqlx", combined.lower(), "backend_engineer missing sqlx")
        self.assertTrue(
            "$1" in combined or "$2" in combined,
            "backend_engineer missing parameterized bind placeholder guidance ($1, $2)",
        )

    def test_f03_03_cargo_clippy_and_test(self) -> None:
        _, _, combined = _role_texts("backend_engineer")
        lowered = combined.lower()
        self.assertRegex(lowered, r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings")
        self.assertIn("cargo test", lowered)

    def test_f03_04_preserves_existing_runtimes(self) -> None:
        _, _, combined = _role_texts("backend_engineer")
        lowered = combined.lower()
        for kw in ("go", "gin", "bun", "express", "fastify", "nestjs", "python"):
            self.assertIn(kw, lowered, f"backend_engineer dropped existing runtime: {kw}")

    def test_f03_05_frontmatter_and_skill_structure(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "backend_engineer.md")
        self.assertEqual(fm["name"], "backend_engineer")
        self.assertFalse(fm["description_folded"])
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
        skill_txt = common.read_text_utf8(root / "plugin" / "skills" / "backend-engineer" / "SKILL.md")
        self.assertIn("## Execution Procedure", skill_txt)


class TestF04SoftwareEngineerRust(unittest.TestCase):
    """F4: software_engineer Rust ownership, safety, and cargo verification."""

    def test_f04_01_ownership_borrowing_lifetimes(self) -> None:
        _, _, combined = _role_texts("software_engineer")
        lowered = combined.lower()
        for kw in ("rust", "ownership", "borrowing", "lifetime"):
            self.assertIn(kw, lowered, f"software_engineer missing {kw}")

    def test_f04_02_result_propagation_and_send_sync(self) -> None:
        _, _, combined = _role_texts("software_engineer")
        self.assertIn("Result", combined, "software_engineer missing Result propagation guidance")
        self.assertIn(".unwrap()", combined, "software_engineer should explicitly prohibit .unwrap()")
        self.assertIn("Send", combined, "software_engineer missing Send thread-safety coverage")
        self.assertIn("Sync", combined, "software_engineer missing Sync thread-safety coverage")

    def test_f04_03_cargo_check_clippy_test(self) -> None:
        _, _, combined = _role_texts("software_engineer")
        lowered = combined.lower()
        self.assertIn("cargo check", lowered, "software_engineer missing cargo check")
        self.assertRegex(lowered, r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings")
        self.assertIn("cargo test", lowered, "software_engineer missing cargo test")

    def test_f04_04_preserves_mandatory_workflows(self) -> None:
        _, skill_txt, _ = _role_texts("software_engineer")
        for wf in (
            "Test-Driven Development",
            "Systematic Debugging",
            "Verification Before Completion",
        ):
            self.assertIn(wf, skill_txt, f"software-engineer/SKILL.md missing {wf}")

    def test_f04_05_frontmatter_and_skill_structure(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "software_engineer.md")
        self.assertEqual(fm["name"], "software_engineer")
        self.assertFalse(fm["description_folded"])
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
        skill_txt = common.read_text_utf8(root / "plugin" / "skills" / "software-engineer" / "SKILL.md")
        self.assertIn("## Associated Mandatory Workflows", skill_txt)


class TestF05EbpfEngineerRust(unittest.TestCase):
    """F5: ebpf_engineer Rust Aya and libbpf-rs integration."""

    def test_f05_01_aya_and_libbpf_rs(self) -> None:
        _, _, combined = _role_texts("ebpf_engineer")
        lowered = combined.lower()
        self.assertIn("rust", lowered)
        self.assertIn("aya", lowered)
        self.assertIn("libbpf-rs", lowered)

    def test_f05_02_rust_ebpf_tooling_and_maps(self) -> None:
        _, _, combined = _role_texts("ebpf_engineer")
        self.assertRegex(
            combined.lower(),
            r"\bbpf-linker\b|\bringbuf\b|perf\s*event",
            "ebpf_engineer missing bpf-linker or Rust ringbuf/perf event consumer guidance",
        )

    def test_f05_03_preserves_core_c_xdp_tc_verifier(self) -> None:
        _, _, combined = _role_texts("ebpf_engineer")
        for kw in ("CO-RE", "XDP", "Verifier", "libbpf"):
            self.assertIn(kw, combined, f"ebpf_engineer dropped {kw}")

    def test_f05_04_deliverables_include_rs(self) -> None:
        _, skill_txt, _ = _role_texts("ebpf_engineer")
        self.assertIn("## Deliverables", skill_txt)
        self.assertIn(".rs", skill_txt, "ebpf-engineer/SKILL.md Deliverables missing .rs")

    def test_f05_05_frontmatter_and_skill_structure(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "ebpf_engineer.md")
        self.assertEqual(fm["name"], "ebpf_engineer")
        self.assertFalse(fm["description_folded"])
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))


class TestF06PerfEngineerRust(unittest.TestCase):
    """F6: perf_engineer Criterion, flamegraph, and Tokio profiling."""

    def test_f06_01_criterion_cargo_bench(self) -> None:
        _, _, combined = _role_texts("perf_engineer")
        lowered = combined.lower()
        self.assertIn("criterion", lowered)
        self.assertIn("cargo bench", lowered)

    def test_f06_02_flamegraph_or_pprof_rs(self) -> None:
        _, _, combined = _role_texts("perf_engineer")
        self.assertRegex(
            combined.lower(),
            r"cargo[- ]flamegraph|pprof-rs",
            "perf_engineer missing cargo-flamegraph/pprof-rs coverage",
        )

    def test_f06_03_tokio_contention_and_zero_gc_alloc(self) -> None:
        _, _, combined = _role_texts("perf_engineer")
        lowered = combined.lower()
        self.assertIn("tokio", lowered)
        self.assertIn("rust", lowered)

    def test_f06_04_preserves_k6_locust_otel_report(self) -> None:
        _, _, combined = _role_texts("perf_engineer")
        for kw in ("k6", "Locust", "OpenTelemetry", "PERF_REPORT.md"):
            self.assertIn(kw, combined, f"perf_engineer dropped {kw}")

    def test_f06_05_frontmatter_and_deliverables(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "perf_engineer.md")
        self.assertEqual(fm["name"], "perf_engineer")
        self.assertFalse(fm["description_folded"])
        skill_txt = common.read_text_utf8(root / "plugin" / "skills" / "perf-engineer" / "SKILL.md")
        self.assertIn("## Deliverables", skill_txt)


class TestF07DataEngineerRust(unittest.TestCase):
    """F7: data_engineer Arrow, DataFusion, and Polars integration."""

    def test_f07_01_apache_arrow_rust(self) -> None:
        _, _, combined = _role_texts("data_engineer")
        lowered = combined.lower()
        self.assertIn("rust", lowered)
        self.assertIn("arrow", lowered)

    def test_f07_02_apache_datafusion(self) -> None:
        _, _, combined = _role_texts("data_engineer")
        self.assertIn("datafusion", combined.lower())

    def test_f07_03_polars(self) -> None:
        _, _, combined = _role_texts("data_engineer")
        self.assertIn("polars", combined.lower())

    def test_f07_04_preserves_kafka_flink_spark_iceberg_dbt(self) -> None:
        _, _, combined = _role_texts("data_engineer")
        for kw in ("Kafka", "Flink", "Spark", "Iceberg", "dbt"):
            self.assertIn(kw, combined, f"data_engineer dropped {kw}")

    def test_f07_05_frontmatter_and_deliverables_rs(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "data_engineer.md")
        self.assertEqual(fm["name"], "data_engineer")
        self.assertFalse(fm["description_folded"])
        skill_txt = common.read_text_utf8(root / "plugin" / "skills" / "data-engineer" / "SKILL.md")
        self.assertIn("## Deliverables", skill_txt)
        self.assertIn(".rs", skill_txt, "data-engineer/SKILL.md Deliverables missing .rs")


class TestF08SystemArchitectRust(unittest.TestCase):
    """F8: system_architect Rust crate/trait boundaries and FFI ABI contracts."""

    def test_f08_01_crate_and_trait_boundaries(self) -> None:
        _, _, combined = _role_texts("system_architect")
        lowered = combined.lower()
        self.assertIn("rust", lowered)
        self.assertTrue(
            "crate" in lowered and "trait" in lowered,
            "system_architect missing Rust crate/trait boundary guidance",
        )

    def test_f08_02_ffi_abi_contracts(self) -> None:
        _, _, combined = _role_texts("system_architect")
        lowered = combined.lower()
        self.assertIn("ffi", lowered)
        self.assertTrue(
            'extern "c"' in lowered or "c abi" in lowered,
            'system_architect missing extern "C" / C ABI contract guidance',
        )

    def test_f08_03_tokio_tower_resilience_and_sqlx(self) -> None:
        _, _, combined = _role_texts("system_architect")
        lowered = combined.lower()
        self.assertTrue("tokio" in lowered or "tower" in lowered)
        self.assertIn("sqlx", lowered)
        self.assertIn("$1", combined)

    def test_f08_04_preserves_mermaid_standards(self) -> None:
        _, _, combined = _role_texts("system_architect")
        for kw in ("flowchart TD", "sequenceDiagram", "erDiagram", "stateDiagram-v2"):
            self.assertIn(kw, combined, f"system_architect dropped Mermaid type {kw}")

    def test_f08_05_frontmatter_9_tools_and_deliverable(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "system_architect.md")
        self.assertEqual(fm["name"], "system_architect")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))
        _, skill_txt, combined = _role_texts("system_architect")
        self.assertIn("ARCHITECTURE.md", combined)
        self.assertIn("## Execution Procedure", skill_txt)


class TestF09CodeReviewerRust(unittest.TestCase):
    """F9: code_reviewer Rust unsafe/FFI/mutex-await and cargo audit/deny checks."""

    def test_f09_01_unsafe_and_safety_invariants(self) -> None:
        _, _, combined = _role_texts("code_reviewer")
        self.assertIn("unsafe", combined)
        self.assertIn("// SAFETY:", combined)

    def test_f09_02_ffi_soundness_and_await_mutex(self) -> None:
        _, _, combined = _role_texts("code_reviewer")
        lowered = combined.lower()
        self.assertIn("ffi", lowered)
        self.assertTrue(
            ".await" in lowered and ("mutex" in lowered or "lock" in lowered),
            "code_reviewer missing mutex-across-.await hazard check",
        )

    def test_f09_03_cargo_clippy_audit_deny(self) -> None:
        _, _, combined = _role_texts("code_reviewer")
        lowered = combined.lower()
        self.assertRegex(lowered, r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings")
        for cmd in ("cargo audit", "cargo deny"):
            self.assertIn(cmd, lowered, f"code_reviewer missing {cmd}")

    def test_f09_04_preserves_owasp_and_verdicts(self) -> None:
        _, _, combined = _role_texts("code_reviewer")
        for kw in ("OWASP Top 10", "APPROVED", "REQUEST_CHANGES"):
            self.assertIn(kw, combined, f"code_reviewer dropped {kw}")

    def test_f09_05_frontmatter_9_tools_and_workflows(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "code_reviewer.md")
        self.assertEqual(fm["name"], "code_reviewer")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))
        _, skill_txt, _ = _role_texts("code_reviewer")
        self.assertIn("## Associated Mandatory Workflows", skill_txt)


class TestF10QaEngineerRust(unittest.TestCase):
    """F10: qa_engineer cargo check, clippy, and test deterministic gates."""

    def test_f10_01_cargo_check_verification(self) -> None:
        _, _, combined = _role_texts("qa_engineer")
        self.assertIn("cargo check", combined.lower())

    def test_f10_02_cargo_clippy_d_warnings(self) -> None:
        _, _, combined = _role_texts("qa_engineer")
        self.assertRegex(combined.lower(), r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings")

    def test_f10_03_cargo_test_execution(self) -> None:
        _, _, combined = _role_texts("qa_engineer")
        self.assertIn("cargo test", combined.lower())

    def test_f10_04_preserves_existing_runners_and_report(self) -> None:
        _, _, combined = _role_texts("qa_engineer")
        for kw in ("go test -race", "pytest", "npm test", "TEST_REPORT.md"):
            self.assertIn(kw, combined, f"qa_engineer dropped {kw}")

    def test_f10_05_frontmatter_9_tools_and_workflows(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "qa_engineer.md")
        self.assertEqual(fm["name"], "qa_engineer")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))
        _, skill_txt, _ = _role_texts("qa_engineer")
        self.assertIn("## Associated Mandatory Workflows", skill_txt)


class TestF11AppsecEngineerRust(unittest.TestCase):
    """F11: appsec_engineer cargo audit, cargo deny, and unsafe/FFI security gating."""

    def test_f11_01_cargo_audit_rustsec(self) -> None:
        _, _, combined = _role_texts("appsec_engineer")
        self.assertIn("cargo audit", combined.lower())

    def test_f11_02_cargo_deny_policy(self) -> None:
        _, _, combined = _role_texts("appsec_engineer")
        lowered = combined.lower()
        self.assertIn("cargo deny", lowered)
        self.assertIn("deny.toml", lowered)

    def test_f11_03_unsafe_and_ffi_trust_boundary(self) -> None:
        _, _, combined = _role_texts("appsec_engineer")
        lowered = combined.lower()
        self.assertIn("unsafe", lowered)
        self.assertIn("ffi", lowered)

    def test_f11_04_preserves_stride_oauth_kms_threat_model(self) -> None:
        _, _, combined = _role_texts("appsec_engineer")
        for kw in ("STRIDE", "OAuth 2.1", "KMS", "THREAT_MODEL.md"):
            self.assertIn(kw, combined, f"appsec_engineer dropped {kw}")

    def test_f11_05_frontmatter_and_deliverables(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "appsec_engineer.md")
        self.assertEqual(fm["name"], "appsec_engineer")
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
        _, skill_txt, _ = _role_texts("appsec_engineer")
        self.assertIn("## Deliverables", skill_txt)


class TestF12CxagentsOrchestrator(unittest.TestCase):
    """F12: cxagents orchestrator roster and Rust dispatch routing."""

    def test_f12_01_roster_includes_rust_engineer(self) -> None:
        agent_txt, skill_txt, _ = _role_texts("cxagents")
        self.assertIn("rust_engineer", agent_txt, "cxagents.md missing rust_engineer")
        self.assertIn("rust_engineer", skill_txt, "cxagents/SKILL.md missing rust_engineer")

    def test_f12_02_roster_declares_25_specialists(self) -> None:
        agent_txt, skill_txt, _ = _role_texts("cxagents")
        self.assertIn("SPECIALIST ROLES", agent_txt.upper())
        self.assertIn("Specialist Roles", skill_txt)

    def test_f12_03_rust_orchestration_flow(self) -> None:
        _, _, combined = _role_texts("cxagents")
        self.assertIn("rust", combined.lower(), "cxagents missing Rust orchestration mention")

    def test_f12_04_preserves_all_25_specialists_and_workflows(self) -> None:
        agent_txt, skill_txt, _ = _role_texts("cxagents")
        for role in common.ALL_SPECIALIST_ROLES:
            self.assertIn(role, agent_txt, f"cxagents.md missing specialist: {role}")
            self.assertIn(role, skill_txt, f"cxagents/SKILL.md missing specialist: {role}")
        for wf in ("Test-Driven Development", "Systematic Debugging", "Verification Before Completion"):
            self.assertIn(wf, agent_txt, f"cxagents.md missing workflow: {wf}")

    def test_f12_05_frontmatter_and_skill_structure(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "cxagents.md")
        self.assertEqual(fm["name"], "cxagents")
        self.assertFalse(fm["description_folded"])
        self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
        _, skill_txt, _ = _role_texts("cxagents")
        self.assertIn("## Execution Procedure", skill_txt)


class TestF13AgentsMdRules(unittest.TestCase):
    """F13: AGENTS.md and plugin/rules/AGENTS.md Rust updates and role index."""

    def test_f13_01_role_section_27_rust_engineer(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        self.assertRegex(
            txt,
            r"(?m)^###\s+27\.\s+.*`rust_engineer`",
            "AGENTS.md missing ### 27. rust_engineer section",
        )

    def test_f13_02_updated_9_specialists_and_cxagents_sections(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        sections = re.split(r"(?m)(?=^###\s+\d+\.)", txt)
        by_role: dict[str, str] = {}
        for sec in sections:
            m = re.match(r"^###\s+\d+\..*`([a-z0-9_]+)`", sec)
            if m:
                by_role[m.group(1)] = sec
        for role in common.M2_ROLES:
            self.assertIn(role, by_role, f"AGENTS.md missing section for {role}")
            self.assertRegex(
                by_role[role].lower(),
                r"\b(?:rust(?:_engineer)?|cargo)\b",
                f"AGENTS.md section for {role} missing Rust/Cargo coverage",
            )

    def test_f13_03_database_standard_includes_sqlx(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        self.assertIn("sqlx", txt.lower(), "AGENTS.md §5 Database standard missing sqlx")

    def test_f13_04_role_workflow_matrix_25_specialists_and_rust(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        m = re.search(r"(?ms)^###\s+Role-to-Workflow Association Matrix.*?(?=^---|\Z)", txt)
        self.assertIsNotNone(m, "AGENTS.md missing Role-to-Workflow Association Matrix")
        assert m is not None
        matrix = m.group(0)
        self.assertIn("rust_engineer", matrix)
        self.assertIn("25 specialist roles", matrix)

    def test_f13_05_preserves_core_sections_and_mermaid_standard(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        for heading in (
            "## 3. Mandatory Mermaid Diagramming Standard",
            "## 5. Database Schema & Query Optimization Standard",
            "## 7. Second Brain & Institutional Memory Integration",
            "## 8. Academic Research & Scientific Manuscript Authoring Rules",
        ):
            self.assertIn(heading, txt, f"AGENTS.md missing core section: {heading}")


class TestF14PythonRuntime(unittest.TestCase):
    """F14: Python runtime personas, team assembly, and main CLI."""

    def test_f14_01_personas_defines_rust_engineer(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        self.assertIn("rust_engineer", configs, "personas.py missing rust_engineer SubagentConfig")
        self.assertTrue(
            bool(configs["rust_engineer"]["system_instructions"].strip()),
            "rust_engineer SubagentConfig has empty system_instructions",
        )

    def test_f14_02_personas_updates_rust_specialists(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        for role in (*common.M2_ROLES, "rust_engineer"):
            self.assertIn(
                role,
                configs,
                f"src/agents/personas.py missing SubagentConfig for {role}",
            )
            instr = configs[role]["system_instructions"]
            self.assertTrue(
                bool(instr.strip()),
                f"{role} has empty system_instructions in personas.py",
            )
            self.assertRegex(
                instr.lower(),
                r"\b(?:rust(?:_engineer)?|cargo)\b",
                f"{role}.system_instructions in personas.py missing Rust/Cargo guidance",
            )

    def test_f14_03_personas_cxagents_has_rust_and_no_duplicates(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        self.assertIn("cxagents", configs, "Missing cxagents SubagentConfig in personas.py")
        block = configs["cxagents"]["system_instructions"]
        self.assertIn("rust_engineer", block)
        non_empty_lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        seen: set[str] = set()
        dups: list[str] = []
        for ln in non_empty_lines:
            if ln in seen:
                dups.append(ln)
            seen.add(ln)
        self.assertEqual(
            dups,
            [],
            f"Duplicate non-empty lines found in cxagents system_instructions: {dups}",
        )

    def test_f14_04_team_registers_rust_engineer_and_m2_roles(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "src" / "team.py")
        self.assertIn("rust_engineer", txt)
        m = re.search(r'(?ms)LEAD_PM_DIRECTOR_INSTRUCTIONS\s*=\s*"""(.*?)"""', txt)
        self.assertIsNotNone(m, "Missing LEAD_PM_DIRECTOR_INSTRUCTIONS in src/team.py")
        assert m is not None
        self.assertIn("rust_engineer", m.group(1))
        for role in (*common.RUST_UPDATED_ROLES, "rust_engineer", "cxagents"):
            self.assertIn(f'"{role}"', txt, f"src/team.py missing allowed_subagent {role}")

    def test_f14_05_main_py_compiles_and_banner_includes_rust(self) -> None:
        root = common.get_repo_root()
        main_py = root / "src" / "main.py"
        py_compile.compile(str(main_py), doraise=True)
        txt = common.read_text_utf8(main_py)
        banner_lines = [ln for ln in txt.splitlines() if "Roles:" in ln]
        self.assertTrue(banner_lines, "src/main.py missing Roles: banner line")
        self.assertIn("rust", "\n".join(banner_lines).lower())


class TestF15DocsCliManifests(unittest.TestCase):
    """F15: Docs, CLI wrappers, plugin manifests, and .agents/agents parity."""

    def test_f15_01_claude_md_has_rust_engineer_and_updated_count(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "CLAUDE.md")
        self.assertIn("@rust_engineer", txt)
        self.assertIn("rust", txt.lower())
        self.assertEqual(common.find_stale_role_counts(txt), [])

    def test_f15_02_readme_has_rust_engineer_and_updated_counts(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "README.md")
        self.assertIn("rust", txt.lower())
        self.assertTrue(
            "rust_engineer" in txt or "Rust Engineer" in txt,
            "README.md missing rust_engineer / Rust Engineer in hierarchy",
        )
        self.assertEqual(common.find_stale_role_counts(txt), [])

    def test_f15_03_antigravity_manifests_have_rust_keywords(self) -> None:
        root = common.get_repo_root()
        for rel in ("plugin/plugin.json", ".antigravity-plugin/plugin.json"):
            data = json.loads(common.read_text_utf8(root / rel))
            keywords = [str(k).lower() for k in data.get("keywords", [])]
            self.assertTrue(
                any("rust" in k for k in keywords),
                f"{rel} missing rust keyword in {keywords}",
            )

    def test_f15_04_claude_codex_package_manifests_updated(self) -> None:
        root = common.get_repo_root()
        for rel in (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            "package.json",
        ):
            txt = common.read_text_utf8(root / rel)
            data = json.loads(txt)
            keywords = [str(k).lower() for k in data.get("keywords", [])]
            self.assertTrue(
                any("rust" in k for k in keywords),
                f"{rel} missing rust keyword",
            )
            self.assertEqual(common.find_stale_role_counts(txt), [], f"{rel} has stale count")
        mkt_txt = common.read_text_utf8(root / ".claude-plugin" / "marketplace.json")
        json.loads(mkt_txt)
        self.assertEqual(common.find_stale_role_counts(mkt_txt), [])

    def test_f15_05_cli_wrappers_and_dot_agents_26_roles(self) -> None:
        root = common.get_repo_root()
        for rel in ("bin/cxops.js", "cx", "cx.ps1"):
            txt = common.read_text_utf8(root / rel)
            self.assertEqual(
                common.find_stale_role_counts(txt),
                [],
                f"{rel} still contains stale role count",
            )
        for role in common.ALL_ROLES:
            self.assertTrue(
                (root / ".agents" / "agents" / role / "agent.md").is_file(),
                f"Missing .agents/agents/{role}/agent.md",
            )
