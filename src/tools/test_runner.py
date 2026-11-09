"""Deterministic Test Runner & Compiler Verification Tool."""

import subprocess
import os

def run_command(command: str, cwd: str = None, timeout: int = 60) -> str:
    """Executes a shell command (compilers, linters, test suites, git commands) in a specified workspace.
    
    Args:
        command: The shell command to execute (e.g. 'go test -v ./...', 'npm test', 'tsc --noEmit').
        cwd: Directory path to execute within. If omitted, uses current workspace.
        timeout: Execution timeout in seconds (default: 60).
        
    Returns:
        Structured output containing Exit Code, Stdout, and Stderr.
    """
    workdir = cwd or os.getcwd()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        status = "SUCCESS" if proc.returncode == 0 else f"FAILED (Exit Code {proc.returncode})"
        output = [
            f"=== COMMAND RESULT: {status} ===",
            f"Command: {command}",
            f"Directory: {workdir}",
            f"Exit Code: {proc.returncode}\n"
        ]
        
        if proc.stdout:
            output.append(f"--- STDOUT ---\n{proc.stdout}")
        if proc.stderr:
            output.append(f"--- STDERR ---\n{proc.stderr}")
            
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"ERROR: Command '{command}' timed out after {timeout} seconds."
    except Exception as e:
        return f"ERROR: Failed to execute command '{command}': {str(e)}"
