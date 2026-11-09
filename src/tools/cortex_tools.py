"""ThutaCortex integration tools for Thea Senior Engineering Team.

Enables agents to search existing institutional knowledge, read product architectures,
and ingest atomic concepts, research reports, and literature references into Thuta Tun's
second brain (/home/lenovo/Documents/ThutaCortex).
"""

import os
import re
from pathlib import Path

VAULT_DIR = Path("/home/lenovo/Documents/ThutaCortex")


def _has_emoji(s: str) -> bool:
    """Checks if a string contains emojis or prohibited symbols."""
    for ch in s:
        cp = ord(ch)
        if (
            0x1F600 <= cp <= 0x1F64F
            or 0x1F300 <= cp <= 0x1F5FF
            or 0x1F680 <= cp <= 0x1F6FF
            or 0x1F700 <= cp <= 0x1F77F
            or 0x1F780 <= cp <= 0x1F7FF
            or 0x1F800 <= cp <= 0x1F8FF
            or 0x1F900 <= cp <= 0x1F9FF
            or 0x1FA00 <= cp <= 0x1FA6F
            or 0x1FA70 <= cp <= 0x1FAFF
            or 0x2600 <= cp <= 0x26FF
            or 0x2700 <= cp <= 0x27BF
        ):
            return True
    return False


def search_cortex(query: str, subfolder: str = "") -> str:
    """Searches markdown notes in ThutaCortex second brain.

    Args:
        query: Keywords or phrases to search for.
        subfolder: Optional subfolder within the vault (e.g. 'Projects', 'Resources/Concepts', 'Areas').

    Returns:
        Formatted summary of matching notes with relative paths and excerpts.
    """
    if not VAULT_DIR.exists():
        return f"Error: ThutaCortex vault not found at {VAULT_DIR}."

    target_dir = VAULT_DIR / subfolder if subfolder else VAULT_DIR
    if not target_dir.exists():
        return f"Error: Target directory {target_dir} does not exist."

    matches = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for root, dirs, files in os.walk(target_dir):
        if ".obsidian" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                file_path = Path(root) / f
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                    if pattern.search(content) or pattern.search(f):
                        rel_path = file_path.relative_to(VAULT_DIR)
                        # Extract first matching line excerpt
                        excerpt = ""
                        for line in content.splitlines():
                            if pattern.search(line) and not line.startswith("---") and not line.startswith("tags:"):
                                excerpt = line.strip()[:140]
                                break
                        matches.append(f"- [[{rel_path.stem}]] ({rel_path})\n  Excerpt: {excerpt or 'Matched in note title'}")
                except Exception as e:
                    continue

    if not matches:
        return f"No notes found matching query: '{query}' in ThutaCortex."

    result = f"ThutaCortex Search Results for '{query}' ({len(matches)} notes found):\n\n"
    result += "\n".join(matches[:25])
    return result


def read_cortex_note(relative_path: str) -> str:
    """Reads a note from the ThutaCortex second brain.

    Args:
        relative_path: Relative path to note inside vault (e.g. 'Projects/Specimen-X.md', 'Areas/Thea-Solutions/Overview.md').

    Returns:
        Full content of the note.
    """
    if not VAULT_DIR.exists():
        return f"Error: ThutaCortex vault not found at {VAULT_DIR}."

    note_path = VAULT_DIR / relative_path
    if not note_path.suffix:
        note_path = note_path.with_suffix(".md")

    if not note_path.exists():
        return f"Error: Note not found at {note_path}."

    try:
        with open(note_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading note {relative_path}: {str(e)}"


def ingest_concept_to_cortex(
    title: str,
    content: str,
    domain_tag: str,
    up_link: str = "Distributed-Systems-MOC",
    related: list[str] = None,
) -> str:
    """Ingests an atomic Zettelkasten concept note into ThutaCortex (Resources/Concepts/).

    Args:
        title: Note title (e.g., 'Anti-Poisoning-Streaming-POT' or 'Deterministic-State-Verification').
        content: The technical body (markdown, single mechanism, equations/diagrams, trade-offs).
        domain_tag: Hierarchical tag (e.g., 'architecture/patterns', 'ai/eval', 'database/concurrency').
        up_link: Parent Map of Content (MOC) note name.
        related: List of related wikilink note names (e.g., ['Thea-Engineering-Team', 'Specimen-X']).

    Returns:
        Confirmation message with file path.
    """
    if not VAULT_DIR.exists():
        return f"Error: ThutaCortex vault not found at {VAULT_DIR}."

    # Validate zero-emoji rule
    if _has_emoji(title) or _has_emoji(content):
        return "Error: Content violates the strict ThutaCortex zero-emoji invariant."

    clean_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-")
    file_path = VAULT_DIR / "Resources" / "Concepts" / f"{clean_title}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    rel_tags = [f"  - {domain_tag}"] if domain_tag else ["  - concept"]
    rel_links = [f'  - "[[{r}]]"' for r in (related or [])]

    frontmatter = f"""---
title: "{title}"
type: concept
created: {os.popen('date +%Y-%m-%d').read().strip()}
tags:
  - concept
{chr(10).join(rel_tags)}
up: "[[{up_link}]]"
related:
{chr(10).join(rel_links) if rel_links else '  - "[[Projects-MOC]]"'}
---

# {title}

{content.strip()}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    return f"Successfully ingested atomic concept note: Resources/Concepts/{clean_title}.md"
