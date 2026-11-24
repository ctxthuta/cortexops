"""Tier 4 E2E Real-World Application Scenarios (S1-S8)."""

from __future__ import annotations

import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from . import common


def _map_cargo_errors(
    output: str,
    crate_map: dict[str, tuple[Path, int]],
) -> str:
    """Maps crates/sNNN paths in Cargo stderr back to original doc/skill source lines."""
    mapped: list[str] = []
    for line in output.splitlines():
        m = re.search(r"crates/(s\d{3})/src/(?:main|lib)\.rs:(\d+)", line)
        if m and m.group(1) in crate_map:
            src_file, start_line = crate_map[m.group(1)]
            rel_line = int(m.group(2))
            mapped.append(f"[{src_file}:{start_line + rel_line}] {line}")
        else:
            mapped.append(line)
    return "\n".join(mapped)


class TestRealWorldScenarios(unittest.TestCase):
    """End-to-end execution of real verification commands, runtime APIs, and Cargo."""

    def test_s1_verify_agents_py(self) -> None:
        root = common.get_repo_root()
        script = root / "verify_agents.py"
        self.assertTrue(script.is_file(), f"Missing {script}")
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"verify_agents.py failed: {proc.stderr or proc.stdout}")
        out = proc.stdout
        self.assertIn(f"Found {len(common.ALL_ROLES)} agent definitions", out, f"Unexpected verify_agents output:\n{out}")
        self.assertIn("rust_engineer", out, f"rust_engineer missing from verify_agents output:\n{out}")
        self.assertNotIn("-> >-", out, "Folded YAML >- leaked into verify_agents output")
        self.assertNotIn("-> No description", out, "Missing description in verify_agents output")

    def test_s2_cxops_verify(self) -> None:
        root = common.get_repo_root()
        node = common.find_node_binary()
        self.assertIsNotNone(node, "Node.js binary missing from PATH")
        assert node is not None
        cli = root / "bin" / "cxops.js"
        self.assertTrue(cli.is_file(), f"Missing {cli}")
        proc = subprocess.run(
            [str(node), str(cli), "verify"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"cxops verify failed: {proc.stderr or proc.stdout}")
        out = proc.stdout
        self.assertIn(f"Found {len(common.ALL_ROLES)} agent definitions", out, f"Unexpected cxops verify output:\n{out}")
        self.assertIn("rust_engineer", out)

    def test_s3_agy_plugin_validate(self) -> None:
        root = common.get_repo_root()
        agy = common.find_agy_binary()
        self.assertIsNotNone(
            agy,
            "Antigravity CLI 'agy' not found at ~/.gemini/bin/agy, ~/.local/bin/agy, or PATH",
        )
        assert agy is not None
        proc = subprocess.run(
            [str(agy), "plugin", "validate", str(root / "plugin"), "--strict", "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"agy plugin validate failed (exit {proc.returncode}): {proc.stderr or proc.stdout}",
        )
        payload = json.loads(proc.stdout)
        components = payload.get("components", {})
        self.assertEqual(components.get("agents"), len(common.ALL_ROLES), f"Expected {len(common.ALL_ROLES)} agents: {payload}")
        self.assertEqual(components.get("skills"), len(common.ALL_ROLES), f"Expected {len(common.ALL_ROLES)} skills: {payload}")
        self.assertEqual(components.get("rules"), 1, f"Expected 1 rule: {payload}")
        self.assertEqual(payload.get("findings"), [], f"Unexpected findings: {payload}")

    def test_s4_python_team_instantiation(self) -> None:
        root = common.get_repo_root()
        py = common.find_runtime_python(root)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)
        probe = (
            "import json; "
            "from src.team import create_cortexops_team; "
            "t = create_cortexops_team(); "
            "subs = [s.name for s in t.subagents]; "
            "allowed = list(t.capabilities.allowed_subagents); "
            "print(json.dumps({'subagents': subs, 'allowed': allowed}))"
        )
        proc = subprocess.run(
            [str(py), "-c", probe],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"src.team.create_cortexops_team() failed under {py}: {proc.stderr or proc.stdout}",
        )
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        subs = data["subagents"]
        allowed = data["allowed"]
        self.assertEqual(len(subs), len(set(subs)), f"Duplicate subagents: {subs}")
        self.assertEqual(subs, allowed, "subagents != allowed_subagents")
        for role in ("rust_engineer", *common.RUST_UPDATED_ROLES, "cxagents"):
            self.assertIn(role, subs, f"{role} missing from team.subagents")
            self.assertIn(role, allowed, f"{role} missing from allowed_subagents")

    def test_s5_dashboard_agent_roster(self) -> None:
        root = common.get_repo_root()
        py = common.find_runtime_python(root)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)
        probe = (
            "import json; "
            "from src.dashboard import get_agent_roster; "
            "print(json.dumps(get_agent_roster()))"
        )
        proc = subprocess.run(
            [str(py), "-c", probe],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"get_agent_roster() failed: {proc.stderr or proc.stdout}",
        )
        roster = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(len(roster), len(common.ALL_ROLES), f"Expected {len(common.ALL_ROLES)} agents in roster, got {len(roster)}")
        names = [item["name"] for item in roster]
        self.assertIn("rust_engineer", names)
        for item in roster:
            desc = str(item.get("description", ""))
            self.assertTrue(bool(desc.strip()), f"Empty description for {item['name']}")
            self.assertNotIn(desc, (">-", ">", "|", "No description"), f"Invalid description for {item['name']}: {desc!r}")
            self.assertNotIn("\n", desc, f"Multi-line description for {item['name']}")

        cli_proc = subprocess.run(
            [str(py), str(root / "src" / "dashboard.py"), "--no-color"],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            cli_proc.returncode,
            0,
            f"dashboard.py --no-color failed: {cli_proc.stderr or cli_proc.stdout}",
        )
        self.assertIn(f"{len(common.ALL_ROLES)} Verified Senior Roles", cli_proc.stdout)

    def test_s6_rust_snippets_cargo_check_clippy_test(self) -> None:
        root = common.get_repo_root()
        cargo = common.find_cargo_binary()
        rustc = common.find_rustc_binary()
        self.assertIsNotNone(
            cargo,
            "Rust toolchain missing: cargo not found in PATH, CARGO_HOME, or ~/.cargo/bin",
        )
        self.assertIsNotNone(
            rustc,
            "Rust toolchain missing: rustc not found in PATH, CARGO_HOME, or ~/.cargo/bin",
        )
        assert cargo is not None and rustc is not None

        env = os.environ.copy()
        extra_bins = os.pathsep.join({str(cargo.parent), str(rustc.parent)})
        env["PATH"] = f"{extra_bins}{os.pathsep}{env.get('PATH', '')}"

        clippy_ver = subprocess.run(
            [str(cargo), "clippy", "--version"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            clippy_ver.returncode,
            0,
            f"cargo clippy component missing: {clippy_ver.stderr or clippy_ver.stdout}",
        )

        blocks, unclosed, rs_files = common.extract_rust_blocks(root)
        self.assertEqual(unclosed, [], f"Unclosed markdown fences: {unclosed}")
        self.assertGreaterEqual(
            len(blocks) + len(rs_files),
            1,
            "No ```rust fenced blocks or .rs files found across target docs/skills/agents",
        )

        with tempfile.TemporaryDirectory(prefix="cortexops_rust_e2e_") as tmp_dir:
            ws_dir = Path(tmp_dir)
            crate_map = common.materialize_rust_workspace(blocks, rs_files, ws_dir)
            commands = (
                [str(cargo), "check", "--workspace", "--all-targets"],
                [str(cargo), "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"],
                [str(cargo), "test", "--workspace", "--all-targets"],
            )
            for cmd in commands:
                proc = subprocess.run(
                    cmd,
                    cwd=str(ws_dir),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    check=False,
                )
                if proc.returncode != 0:
                    diag = _map_cargo_errors(f"{proc.stdout}\n{proc.stderr}", crate_map)
                    self.fail(
                        f"Command {' '.join(cmd)} failed with exit code {proc.returncode}:\n{diag}"
                    )

    def test_s7_cxops_doctor_help_and_main_help(self) -> None:
        root = common.get_repo_root()
        node = common.find_node_binary()
        self.assertIsNotNone(node, "Node.js binary missing from PATH")
        assert node is not None
        cli = root / "bin" / "cxops.js"

        for subcmd in ("doctor", "help"):
            proc = subprocess.run(
                [str(node), str(cli), subcmd],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(
                proc.returncode,
                0,
                f"cxops {subcmd} failed: {proc.stderr or proc.stdout}",
            )
            stale = common.find_stale_role_counts(proc.stdout)
            self.assertEqual(stale, [], f"Stale count in cxops {subcmd}: {stale}")
            if subcmd == "doctor":
                self.assertIn(f"{len(common.ALL_ROLES)} verified roles", proc.stdout)
                self.assertNotIn("[FAIL]", proc.stdout)

        py = common.find_runtime_python(root)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)
        main_proc = subprocess.run(
            [str(py), str(root / "src" / "main.py"), "--help"],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            main_proc.returncode,
            0,
            f"src/main.py --help failed: {main_proc.stderr or main_proc.stdout}",
        )
        self.assertEqual(common.find_stale_role_counts(main_proc.stdout), [])

    def test_s8_e2e_self_hygiene(self) -> None:
        root = common.get_repo_root()
        e2e_dir = root / "tests" / "e2e"
        self.assertTrue(e2e_dir.is_dir(), f"Missing {e2e_dir}")
        py_files = sorted(e2e_dir.glob("*.py"))
        self.assertGreaterEqual(len(py_files), 7)
        for pyf in py_files:
            py_compile.compile(str(pyf), doraise=True)
            hits = common.find_emojis(common.read_text_utf8(pyf))
            self.assertEqual(hits, [], f"Emoji found in {pyf}: {hits}")
        self.assertFalse((root / "plugin" / "tests").exists())
        self.assertFalse((root / ".agents" / "tests").exists())
