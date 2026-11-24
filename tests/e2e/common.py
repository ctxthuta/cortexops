"""Shared utilities, parsers, and validators for CortexOps E2E tests."""

from __future__ import annotations

import ast
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

HOST_REPO_ROOT = Path(__file__).resolve().parents[2]
_ACTIVE_REPO_ROOT: Path | None = None

ORCHESTRATOR_ROLE = "cxagents"

ALL_SPECIALIST_ROLES: tuple[str, ...] = (
    "academic_researcher",
    "agent_architect",
    "ai_ml_engineer",
    "ai_redteam_engineer",
    "al_developer",
    "appsec_engineer",
    "backend_engineer",
    "chaos_engineer",
    "code_reviewer",
    "compiler_engineer",
    "compliance_engineer",
    "consensus_engineer",
    "cryptography_engineer",
    "data_engineer",
    "database_engineer",
    "devops_engineer",
    "ebpf_engineer",
    "embedded_systems_engineer",
    "finops_engineer",
    "frontend_engineer",
    "gpu_kernel_engineer",
    "mlops_engineer",
    "mobile_engineer",
    "network_protocol_engineer",
    "perf_engineer",
    "platform_engineer",
    "qa_engineer",
    "rnd_researcher",
    "rust_engineer",
    "search_retrieval_engineer",
    "software_engineer",
    "synthetic_data_engineer",
    "systems_integrator",
    "system_architect",
    "uiux_designer",
)

ALL_ROLES: tuple[str, ...] = tuple(sorted((*ALL_SPECIALIST_ROLES, ORCHESTRATOR_ROLE)))

RUST_UPDATED_ROLES: tuple[str, ...] = (
    "backend_engineer",
    "software_engineer",
    "ebpf_engineer",
    "perf_engineer",
    "data_engineer",
    "system_architect",
    "code_reviewer",
    "qa_engineer",
    "appsec_engineer",
)

M2_ROLES: tuple[str, ...] = (*RUST_UPDATED_ROLES, ORCHESTRATOR_ROLE)

STANDARD_7_TOOLS: tuple[str, ...] = (
    "send_message",
    "view_file",
    "search_web",
    "write_file",
    "edit_file",
    "run_command",
    "manage_task",
)

EXTENDED_9_TOOLS: tuple[str, ...] = (
    "send_message",
    "view_file",
    "search_web",
    "schedule",
    "generate_image",
    "write_file",
    "edit_file",
    "run_command",
    "manage_task",
)

JSON_MANIFEST_RELPATHS: tuple[str, ...] = (
    "plugin/plugin.json",
    ".antigravity-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    "package.json",
)

AGENTS_ROLE_NUMBER_MAP: dict[str, int] = {
    "system_architect": 3,
    "backend_engineer": 6,
    "software_engineer": 7,
    "qa_engineer": 10,
    "code_reviewer": 11,
    "cxagents": 13,
    "data_engineer": 15,
    "perf_engineer": 17,
    "appsec_engineer": 19,
    "ebpf_engineer": 24,
    "rust_engineer": 27,
}

_FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})([^\n]*)$")
_HTML_TAG_RE = re.compile(
    r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s+[^<>]*)?/?>"
)
_MERMAID_HEADER_RE = re.compile(
    r"^(?:flowchart\s+(?:TD|TB|BT|RL|LR)|graph\s+(?:TD|TB|BT|RL|LR)|"
    r"sequenceDiagram|erDiagram|classDiagram|stateDiagram-v2)\b"
)
_NUMBERED_STEP_COMMENT_RE = re.compile(
    r"^\s*(?://|#|/\*+)\s*(?:Step\s+\d+\b|\d+[.)]\s)",
    re.IGNORECASE,
)
_STALE_ROLE_COUNT_RES: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?i)\b(?:11|12|13|24)\s+(?:CortexOps\s+)?"
        r"(?:Staff(?:/|\s+and\s+)Principal\s+)?"
        r"(?:(?:specialist|specialized|declarative|engineering)\s+)*"
        r"(?:roles|personas|agents|specialists|subagent\s+definitions|subagents)\b"
    ),
    re.compile(
        r"(?i)\ball\s+(?:11|12|13|24)\s+"
        r"(?:subagents|agents|specialist|specialized|declarative)\b"
    ),
)

_UNSAFE_FN_RE = re.compile(
    r"\bunsafe\s+(?:extern\s+(?:\"[^\"]*\"\s+)?|async\s+)?fn\b"
)
_UNSAFE_BLOCK_OR_ITEM_RE = re.compile(
    r"\bunsafe\s*(?:\{|impl\b|trait\b|extern\b)"
)

_FOLDED_YAML_MARKERS = {">-", ">", "|", "|-", "|+", ">+"}
_KNOWN_AGENT_BOOL_POLICY_KEYS = {
    "name",
    "description",
    "tools",
    "inheritCustomizations",
    "inheritMcp",
    "mainAgent",
    "subagent",
    "commandExecutionPolicy",
}


@dataclass(frozen=True)
class FencedBlock:
    """Represents a fenced markdown code block with source coordinates."""

    file: Path
    start_line: int
    end_line: int
    info: str
    lang: str
    code: str


def set_repo_root(path: Path | str | None) -> None:
    """Sets the active repository root for E2E test execution."""
    global _ACTIVE_REPO_ROOT
    if path is None:
        _ACTIVE_REPO_ROOT = None
    else:
        _ACTIVE_REPO_ROOT = Path(path).resolve()


def get_repo_root() -> Path:
    """Returns the active repository root, favoring explicit or env override."""
    if _ACTIVE_REPO_ROOT is not None:
        return _ACTIVE_REPO_ROOT
    env_root = os.environ.get("CORTEXOPS_E2E_REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return HOST_REPO_ROOT


def snake_to_kebab(name: str) -> str:
    """Converts snake_case identifier to kebab-case."""
    return name.replace("_", "-")


def kebab_to_snake(name: str) -> str:
    """Converts kebab-case identifier to snake_case."""
    return name.replace("-", "_")


def read_text_utf8(path: Path) -> str:
    """Reads a UTF-8 text file cleanly."""
    return path.read_text(encoding="utf-8")


def extract_frontmatter_lines(path: Path) -> list[str]:
    """Extracts YAML frontmatter lines strictly between opening and closing ---."""
    lines = read_text_utf8(path).splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing opening '---' YAML frontmatter marker")
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return lines[1:idx]
    raise ValueError(f"{path}: unclosed YAML frontmatter block")


def _strip_yaml_quotes(value: str) -> str:
    val = value.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        return val[1:-1]
    return val


def parse_agent_frontmatter(path: Path) -> dict[str, object]:
    """Parses agent markdown frontmatter using strict boundary slicing."""
    fm_lines = extract_frontmatter_lines(path)
    result: dict[str, object] = {
        "name": "",
        "description": "",
        "raw_description_value": "",
        "description_folded": False,
        "description_multiline": False,
        "tools": [],
        "duplicate_tools": [],
        "unknown_keys": [],
        "keys": [],
    }
    in_tools = False
    in_desc_continuation = False
    seen_tools: set[str] = set()
    tools_list: list[str] = []
    dup_tools: list[str] = []
    unknown_keys: list[str] = []
    keys: list[str] = []

    for raw_line in fm_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        is_indented = raw_line.startswith((" ", "\t"))
        if in_tools and is_indented and stripped.startswith("- "):
            tool_name = _strip_yaml_quotes(stripped[2:])
            if tool_name in seen_tools:
                dup_tools.append(tool_name)
            seen_tools.add(tool_name)
            tools_list.append(tool_name)
            continue
        if in_desc_continuation and (
            is_indented or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", raw_line)
        ):
            result["description_multiline"] = True
            prev = str(result["description"])
            result["description"] = f"{prev} {stripped}".strip()
            continue

        in_tools = False
        in_desc_continuation = False
        if ":" not in raw_line:
            continue
        key, raw_val = raw_line.split(":", 1)
        key = key.strip()
        val = raw_val.strip()
        keys.append(key)
        if key not in _KNOWN_AGENT_BOOL_POLICY_KEYS:
            unknown_keys.append(key)

        if key == "name":
            result["name"] = _strip_yaml_quotes(val)
        elif key == "description":
            result["raw_description_value"] = val
            if val in _FOLDED_YAML_MARKERS or val == "":
                result["description_folded"] = val in _FOLDED_YAML_MARKERS
                in_desc_continuation = True
                result["description"] = ""
            else:
                result["description"] = _strip_yaml_quotes(val)
                in_desc_continuation = True
        elif key == "tools":
            in_tools = True
        else:
            lowered = val.lower()
            if lowered == "true":
                result[key] = True
            elif lowered == "false":
                result[key] = False
            else:
                result[key] = _strip_yaml_quotes(val)

    result["tools"] = tools_list
    result["duplicate_tools"] = dup_tools
    result["unknown_keys"] = unknown_keys
    result["keys"] = keys
    return result


def parse_skill_frontmatter(path: Path) -> dict[str, object]:
    """Parses SKILL.md frontmatter including folded multi-line descriptions."""
    fm_lines = extract_frontmatter_lines(path)
    name = ""
    desc_parts: list[str] = []
    is_folded = False
    in_desc = False

    for raw_line in fm_lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        is_indented = raw_line.startswith((" ", "\t"))
        if in_desc and is_indented:
            desc_parts.append(stripped)
            continue
        in_desc = False
        if ":" not in raw_line:
            continue
        key, raw_val = raw_line.split(":", 1)
        key = key.strip()
        val = raw_val.strip()
        if key == "name":
            name = _strip_yaml_quotes(val)
        elif key == "description":
            in_desc = True
            if val in _FOLDED_YAML_MARKERS:
                is_folded = True
            elif val:
                desc_parts.append(_strip_yaml_quotes(val))

    return {
        "name": name,
        "description": " ".join(desc_parts).strip(),
        "is_folded": is_folded,
    }


def _is_emoji_codepoint(cp: int) -> bool:
    if 0x1F300 <= cp <= 0x1FAFF:
        return True
    if 0x2600 <= cp <= 0x27BF:
        return True
    if 0x2300 <= cp <= 0x23FF:
        return True
    if 0x2B00 <= cp <= 0x2BFF:
        return True
    if 0x1F000 <= cp <= 0x1F2FF:
        return True
    if 0x1F1E6 <= cp <= 0x1F1FF:
        return True
    if cp in (0xFE0F, 0x200D):
        return True
    return False


def _eval_ast_str(node: ast.AST | None, env: dict[str, str]) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _eval_ast_str(node.left, env)
        right = _eval_ast_str(node.right, env)
        if left is not None and right is not None:
            return left + right
    return None


def parse_personas_subagents(personas_path: Path) -> dict[str, dict[str, str]]:
    """Extracts SubagentConfig definitions and resolves system_instructions via AST."""
    tree = ast.parse(read_text_utf8(personas_path), filename=str(personas_path))
    str_vars: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            val = _eval_ast_str(node.value, str_vars)
            if val is not None:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        str_vars[target.id] = val
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            val = _eval_ast_str(node.value, str_vars)
            if val is not None and isinstance(node.target, ast.Name):
                str_vars[node.target.id] = val

    configs: dict[str, dict[str, str]] = {}
    for node in tree.body:
        target_var = ""
        call_node: ast.Call | None = None
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call_node = node.value
            for target in node.targets:
                if isinstance(target, ast.Name):
                    target_var = target.id
                    break
        elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Call):
            call_node = node.value
            if isinstance(node.target, ast.Name):
                target_var = node.target.id
        if call_node is None:
            continue
        func = call_node.func
        func_name = (
            func.attr
            if isinstance(func, ast.Attribute)
            else (func.id if isinstance(func, ast.Name) else "")
        )
        if func_name != "SubagentConfig":
            continue
        kw_map = {kw.arg: kw.value for kw in call_node.keywords if kw.arg}
        role_name = _eval_ast_str(kw_map.get("name"), str_vars) or target_var
        if not role_name:
            continue
        desc = _eval_ast_str(kw_map.get("description"), str_vars) or ""
        instr_node = kw_map.get("system_instructions")
        instr = _eval_ast_str(instr_node, str_vars) or ""
        instr_var = instr_node.id if isinstance(instr_node, ast.Name) else ""
        configs[role_name] = {
            "var_name": target_var,
            "description": desc,
            "system_instructions": instr,
            "instr_var": instr_var,
        }
    return configs


def find_emojis(text: str) -> list[tuple[int, str, str]]:
    """Returns (line_no, char, codepoint_hex) for any emoji characters found."""
    hits: list[tuple[int, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for ch in line:
            cp = ord(ch)
            if _is_emoji_codepoint(cp):
                hits.append((line_no, ch, f"U+{cp:04X}"))
    return hits


def iter_cortexops_text_files(repo_root: Path) -> list[Path]:
    """Returns all CortexOps-owned text files excluding upstream plugin/workflows."""
    candidates: set[Path] = set()

    for rel_dir in (
        "plugin/agents",
        "plugin/skills",
        "plugin/rules",
        ".agents/agents",
        "src",
        "tests/e2e",
    ):
        base = repo_root / rel_dir
        if not base.exists():
            continue
        for item in base.rglob("*"):
            if not item.is_file():
                continue
            if "__pycache__" in item.parts or ".venv" in item.parts:
                continue
            if item.suffix.lower() in (
                ".md",
                ".py",
                ".rs",
                ".toml",
                ".json",
                ".txt",
                ".yaml",
                ".yml",
            ):
                candidates.add(item)

    for rel_file in (
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "verify_agents.py",
        "bin/cxops.js",
        "cx",
        "cx.ps1",
        *JSON_MANIFEST_RELPATHS,
    ):
        p = repo_root / rel_file
        if p.is_file():
            candidates.add(p)

    return sorted(candidates)


def extract_fenced_blocks(
    text: str,
    file_path: Path,
    langs: tuple[str, ...] | None = None,
) -> tuple[list[FencedBlock], list[int]]:
    """Extracts fenced code blocks and reports any unclosed fences."""
    blocks: list[FencedBlock] = []
    unclosed: list[int] = []
    lines = text.splitlines()
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_info = ""
    fence_start = 0
    buf: list[str] = []

    for idx, line in enumerate(lines, 1):
        if not in_fence:
            match = _FENCE_OPEN_RE.match(line)
            if match:
                fence_token = match.group(1)
                fence_char = fence_token[0]
                fence_len = len(fence_token)
                fence_info = match.group(2).strip()
                fence_start = idx
                buf = []
                in_fence = True
        else:
            close_re = re.compile(
                rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$"
            )
            if close_re.match(line):
                lang = ""
                if fence_info:
                    lang = fence_info.split(",")[0].split()[0].lower()
                if langs is None or lang in langs:
                    blocks.append(
                        FencedBlock(
                            file=file_path,
                            start_line=fence_start,
                            end_line=idx,
                            info=fence_info,
                            lang=lang,
                            code="\n".join(buf),
                        )
                    )
                in_fence = False
            else:
                buf.append(line)

    if in_fence:
        unclosed.append(fence_start)

    return blocks, unclosed


def extract_rust_blocks(
    repo_root: Path,
) -> tuple[list[FencedBlock], list[tuple[Path, int]], list[Path]]:
    """Collects all fenced Rust blocks and standalone .rs files across target scopes."""
    scan_files: list[Path] = []
    for rel_dir in ("plugin/agents", "plugin/skills", ".agents/agents", "src"):
        base = repo_root / rel_dir
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts:
                    if p.suffix.lower() in (".md", ".py"):
                        scan_files.append(p)
    for rel_file in (
        "AGENTS.md",
        "plugin/rules/AGENTS.md",
        "CLAUDE.md",
        "README.md",
    ):
        p = repo_root / rel_file
        if p.is_file():
            scan_files.append(p)

    blocks: list[FencedBlock] = []
    unclosed_locations: list[tuple[Path, int]] = []
    for path in scan_files:
        found, unclosed = extract_fenced_blocks(
            read_text_utf8(path), path, langs=("rust", "rs")
        )
        blocks.extend(found)
        for line_no in unclosed:
            unclosed_locations.append((path, line_no))

    rs_files: list[Path] = []
    plugin_dir = repo_root / "plugin"
    if plugin_dir.exists():
        rs_files = sorted(p for p in plugin_dir.rglob("*.rs") if p.is_file())

    return blocks, unclosed_locations, rs_files


def _check_unquoted_flowchart_labels(text: str) -> list[tuple[int, str]]:
    """Detects unquoted or partially quoted node labels with parens or brackets."""
    issues: list[tuple[int, str]] = []
    idx = 0
    n = len(text)
    shape_pairs = (
        ("([", "])"),
        ("[[", "]]"),
        ("[(", ")]"),
        ("((", "))"),
        ("{{", "}}"),
        ("[", "]"),
        ("(", ")"),
        ("{", "}"),
    )

    while idx < n:
        ch = text[idx]
        if ch == '"':
            end_q = text.find('"', idx + 1)
            idx = end_q + 1 if end_q != -1 else n
            continue
        if ch.isalnum() or ch in ("_", "-"):
            id_start = idx
            while idx < n and (text[idx].isalnum() or text[idx] in ("_", "-")):
                idx += 1
            if idx < n and text[idx] in ("[", "(", "{"):
                matched_open = ""
                matched_close = ""
                for op, cl in shape_pairs:
                    if text.startswith(op, idx):
                        matched_open = op
                        matched_close = cl
                        break
                if matched_open:
                    content_start = idx + len(matched_open)
                    depth = 1
                    pos = content_start
                    found_nested = False
                    while pos < n and depth > 0:
                        if text[pos] == '"':
                            end_q = text.find('"', pos + 1)
                            pos = end_q + 1 if end_q != -1 else n
                            continue
                        if text.startswith(matched_close, pos):
                            depth -= 1
                            pos += len(matched_close)
                            if depth == 0:
                                break
                            continue
                        if text[pos] in ("(", ")", "[", "]"):
                            found_nested = True
                        pos += 1
                    if found_nested:
                        node_id = text[id_start:idx]
                        line_no = text[:id_start].count("\n") + 1
                        snippet = text[id_start:pos].replace("\n", "\\n")
                        issues.append(
                            (
                                line_no,
                                f"unquoted Mermaid label with parens/brackets on '{node_id}': "
                                f"{snippet}",
                            )
                        )
                    idx = pos if depth == 0 else content_start
                    continue
        idx += 1

    return issues


def validate_mermaid_block(code: str) -> list[str]:
    """Validates Mermaid diagram header, HTML absence, and quoted node labels."""
    errors: list[str] = []
    non_empty = [
        ln.strip()
        for ln in code.splitlines()
        if ln.strip() and not ln.strip().startswith("%%")
    ]
    if not non_empty:
        return ["empty Mermaid diagram block"]

    header = non_empty[0]
    if not _MERMAID_HEADER_RE.match(header):
        errors.append(f"unsupported Mermaid diagram header: {header!r}")

    is_flowchart = header.startswith(("flowchart ", "graph "))
    flowchart_lines: list[str] = []
    skipped_header = False

    for line_no, raw_line in enumerate(code.splitlines(), 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("%%"):
            flowchart_lines.append("")
            continue
        html_match = _HTML_TAG_RE.search(stripped)
        if html_match:
            errors.append(
                f"line {line_no}: raw HTML tag {html_match.group(0)!r} in Mermaid block"
            )
        if not skipped_header:
            skipped_header = True
            flowchart_lines.append("")
            continue
        if stripped.startswith(("style ", "classDef ", "class ", "linkStyle ")):
            flowchart_lines.append("")
            continue
        flowchart_lines.append(raw_line)

    if is_flowchart:
        for line_no, issue in _check_unquoted_flowchart_labels("\n".join(flowchart_lines)):
            errors.append(f"line {line_no}: {issue}")

    return errors


def find_numbered_step_comments(code: str) -> list[tuple[int, str]]:
    """Detects numbered step comments inside fenced code blocks."""
    hits: list[tuple[int, str]] = []
    for line_no, line in enumerate(code.splitlines(), 1):
        if _NUMBERED_STEP_COMMENT_RE.match(line):
            hits.append((line_no, line.strip()))
    return hits


def _strip_rust_strings_and_line_comment(line: str) -> str:
    out: list[str] = []
    i = 0
    n = len(line)
    in_str = False
    while i < n:
        ch = line[i]
        if in_str:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == "/" and i + 1 < n and line[i + 1] == "/":
            break
        if ch == '"':
            in_str = True
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


class CfgTestScopeTracker:
    """Tracks whether Rust lines fall inside a #[cfg(test)] item block."""

    def __init__(self) -> None:
        self.in_cfg_test = False
        self.pending_cfg_test = False
        self.depth = 0

    def advance(self, line: str) -> bool:
        code_only = _strip_rust_strings_and_line_comment(line)
        if "#[cfg(test)]" in code_only:
            self.pending_cfg_test = True

        if self.pending_cfg_test:
            semi_idx = code_only.find(";")
            brace_idx = code_only.find("{")
            if semi_idx != -1 and (brace_idx == -1 or semi_idx < brace_idx):
                self.pending_cfg_test = False

        line_in_test = self.in_cfg_test
        if self.pending_cfg_test and "{" in code_only:
            self.in_cfg_test = True
            self.pending_cfg_test = False
            self.depth = code_only.count("{") - code_only.count("}")
            line_in_test = True
            if self.depth <= 0:
                self.in_cfg_test = False
                self.depth = 0
        elif self.in_cfg_test:
            self.depth += code_only.count("{") - code_only.count("}")
            if self.depth <= 0:
                self.in_cfg_test = False
                self.depth = 0

        return line_in_test


def _has_safety_annotation(
    lines: list[str],
    idx: int,
    accept_doc_safety: bool,
    check_inner_line: bool,
) -> bool:
    for j in range(idx - 1, max(-1, idx - 4), -1):
        stripped = lines[j].strip()
        if j < idx - 1 and re.search(r"\bunsafe\b", lines[j]) and not stripped.startswith("#["):
            break
        if "// SAFETY:" in lines[j]:
            return True

    for j in range(idx - 1, -1, -1):
        stripped = lines[j].strip()
        if not stripped or stripped.startswith(("//", "#[", "/*", "*")):
            if "// SAFETY:" in lines[j]:
                return True
            if accept_doc_safety and re.search(r"///\s*#\s*Safety\b", lines[j]):
                return True
            if accept_doc_safety and stripped.startswith(("/**", "*")) and re.search(
                r"#\s*Safety\b", lines[j]
            ):
                return True
        else:
            break

    if "// SAFETY:" in lines[idx]:
        return True
    if check_inner_line and idx + 1 < len(lines) and "// SAFETY:" in lines[idx + 1]:
        return True
    return False


def find_rust_hygiene_violations(code: str, info: str = "") -> list[str]:
    """Checks Rust snippet hygiene: no stubs, unannotated unsafe, or non-test unwrap."""
    violations: list[str] = []
    tokens = {tok.strip().lower() for tok in info.replace(",", " ").split() if tok.strip()}
    for banned_mod in ("ignore", "no_run", "compile_fail"):
        if banned_mod in tokens:
            violations.append(f"non-compilable fence modifier '{banned_mod}' in '{info}'")

    if find_emojis(code):
        violations.append("emoji character found inside Rust snippet")

    for line_no, line_txt in find_numbered_step_comments(code):
        violations.append(f"line {line_no}: numbered step comment {line_txt!r}")

    lines = code.splitlines()
    tracker = CfgTestScopeTracker()

    for idx, line in enumerate(lines):
        line_no = idx + 1

        # Check ellipsis placeholders outside variadic extern "C" signatures
        if re.search(r"(?<!\.)(?<!,)\.\.\.(?!\.)", line):
            if not re.search(r",\s*\.\.\.\s*\)", line):
                violations.append(f"line {line_no}: placeholder ellipsis '...' in Rust snippet")

        if re.search(r"\b(?:todo|unimplemented)!\s*\(", line):
            violations.append(f"line {line_no}: unfinished macro stub in Rust snippet")
        if re.search(r"//.*\b(?:TODO|FIXME)\b|/\*.*\b(?:TODO|FIXME)\b", line):
            violations.append(f"line {line_no}: TODO/FIXME comment in Rust snippet")

        in_cfg_test = tracker.advance(line)
        if not in_cfg_test:
            if ".unwrap()" in line or ".expect(" in line:
                violations.append(
                    f"line {line_no}: .unwrap()/.expect() outside #[cfg(test)]"
                )

        if _UNSAFE_FN_RE.search(line):
            if not _has_safety_annotation(
                lines, idx, accept_doc_safety=True, check_inner_line=False
            ):
                violations.append(
                    f"line {line_no}: unsafe fn missing '/// # Safety' or '// SAFETY:' invariant"
                )
        elif _UNSAFE_BLOCK_OR_ITEM_RE.search(line):
            if not _has_safety_annotation(
                lines, idx, accept_doc_safety=False, check_inner_line=True
            ):
                violations.append(
                    f"line {line_no}: unsafe block/item missing '// SAFETY:' invariant comment"
                )

    return violations


def find_stale_role_counts(text: str) -> list[tuple[int, str]]:
    """Detects stale specialist/agent/persona counts (11, 12, 13, 24) in context."""
    hits: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for pat in _STALE_ROLE_COUNT_RES:
            for m in pat.finditer(line):
                hits.append((line_no, m.group(0)))
    return hits


def find_agy_binary() -> Path | None:
    """Resolves the Antigravity CLI binary if installed."""
    candidates = [
        Path.home() / ".gemini" / "bin" / "agy",
        Path.home() / ".local" / "bin" / "agy",
    ]
    which_agy = shutil.which("agy")
    if which_agy:
        candidates.append(Path(which_agy))
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def _find_rust_tool(tool_name: str) -> Path | None:
    which_path = shutil.which(tool_name)
    if which_path:
        return Path(which_path)
    candidates: list[Path] = []
    cargo_home = os.environ.get("CARGO_HOME")
    if cargo_home:
        candidates.append(Path(cargo_home) / "bin" / tool_name)
    candidates.append(Path.home() / ".cargo" / "bin" / tool_name)
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def find_cargo_binary() -> Path | None:
    """Resolves cargo executable from PATH, CARGO_HOME, or ~/.cargo/bin."""
    return _find_rust_tool("cargo")


def find_rustc_binary() -> Path | None:
    """Resolves rustc executable from PATH, CARGO_HOME, or ~/.cargo/bin."""
    return _find_rust_tool("rustc")


def find_node_binary() -> Path | None:
    """Resolves node executable from PATH."""
    which_node = shutil.which("node")
    return Path(which_node) if which_node else None


def find_runtime_python(repo_root: Path) -> Path:
    """Resolves the Python interpreter with project dependencies (.venv preferred)."""
    for cand in (
        repo_root / ".venv" / "bin" / "python3",
        HOST_REPO_ROOT / ".venv" / "bin" / "python3",
    ):
        if cand.is_file() and os.access(cand, os.X_OK):
            return cand
    return Path(sys.executable)


def materialize_rust_workspace(
    blocks: list[FencedBlock],
    rs_files: list[Path],
    workspace_dir: Path,
) -> dict[str, tuple[Path, int]]:
    """Writes extracted Rust snippets as independent workspace crates for Cargo."""
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "Cargo.toml").write_text(
        '[workspace]\nresolver = "2"\nmembers = ["crates/*"]\n',
        encoding="utf-8",
    )
    crate_map: dict[str, tuple[Path, int]] = {}
    items: list[tuple[Path, int, str]] = [
        (blk.file, blk.start_line, blk.code) for blk in blocks
    ]
    for rs_path in rs_files:
        items.append((rs_path, 1, read_text_utf8(rs_path)))

    for idx, (src_file, start_line, code) in enumerate(items, 1):
        crate_name = f"s{idx:03d}"
        crate_dir = workspace_dir / "crates" / crate_name
        src_dir = crate_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (crate_dir / "Cargo.toml").write_text(
            f'[package]\nname = "{crate_name}"\nversion = "0.1.0"\nedition = "2021"\n',
            encoding="utf-8",
        )
        is_bin = bool(
            re.search(r"(?m)^\s*(?:pub\s+)?(?:async\s+)?fn\s+main\s*\(", code)
        )
        target_rs = src_dir / ("main.rs" if is_bin else "lib.rs")
        target_rs.write_text(code + "\n", encoding="utf-8")
        crate_map[crate_name] = (src_file, start_line)

    return crate_map
