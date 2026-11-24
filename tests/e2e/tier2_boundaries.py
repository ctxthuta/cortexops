"""Tier 2 E2E Boundary & Corner Case Tests (F1-F15, >= 75 tests)."""

from __future__ import annotations

import ast
import json
import py_compile
import re
import unittest
from pathlib import Path

from . import common


def _assert_single_line_agent_description(tc: unittest.TestCase, role: str) -> dict[str, object]:
    root = common.get_repo_root()
    path = root / "plugin" / "agents" / f"{role}.md"
    tc.assertTrue(path.is_file(), f"Missing agent file: {path}")
    fm = common.parse_agent_frontmatter(path)
    desc = str(fm["description"])
    tc.assertFalse(fm["description_folded"], f"{role}.md uses folded YAML description")
    tc.assertFalse(fm["description_multiline"], f"{role}.md has multi-line description")
    tc.assertTrue(bool(desc), f"{role}.md has empty description")
    tc.assertNotIn(desc, (">-", ">", "|", "No description"), f"{role}.md invalid description: {desc!r}")
    tc.assertLessEqual(len(desc), 450, f"{role}.md description exceeds 450 chars")
    return fm


def _assert_zero_emojis_for_role(tc: unittest.TestCase, role: str) -> None:
    root = common.get_repo_root()
    for path in (
        root / "plugin" / "agents" / f"{role}.md",
        root / "plugin" / "skills" / common.snake_to_kebab(role) / "SKILL.md",
        root / ".agents" / "agents" / role / "agent.md",
    ):
        if path.is_file():
            hits = common.find_emojis(common.read_text_utf8(path))
            tc.assertEqual(hits, [], f"Emojis found in {path}: {hits}")


def _assert_no_numbered_step_comments_in_code(tc: unittest.TestCase, path: Path) -> None:
    if not path.is_file():
        return
    blocks, unclosed = common.extract_fenced_blocks(common.read_text_utf8(path), path)
    tc.assertEqual(unclosed, [], f"Unclosed fenced code block in {path}: {unclosed}")
    for blk in blocks:
        hits = common.find_numbered_step_comments(blk.code)
        tc.assertEqual(
            hits,
            [],
            f"Numbered step comments in {path}:{blk.start_line}: {hits}",
        )


def _assert_no_unfinished_todo_stubs(tc: unittest.TestCase, path: Path) -> None:
    tc.assertTrue(path.is_file(), f"Missing file: {path}")
    text = common.read_text_utf8(path)
    blocks, _ = common.extract_fenced_blocks(text, path)
    for blk in blocks:
        for idx, line in enumerate(blk.code.splitlines(), 1):
            tc.assertIsNone(
                re.search(r"\b(?:TODO|FIXME|TBD)\b|todo!\(|unimplemented!\(", line),
                f"{path}:{blk.start_line + idx}: unfinished stub in code block: {line!r}",
            )
    for line_no, line in enumerate(text.splitlines(), 1):
        if re.search(r"(?m)^(?:#+\s*)?(?:TODO|FIXME|TBD)\s*:", line):
            tc.fail(f"{path}:{line_no}: unfinished placeholder marker: {line!r}")


class TestBoundaryF01RustEngineer(unittest.TestCase):
    """Boundary checks for F1 (rust_engineer)."""

    def test_t2_f01_01_single_line_description(self) -> None:
        fm = _assert_single_line_agent_description(self, "rust_engineer")
        self.assertFalse(str(fm["raw_description_value"]).endswith("\\"))

    def test_t2_f01_02_zero_emojis_and_no_numbered_step_comments(self) -> None:
        _assert_zero_emojis_for_role(self, "rust_engineer")
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(self, root / "plugin" / "agents" / "rust_engineer.md")
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
        )

    def test_t2_f01_03_skill_kebab_name_and_folded_description(self) -> None:
        root = common.get_repo_root()
        skill_path = root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
        self.assertTrue(skill_path.is_file(), "Missing rust-engineer/SKILL.md")
        fm = common.parse_skill_frontmatter(skill_path)
        self.assertEqual(fm["name"], "rust-engineer")
        self.assertTrue(fm["is_folded"], "SKILL.md description should use >- folded block")
        self.assertTrue(bool(fm["description"]), "SKILL.md description must be non-empty")

    def test_t2_f01_04_no_duplicate_tools_or_unknown_frontmatter_keys(self) -> None:
        root = common.get_repo_root()
        fm = common.parse_agent_frontmatter(root / "plugin" / "agents" / "rust_engineer.md")
        self.assertEqual(fm["duplicate_tools"], [], f"Duplicate tools: {fm['duplicate_tools']}")
        self.assertEqual(fm["unknown_keys"], [], f"Unknown frontmatter keys: {fm['unknown_keys']}")

    def test_t2_f01_05_no_unfinished_placeholders(self) -> None:
        root = common.get_repo_root()
        _assert_no_unfinished_todo_stubs(self, root / "plugin" / "agents" / "rust_engineer.md")
        _assert_no_unfinished_todo_stubs(
            self, root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
        )


class TestBoundaryF02RustSnippets(unittest.TestCase):
    """Boundary checks for F2 (Rust snippet hygiene and fence completeness)."""

    def test_t2_f02_01_no_ellipsis_placeholders_in_rust_blocks(self) -> None:
        root = common.get_repo_root()
        blocks, unclosed, _ = common.extract_rust_blocks(root)
        self.assertEqual(unclosed, [], f"Unclosed markdown fences: {unclosed}")
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            for idx, line in enumerate(blk.code.splitlines(), 1):
                if re.search(r"(?<!\.)(?<!,)\.\.\.(?!\.)", line) and not re.search(
                    r",\s*\.\.\.\s*\)", line
                ):
                    self.fail(
                        f"{blk.file}:{blk.start_line + idx}: ellipsis placeholder '...' in Rust block"
                    )

    def test_t2_f02_02_no_unwrap_or_expect_outside_tests(self) -> None:
        root = common.get_repo_root()
        blocks, _, _ = common.extract_rust_blocks(root)
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            violations = [
                v for v in common.find_rust_hygiene_violations(blk.code, blk.info)
                if ".unwrap()" in v
            ]
            self.assertEqual(violations, [], f"{blk.file}:{blk.start_line}: {violations}")

    def test_t2_f02_03_unsafe_requires_safety_comment(self) -> None:
        root = common.get_repo_root()
        blocks, _, _ = common.extract_rust_blocks(root)
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            violations = [
                v for v in common.find_rust_hygiene_violations(blk.code, blk.info)
                if "SAFETY:" in v
            ]
            self.assertEqual(violations, [], f"{blk.file}:{blk.start_line}: {violations}")

    def test_t2_f02_04_no_todo_macros_or_numbered_step_comments(self) -> None:
        root = common.get_repo_root()
        blocks, _, _ = common.extract_rust_blocks(root)
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            violations = [
                v for v in common.find_rust_hygiene_violations(blk.code, blk.info)
                if "stub" in v or "TODO" in v or "numbered step" in v
            ]
            self.assertEqual(violations, [], f"{blk.file}:{blk.start_line}: {violations}")

    def test_t2_f02_05_no_ignored_or_uncompilable_rust_fences(self) -> None:
        root = common.get_repo_root()
        blocks, unclosed, _ = common.extract_rust_blocks(root)
        self.assertEqual(unclosed, [], f"Unclosed markdown fences: {unclosed}")
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            violations = [
                v for v in common.find_rust_hygiene_violations(blk.code, blk.info)
                if "non-compilable" in v
            ]
            self.assertEqual(violations, [], f"{blk.file}:{blk.start_line}: {violations}")


class TestBoundaryF03BackendEngineer(unittest.TestCase):
    """Boundary checks for F3 (backend_engineer)."""

    def test_t2_f03_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "backend_engineer")

    def test_t2_f03_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "backend_engineer")

    def test_t2_f03_03_preserves_multi_language_coverage(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "plugin" / "agents" / "backend_engineer.md").lower()
        for lang in ("go", "bun", "python", "rust"):
            self.assertIn(lang, txt, f"backend_engineer missing runtime {lang}")

    def test_t2_f03_04_prohibits_raw_sql_format_interpolation(self) -> None:
        root = common.get_repo_root()
        for path in (
            root / "plugin" / "agents" / "backend_engineer.md",
            root / "plugin" / "skills" / "backend-engineer" / "SKILL.md",
        ):
            txt = common.read_text_utf8(path)
            for line_no, line in enumerate(txt.splitlines(), 1):
                if "format!" in line and "sql" in line.lower():
                    self.assertRegex(
                        line.lower(),
                        r"\b(?:no|zero|never|prohibit|forbid|avoid|ban|reject|instead of)\b",
                        f"{path}:{line_no}: format! near SQL without prohibition context",
                    )

    def test_t2_f03_05_no_numbered_step_comments_or_stubs(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "backend_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "backend-engineer" / "SKILL.md"
        )
        _assert_no_unfinished_todo_stubs(self, root / "plugin" / "agents" / "backend_engineer.md")


class TestBoundaryF04SoftwareEngineer(unittest.TestCase):
    """Boundary checks for F4 (software_engineer)."""

    def test_t2_f04_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "software_engineer")

    def test_t2_f04_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "software_engineer")

    def test_t2_f04_03_prose_lists_allowed_code_comments_prohibited(self) -> None:
        root = common.get_repo_root()
        skill_path = root / "plugin" / "skills" / "software-engineer" / "SKILL.md"
        _assert_no_numbered_step_comments_in_code(self, skill_path)
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "software_engineer.md"
        )

    def test_t2_f04_04_unwrap_mentioned_only_as_prohibition_or_in_tests(self) -> None:
        root = common.get_repo_root()
        prohibition_re = re.compile(
            r"\b(?:no|without|prohibit|prohibits|prohibiting|avoid|forbid|never|zero|ban|not)\b"
        )
        for path in (
            root / "plugin" / "agents" / "software_engineer.md",
            root / "plugin" / "skills" / "software-engineer" / "SKILL.md",
        ):
            txt = common.read_text_utf8(path)
            in_fence = False
            fence_char = ""
            fence_len = 0
            fence_lang = ""
            cfg_tracker = common.CfgTestScopeTracker()

            for line_no, line in enumerate(txt.splitlines(), 1):
                if not in_fence:
                    m_open = common._FENCE_OPEN_RE.match(line)
                    if m_open:
                        token = m_open.group(1)
                        fence_char = token[0]
                        fence_len = len(token)
                        info = m_open.group(2).strip()
                        fence_lang = info.split(",")[0].split()[0].lower() if info else ""
                        in_fence = True
                        cfg_tracker = common.CfgTestScopeTracker()
                        continue
                else:
                    close_re = re.compile(
                        rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$"
                    )
                    if close_re.match(line):
                        in_fence = False
                        fence_lang = ""
                        continue

                if in_fence:
                    in_test = cfg_tracker.advance(line)
                    if fence_lang in ("rust", "rs", "") and not in_test:
                        if ".unwrap()" in line or ".expect(" in line:
                            self.fail(
                                f"{path}:{line_no}: .unwrap()/.expect() in non-test code block: {line!r}"
                            )
                else:
                    if (".unwrap()" in line or ".expect(" in line) and not line.strip().startswith("//"):
                        self.assertRegex(
                            line.lower(),
                            prohibition_re,
                            f"{path}:{line_no}: .unwrap()/.expect() outside prohibition rule: {line!r}",
                        )

    def test_t2_f04_05_no_unfinished_todo_stubs(self) -> None:
        root = common.get_repo_root()
        _assert_no_unfinished_todo_stubs(self, root / "plugin" / "agents" / "software_engineer.md")
        _assert_no_unfinished_todo_stubs(
            self, root / "plugin" / "skills" / "software-engineer" / "SKILL.md"
        )


class TestBoundaryF05EbpfEngineer(unittest.TestCase):
    """Boundary checks for F5 (ebpf_engineer)."""

    def test_t2_f05_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "ebpf_engineer")

    def test_t2_f05_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "ebpf_engineer")

    def test_t2_f05_03_covers_both_aya_and_libbpf_rs(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "ebpf_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "ebpf-engineer" / "SKILL.md")
        ).lower()
        self.assertIn("aya", combined)
        self.assertIn("libbpf-rs", combined)

    def test_t2_f05_04_preserves_clang_bpf_core_c_rules(self) -> None:
        root = common.get_repo_root()
        skill_txt = common.read_text_utf8(
            root / "plugin" / "skills" / "ebpf-engineer" / "SKILL.md"
        )
        self.assertIn("clang -target bpf", skill_txt)
        self.assertIn("CO-RE", skill_txt)

    def test_t2_f05_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "ebpf_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "ebpf-engineer" / "SKILL.md"
        )


class TestBoundaryF06PerfEngineer(unittest.TestCase):
    """Boundary checks for F6 (perf_engineer)."""

    def test_t2_f06_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "perf_engineer")

    def test_t2_f06_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "perf_engineer")

    def test_t2_f06_03_preserves_existing_load_and_tracing_tools(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "perf_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "perf-engineer" / "SKILL.md")
        )
        for kw in ("k6", "Locust", "OpenTelemetry", "Criterion"):
            self.assertIn(kw, combined)

    def test_t2_f06_04_retains_percentile_metrics(self) -> None:
        root = common.get_repo_root()
        combined = common.read_text_utf8(root / "plugin" / "agents" / "perf_engineer.md")
        self.assertIn("p95", combined)
        self.assertIn("p99", combined)

    def test_t2_f06_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "perf_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "perf-engineer" / "SKILL.md"
        )


class TestBoundaryF07DataEngineer(unittest.TestCase):
    """Boundary checks for F7 (data_engineer)."""

    def test_t2_f07_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "data_engineer")

    def test_t2_f07_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "data_engineer")

    def test_t2_f07_03_covers_all_three_rust_data_engines(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "data_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "data-engineer" / "SKILL.md")
        ).lower()
        for crate in ("arrow", "datafusion", "polars"):
            self.assertIn(crate, combined, f"data_engineer missing {crate}")

    def test_t2_f07_04_preserves_spark_flink_iceberg_dbt(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "plugin" / "agents" / "data_engineer.md")
        for kw in ("Spark", "Flink", "Iceberg", "dbt"):
            self.assertIn(kw, txt)

    def test_t2_f07_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "data_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "data-engineer" / "SKILL.md"
        )


class TestBoundaryF08SystemArchitect(unittest.TestCase):
    """Boundary checks for F8 (system_architect)."""

    def test_t2_f08_01_single_line_description_and_9_tools(self) -> None:
        fm = _assert_single_line_agent_description(self, "system_architect")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))

    def test_t2_f08_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "system_architect")

    def test_t2_f08_03_mermaid_blocks_valid_if_present(self) -> None:
        root = common.get_repo_root()
        for path in (
            root / "plugin" / "agents" / "system_architect.md",
            root / "plugin" / "skills" / "system-architect" / "SKILL.md",
        ):
            blocks, unclosed = common.extract_fenced_blocks(
                common.read_text_utf8(path), path, langs=("mermaid",)
            )
            self.assertEqual(unclosed, [], f"Unclosed fence in {path}: {unclosed}")
            for blk in blocks:
                errs = common.validate_mermaid_block(blk.code)
                self.assertEqual(errs, [], f"{path}:{blk.start_line}: {errs}")

    def test_t2_f08_04_preserves_ddl_and_rfc7807(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "plugin" / "agents" / "system_architect.md")
        for kw in ("ARCHITECTURE.md", "PostgreSQL DDL", "RFC 7807"):
            self.assertIn(kw, txt)

    def test_t2_f08_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "system_architect.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "system-architect" / "SKILL.md"
        )


class TestBoundaryF09CodeReviewer(unittest.TestCase):
    """Boundary checks for F9 (code_reviewer)."""

    def test_t2_f09_01_single_line_description_and_9_tools(self) -> None:
        fm = _assert_single_line_agent_description(self, "code_reviewer")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))

    def test_t2_f09_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "code_reviewer")

    def test_t2_f09_03_requires_both_cargo_audit_and_cargo_deny(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "code_reviewer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "code-reviewer" / "SKILL.md")
        ).lower()
        self.assertIn("cargo audit", combined)
        self.assertIn("cargo deny", combined)

    def test_t2_f09_04_safety_invariant_and_await_mutex_check(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "code_reviewer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "code-reviewer" / "SKILL.md")
        )
        self.assertIn("// SAFETY:", combined)
        self.assertIn(".await", combined)

    def test_t2_f09_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "code_reviewer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "code-reviewer" / "SKILL.md"
        )


class TestBoundaryF10QaEngineer(unittest.TestCase):
    """Boundary checks for F10 (qa_engineer)."""

    def test_t2_f10_01_single_line_description_and_9_tools(self) -> None:
        fm = _assert_single_line_agent_description(self, "qa_engineer")
        self.assertEqual(fm["tools"], list(common.EXTENDED_9_TOOLS))

    def test_t2_f10_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "qa_engineer")

    def test_t2_f10_03_exact_clippy_deny_warnings_flag(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "qa_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "qa-engineer" / "SKILL.md")
        ).lower()
        self.assertRegex(combined, r"cargo\s+clippy\b[^\n]*--\s+-d\s+warnings")

    def test_t2_f10_04_enforces_exit_code_zero_gate(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "qa_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "qa-engineer" / "SKILL.md")
        ).lower()
        self.assertIn("exit code 0", combined)

    def test_t2_f10_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "qa_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "qa-engineer" / "SKILL.md"
        )


class TestBoundaryF11AppsecEngineer(unittest.TestCase):
    """Boundary checks for F11 (appsec_engineer)."""

    def test_t2_f11_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "appsec_engineer")

    def test_t2_f11_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "appsec_engineer")

    def test_t2_f11_03_requires_both_cargo_audit_and_cargo_deny_toml(self) -> None:
        root = common.get_repo_root()
        combined = (
            common.read_text_utf8(root / "plugin" / "agents" / "appsec_engineer.md")
            + "\n"
            + common.read_text_utf8(root / "plugin" / "skills" / "appsec-engineer" / "SKILL.md")
        ).lower()
        self.assertIn("cargo audit", combined)
        self.assertIn("cargo deny", combined)
        self.assertIn("deny.toml", combined)

    def test_t2_f11_04_preserves_auth_and_crypto_standards(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "plugin" / "skills" / "appsec-engineer" / "SKILL.md")
        for kw in ("Argon2id", "OAuth 2.1", "KMS"):
            self.assertIn(kw, txt)

    def test_t2_f11_05_no_numbered_step_comments_in_code(self) -> None:
        root = common.get_repo_root()
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "agents" / "appsec_engineer.md"
        )
        _assert_no_numbered_step_comments_in_code(
            self, root / "plugin" / "skills" / "appsec-engineer" / "SKILL.md"
        )


class TestBoundaryF12Cxagents(unittest.TestCase):
    """Boundary checks for F12 (cxagents)."""

    def test_t2_f12_01_single_line_description(self) -> None:
        _assert_single_line_agent_description(self, "cxagents")

    def test_t2_f12_02_zero_emojis(self) -> None:
        _assert_zero_emojis_for_role(self, "cxagents")

    def test_t2_f12_03_no_stale_24_specialist_counts(self) -> None:
        root = common.get_repo_root()
        for path in (
            root / "plugin" / "agents" / "cxagents.md",
            root / "plugin" / "skills" / "cxagents" / "SKILL.md",
        ):
            hits = common.find_stale_role_counts(common.read_text_utf8(path))
            self.assertEqual(hits, [], f"Stale count in {path}: {hits}")

    def test_t2_f12_04_no_duplicate_roster_entries(self) -> None:
        root = common.get_repo_root()
        for path in (
            root / "plugin" / "agents" / "cxagents.md",
            root / "plugin" / "skills" / "cxagents" / "SKILL.md",
        ):
            txt = common.read_text_utf8(path)
            found = re.findall(r"(?m)^\s*[-*]\s+`?([a-z0-9_]+)`?\s*:", txt)
            self.assertGreaterEqual(len(found), 25, f"Expected >=25 roster entries in {path}")
            self.assertEqual(len(found), len(set(found)), f"Duplicate roster roles in {path}: {found}")

    def test_t2_f12_05_preserves_notebook_replication_standards(self) -> None:
        root = common.get_repo_root()
        skill_txt = common.read_text_utf8(root / "plugin" / "skills" / "cxagents" / "SKILL.md")
        self.assertIn("Jupyter Notebook", skill_txt)


class TestBoundaryF13AgentsMd(unittest.TestCase):
    """Boundary checks for F13 (AGENTS.md and plugin/rules/AGENTS.md)."""

    def test_t2_f13_01_sequential_role_headings_1_to_27(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        m = re.search(
            r"(?ms)^##\s+6\.\s+Detailed Senior-Level Role Specifications.*?(?=^###\s+Role-to-Workflow Association Matrix|\Z)",
            txt,
        )
        self.assertIsNotNone(m, "AGENTS.md missing §6 Detailed Senior-Level Role Specifications")
        assert m is not None
        nums = [int(x) for x in re.findall(r"(?m)^###\s+(\d+)\.\s+", m.group(0))]
        self.assertEqual(nums, list(range(1, len(nums) + 1)), f"Role headings not sequential: {nums}")

    def test_t2_f13_02_zero_emojis_in_both_agents_md_files(self) -> None:
        root = common.get_repo_root()
        for rel in ("AGENTS.md", "plugin/rules/AGENTS.md"):
            hits = common.find_emojis(common.read_text_utf8(root / rel))
            self.assertEqual(hits, [], f"Emojis in {rel}: {hits}")

    def test_t2_f13_03_mermaid_blocks_valid_without_prose_false_positive(self) -> None:
        root = common.get_repo_root()
        path = root / "AGENTS.md"
        blocks, unclosed = common.extract_fenced_blocks(
            common.read_text_utf8(path), path, langs=("mermaid",)
        )
        self.assertEqual(unclosed, [], f"Unclosed markdown fences in AGENTS.md: {unclosed}")
        for blk in blocks:
            errs = common.validate_mermaid_block(blk.code)
            self.assertEqual(errs, [], f"AGENTS.md:{blk.start_line}: {errs}")

    def test_t2_f13_04_no_stale_counts_without_heading_false_positives(self) -> None:
        root = common.get_repo_root()
        for rel in ("AGENTS.md", "plugin/rules/AGENTS.md"):
            hits = common.find_stale_role_counts(common.read_text_utf8(root / rel))
            self.assertEqual(hits, [], f"Stale count in {rel}: {hits}")

    def test_t2_f13_05_preserves_ground_truth_constants(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        for val in ("2844", "1440", "0.9251", "0.9971", "0.9961"):
            self.assertIn(val, txt, f"AGENTS.md dropped §8 ground truth constant {val}")


class TestBoundaryF14PythonRuntime(unittest.TestCase):
    """Boundary checks for F14 (src/ Python modules)."""

    def test_t2_f14_01_all_src_python_files_parse_and_compile(self) -> None:
        root = common.get_repo_root()
        py_files = sorted((root / "src").rglob("*.py"))
        self.assertGreaterEqual(len(py_files), 3)
        for pyf in py_files:
            ast.parse(common.read_text_utf8(pyf), filename=str(pyf))
            py_compile.compile(str(pyf), doraise=True)

    def test_t2_f14_02_zero_emojis_in_src_python(self) -> None:
        root = common.get_repo_root()
        for pyf in sorted((root / "src").rglob("*.py")):
            hits = common.find_emojis(common.read_text_utf8(pyf))
            self.assertEqual(hits, [], f"Emojis in {pyf}: {hits}")

    def test_t2_f14_03_personas_cxagents_zero_duplicate_role_lines(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        self.assertIn("cxagents", configs, "Missing cxagents SubagentConfig in personas.py")
        block = configs["cxagents"]["system_instructions"]
        non_empty = [ln.strip() for ln in block.splitlines() if ln.strip()]
        seen_lines: set[str] = set()
        dup_lines: list[str] = []
        for ln in non_empty:
            if ln in seen_lines:
                dup_lines.append(ln)
            seen_lines.add(ln)
        self.assertEqual(
            dup_lines,
            [],
            f"Duplicate non-empty lines in cxagents system_instructions: {dup_lines}",
        )
        role_lines = [ln for ln in non_empty if ln.startswith("- ")]
        roles = [ln.split(":", 1)[0].lstrip("- ").strip() for ln in role_lines]
        self.assertEqual(len(roles), len(set(roles)), f"Duplicate roles in cxagents system_instructions: {roles}")

    def test_t2_f14_04_team_py_zero_stale_role_counts(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "src" / "team.py")
        self.assertEqual(common.find_stale_role_counts(txt), [])
        self.assertEqual(common.find_emojis(txt), [])

    def test_t2_f14_05_personas_rust_engineer_ast_single_line_description(self) -> None:
        root = common.get_repo_root()
        personas_path = root / "src" / "agents" / "personas.py"
        tree = ast.parse(common.read_text_utf8(personas_path), filename=str(personas_path))
        found = False
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "rust_engineer":
                        found = True
                        self.assertIsInstance(node.value, ast.Call)
                        assert isinstance(node.value, ast.Call)
                        kw_map = {kw.arg: kw.value for kw in node.value.keywords if kw.arg}
                        self.assertIn("name", kw_map)
                        self.assertIn("description", kw_map)
                        name_val = ast.literal_eval(kw_map["name"])
                        desc_val = ast.literal_eval(kw_map["description"])
                        self.assertEqual(name_val, "rust_engineer")
                        self.assertTrue(bool(desc_val.strip()))
                        self.assertNotIn("\n", desc_val)
        self.assertTrue(found, "rust_engineer SubagentConfig assignment not found in personas.py")


class TestBoundaryF15DocsCliManifests(unittest.TestCase):
    """Boundary checks for F15 (docs, CLI, manifests, and workflow exclusions)."""

    def test_t2_f15_01_zero_stale_role_counts_across_docs_cli_manifests(self) -> None:
        root = common.get_repo_root()
        targets = (
            "CLAUDE.md",
            "README.md",
            "bin/cxops.js",
            "cx",
            "cx.ps1",
            *common.JSON_MANIFEST_RELPATHS,
        )
        for rel in targets:
            path = root / rel
            self.assertTrue(path.is_file(), f"Missing target file: {rel}")
            hits = common.find_stale_role_counts(common.read_text_utf8(path))
            self.assertEqual(hits, [], f"Stale count in {rel}: {hits}")

    def test_t2_f15_02_all_6_json_manifests_valid_utf8_json(self) -> None:
        root = common.get_repo_root()
        for rel in common.JSON_MANIFEST_RELPATHS:
            path = root / rel
            self.assertTrue(path.is_file(), f"Missing JSON manifest: {rel}")
            parsed = json.loads(common.read_text_utf8(path))
            self.assertIsInstance(parsed, dict)

    def test_t2_f15_03_zero_emojis_across_docs_cli_manifests(self) -> None:
        root = common.get_repo_root()
        for rel in (
            "CLAUDE.md",
            "README.md",
            "verify_agents.py",
            "bin/cxops.js",
            "cx",
            "cx.ps1",
            *common.JSON_MANIFEST_RELPATHS,
        ):
            path = root / rel
            if path.is_file():
                hits = common.find_emojis(common.read_text_utf8(path))
                self.assertEqual(hits, [], f"Emojis in {rel}: {hits}")

    def test_t2_f15_04_cortexops_owned_files_zero_emojis_workflows_excluded(self) -> None:
        root = common.get_repo_root()
        files = common.iter_cortexops_text_files(root)
        self.assertGreaterEqual(len(files), 20)
        for path in files:
            self.assertNotIn(
                ("plugin", "workflows"),
                list(zip(path.parts, path.parts[1:])),
                f"plugin/workflows should be excluded from CortexOps zero-emoji gate: {path}",
            )
            hits = common.find_emojis(common.read_text_utf8(path))
            self.assertEqual(hits, [], f"Emojis in {path}: {hits}")

    def test_t2_f15_05_unmodified_agents_frontmatter_no_false_positives(self) -> None:
        for role in common.ALL_ROLES:
            fm = _assert_single_line_agent_description(self, role)
            self.assertEqual(fm["duplicate_tools"], [], f"Duplicate tools in {role}.md")
            self.assertEqual(fm["unknown_keys"], [], f"Unknown keys in {role}.md")
            self.assertTrue(bool(fm["tools"]), f"Empty tools list in {role}.md")
            if role in ("al_developer", "frontend_engineer"):
                self.assertEqual(fm["tools"], list(common.STANDARD_7_TOOLS))
