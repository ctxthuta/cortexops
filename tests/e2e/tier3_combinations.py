"""Tier 3 E2E Cross-Feature Pairwise Combination Tests (>= 15 tests)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import unittest

from . import common


def _probe_team(repo_root) -> dict[str, object]:
    py = common.find_runtime_python(repo_root)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)
    script = (
        "import json; "
        "from src.team import create_cortexops_team; "
        "t = create_cortexops_team(); "
        "subs = [s.name for s in t.subagents]; "
        "allowed = list(t.capabilities.allowed_subagents); "
        "print(json.dumps({'subagents': subs, 'allowed': allowed}))"
    )
    proc = subprocess.run(
        [str(py), "-c", script],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"Failed to instantiate src.team.create_cortexops_team() with {py}: "
            f"{proc.stderr or proc.stdout}"
        )
    return json.loads(proc.stdout.strip().splitlines()[-1])


class TestCrossFeatureCombinations(unittest.TestCase):
    """Pairwise cross-feature parity and consistency checks (T3-01 .. T3-16)."""

    def test_t3_01_agents_md_byte_identical_to_plugin_rules(self) -> None:
        root = common.get_repo_root()
        a = (root / "AGENTS.md").read_bytes()
        b = (root / "plugin" / "rules" / "AGENTS.md").read_bytes()
        self.assertEqual(a, b, "AGENTS.md and plugin/rules/AGENTS.md diverged")

    def test_t3_02_plugin_json_byte_identical_to_antigravity_plugin_json(self) -> None:
        root = common.get_repo_root()
        a = (root / "plugin" / "plugin.json").read_bytes()
        b = (root / ".antigravity-plugin" / "plugin.json").read_bytes()
        self.assertEqual(a, b, "plugin/plugin.json and .antigravity-plugin/plugin.json diverged")

    def test_t3_03_rust_engineer_dot_agents_mirror_identical(self) -> None:
        root = common.get_repo_root()
        src = root / "plugin" / "agents" / "rust_engineer.md"
        dst = root / ".agents" / "agents" / "rust_engineer" / "agent.md"
        self.assertTrue(src.is_file(), f"Missing {src}")
        self.assertTrue(dst.is_file(), f"Missing {dst}")
        self.assertEqual(src.read_bytes(), dst.read_bytes())

    def test_t3_04_all_26_dot_agents_mirrors_identical(self) -> None:
        root = common.get_repo_root()
        for role in common.ALL_ROLES:
            src = root / "plugin" / "agents" / f"{role}.md"
            dst = root / ".agents" / "agents" / role / "agent.md"
            self.assertTrue(src.is_file(), f"Missing {src}")
            self.assertTrue(dst.is_file(), f"Missing {dst}")
            self.assertEqual(
                src.read_bytes(),
                dst.read_bytes(),
                f".agents/agents/{role}/agent.md differs from plugin/agents/{role}.md",
            )

    def test_t3_05_agent_skill_bidirectional_set_parity(self) -> None:
        root = common.get_repo_root()
        agent_names = {p.stem for p in (root / "plugin" / "agents").glob("*.md")}
        skill_names = {
            common.kebab_to_snake(p.parent.name)
            for p in (root / "plugin" / "skills").glob("*/SKILL.md")
        }
        self.assertEqual(agent_names, set(common.ALL_ROLES))
        self.assertEqual(agent_names, skill_names)
        for role in common.ALL_ROLES:
            skill_path = (
                root / "plugin" / "skills" / common.snake_to_kebab(role) / "SKILL.md"
            )
            fm = common.parse_skill_frontmatter(skill_path)
            self.assertEqual(fm["name"], common.snake_to_kebab(role))
            self.assertTrue(bool(fm["description"]), f"Empty description in {skill_path}")

    def test_t3_06_rust_engineer_agent_skill_description_parity(self) -> None:
        root = common.get_repo_root()
        agent_fm = common.parse_agent_frontmatter(
            root / "plugin" / "agents" / "rust_engineer.md"
        )
        skill_fm = common.parse_skill_frontmatter(
            root / "plugin" / "skills" / "rust-engineer" / "SKILL.md"
        )
        self.assertEqual(
            str(agent_fm["description"]).strip(),
            str(skill_fm["description"]).strip(),
            "rust_engineer agent and skill descriptions must match",
        )

    def test_t3_07_cxagents_agent_and_skill_cover_all_25_specialists(self) -> None:
        root = common.get_repo_root()
        cx_agent = common.read_text_utf8(root / "plugin" / "agents" / "cxagents.md")
        cx_skill = common.read_text_utf8(
            root / "plugin" / "skills" / "cxagents" / "SKILL.md"
        )
        for role in common.ALL_SPECIALIST_ROLES:
            self.assertIn(f"`{role}`", cx_agent, f"cxagents.md missing `{role}`")
            self.assertRegex(
                cx_skill,
                rf"(?<![a-z0-9_]){re.escape(role)}(?![a-z0-9_])",
                f"cxagents/SKILL.md missing {role}",
            )

    def test_t3_08_agents_md_index_covers_all_26_roles(self) -> None:
        root = common.get_repo_root()
        txt = common.read_text_utf8(root / "AGENTS.md")
        for role in common.ALL_ROLES:
            self.assertRegex(
                txt,
                rf"(?m)^###\s+\d+\..*\(`{re.escape(role)}`\)|^###\s+\d+\..*`{re.escape(role)}`",
                f"AGENTS.md missing numbered heading for {role}",
            )

    def test_t3_09_team_py_subagents_equals_allowed_subagents_no_duplicates(self) -> None:
        root = common.get_repo_root()
        info = _probe_team(root)
        subs = list(info["subagents"])  # type: ignore[arg-type]
        allowed = list(info["allowed"])  # type: ignore[arg-type]
        self.assertEqual(len(subs), len(set(subs)), f"Duplicate subagents: {subs}")
        self.assertEqual(len(allowed), len(set(allowed)), f"Duplicate allowed: {allowed}")
        self.assertEqual(subs, allowed, "team.subagents and allowed_subagents diverged")

    def test_t3_10_rust_engineer_registered_in_personas_and_team(self) -> None:
        root = common.get_repo_root()
        agent_fm = common.parse_agent_frontmatter(
            root / "plugin" / "agents" / "rust_engineer.md"
        )
        info = _probe_team(root)
        self.assertIn(agent_fm["name"], info["subagents"])  # type: ignore[operator]
        self.assertIn(agent_fm["name"], info["allowed"])  # type: ignore[operator]

    def test_t3_11_personas_cxagents_aligned_with_team_specialists(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        self.assertIn("cxagents", configs, "Missing cxagents SubagentConfig in personas.py")
        cx_block = configs["cxagents"]["system_instructions"]
        info = _probe_team(root)
        for role in (*common.RUST_UPDATED_ROLES, "rust_engineer"):
            self.assertIn(role, cx_block, f"cxagents system_instructions missing {role}")
            self.assertIn(role, info["subagents"], f"team.py missing {role}")  # type: ignore[operator]

    def test_t3_12_m2_rust_roles_synced_between_plugin_and_personas(self) -> None:
        root = common.get_repo_root()
        configs = common.parse_personas_subagents(root / "src" / "agents" / "personas.py")
        for role in common.M2_ROLES:
            agent_txt = common.read_text_utf8(root / "plugin" / "agents" / f"{role}.md")
            self.assertRegex(
                agent_txt.lower(),
                r"\b(?:rust(?:_engineer)?|cargo)\b",
                f"{role}.md missing rust/cargo",
            )
            self.assertIn(role, configs, f"Missing {role} SubagentConfig in personas.py")
            self.assertRegex(
                configs[role]["system_instructions"].lower(),
                r"\b(?:rust(?:_engineer)?|cargo)\b",
                f"{role}.system_instructions missing rust/cargo",
            )

    def test_t3_13_rust_engineer_registered_across_docs_and_manifests(self) -> None:
        root = common.get_repo_root()
        claude_txt = common.read_text_utf8(root / "CLAUDE.md")
        readme_txt = common.read_text_utf8(root / "README.md")
        self.assertIn("@rust_engineer", claude_txt)
        self.assertTrue("rust_engineer" in readme_txt or "Rust Engineer" in readme_txt)
        for rel in (
            "plugin/plugin.json",
            ".antigravity-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            "package.json",
        ):
            data = json.loads(common.read_text_utf8(root / rel))
            keywords = [str(k).lower() for k in data.get("keywords", [])]
            self.assertTrue(any("rust" in k for k in keywords), f"{rel} missing rust keyword")

    def test_t3_14_role_counts_consistent_across_rules_cxagents_docs_cli(self) -> None:
        root = common.get_repo_root()
        files = (
            "AGENTS.md",
            "plugin/rules/AGENTS.md",
            "plugin/agents/cxagents.md",
            "plugin/skills/cxagents/SKILL.md",
            "CLAUDE.md",
            "README.md",
            "bin/cxops.js",
            "cx",
            "cx.ps1",
        )
        for rel in files:
            hits = common.find_stale_role_counts(common.read_text_utf8(root / rel))
            self.assertEqual(hits, [], f"Stale role count in {rel}: {hits}")

    def test_t3_15_all_rust_blocks_across_repo_pass_hygiene(self) -> None:
        root = common.get_repo_root()
        blocks, unclosed, _ = common.extract_rust_blocks(root)
        self.assertEqual(unclosed, [], f"Unclosed fences: {unclosed}")
        self.assertGreaterEqual(len(blocks), 1, "No ```rust blocks found")
        for blk in blocks:
            violations = common.find_rust_hygiene_violations(blk.code, blk.info)
            self.assertEqual(
                violations,
                [],
                f"{blk.file}:{blk.start_line}: Rust snippet hygiene violations: {violations}",
            )

    def test_t3_16_core_manifest_versions_consistent(self) -> None:
        root = common.get_repo_root()
        paths = (
            "package.json",
            "plugin/plugin.json",
            ".antigravity-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        )
        versions = {
            rel: json.loads(common.read_text_utf8(root / rel)).get("version")
            for rel in paths
        }
        unique_versions = set(versions.values())
        self.assertEqual(
            len(unique_versions),
            1,
            f"Manifest versions out of sync: {versions}",
        )
