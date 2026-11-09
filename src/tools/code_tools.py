"""Workspace Code & File Management Tools."""

import os
from pathlib import Path

def view_file(path: str, start_line: int = 1, end_line: int = None) -> str:
    """Reads the contents of a file in the workspace with line numbers.
    
    Args:
        path: Path to the file.
        start_line: First line to read (1-indexed).
        end_line: Last line to read (inclusive). If None, reads to end.
    """
    if not os.path.exists(path):
        return f"ERROR: File not found at '{path}'."
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        end = end_line if end_line and end_line <= len(lines) else len(lines)
        start = max(1, start_line)
        
        output = [f"=== File: {path} (Lines {start}-{end} of {len(lines)}) ==="]
        for idx in range(start - 1, end):
            output.append(f"{idx + 1:4d} | {lines[idx].rstrip()}")
        return "\n".join(output)
    except Exception as e:
        return f"ERROR reading file '{path}': {str(e)}"

def create_file(path: str, content: str) -> str:
    """Creates a new file with the specified content. Automatically creates parent directories.
    
    Args:
        path: Path where the file should be written.
        content: The text content of the file.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created file: {path} ({len(content)} bytes)"
    except Exception as e:
        return f"ERROR creating file '{path}': {str(e)}"

def edit_file(path: str, target: str, replacement: str) -> str:
    """Replaces exact target text with replacement text in an existing file.
    
    Args:
        path: Path to the file.
        target: The exact string to replace.
        replacement: The replacement content.
    """
    if not os.path.exists(path):
        return f"ERROR: File '{path}' does not exist."
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
            
        if target not in data:
            return f"ERROR: Target string not found in '{path}'. Please ensure exact whitespace matching."
            
        count = data.count(target)
        new_data = data.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_data)
        return f"Successfully replaced {count} occurrence(s) of target in '{path}'."
    except Exception as e:
        return f"ERROR editing file '{path}': {str(e)}"

def list_directory(path: str = ".") -> str:
    """Lists files and directories at the given path.
    
    Args:
        path: Directory path to list (default: current directory).
    """
    if not os.path.exists(path):
        return f"ERROR: Directory '{path}' does not exist."
    try:
        entries = os.listdir(path)
        dirs = []
        files = []
        for e in sorted(entries):
            full = os.path.join(path, e)
            if os.path.isdir(full):
                dirs.append(f"  [DIR]  {e}/")
            else:
                size = os.path.getsize(full)
                files.append(f"  [FILE] {e} ({size} bytes)")
        return f"=== Directory Listing: {path} ===\n" + "\n".join(dirs + files)
    except Exception as e:
        return f"ERROR listing directory '{path}': {str(e)}"
