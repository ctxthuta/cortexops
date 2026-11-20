# Cross-Platform Windows PowerShell Uninstaller for CortexOps Multi-Agent Framework
param (
    [switch]$Force,
    [switch]$Purge
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "============================================================"
Write-Host "Uninstalling CortexOps Multi-Agent Framework (Windows)"
Write-Host "============================================================"

if (-not $Force) {
    $confirm = Read-Host "Are you sure you want to uninstall and unregister all subagents? [y/N]"
    if ($confirm -notmatch "^[Yy]$") {
        Write-Host "Uninstallation aborted."
        exit 0
    }
}

# Plugin junction removal
$PluginsRoot = Join-Path $env:USERPROFILE ".gemini\config\plugins"
foreach ($name in @("cortexops", "thea-engineering-team")) {
    $target = Join-Path $PluginsRoot $name
    if (Test-Path -LiteralPath $target) {
        Write-Host "Removing Antigravity global plugin junction ($name)..."
        $item = Get-Item -LiteralPath $target -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            $item.Delete()
        } else {
            Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Removed junction: $target"
    }
}

# Virtual environment cleanup
$VenvDir = Join-Path $ScriptDir ".venv"
if (Test-Path $VenvDir) {
    Write-Host "Removing Python virtual environment..."
    Remove-Item -Path $VenvDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Removed: $VenvDir"
} else {
    Write-Host "Virtual environment not present."
}

# Artifact and cache cleanup
Write-Host "Cleaning up Python caches and temporary files..."
Get-ChildItem -Path $ScriptDir -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $ScriptDir -Recurse -Filter "*.pyc" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
$WorkspacesDir = Join-Path $ScriptDir "workspaces"
if (Test-Path $WorkspacesDir) {
    Get-ChildItem -Path $WorkspacesDir -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "Cleaned up Python caches and workspace artifacts."

Write-Host "============================================================"
Write-Host "Uninstallation complete. Antigravity plugin unlinked."
Write-Host "============================================================"

# Optional Repository Purge
if ($Purge) {
    if ([string]::IsNullOrWhiteSpace($ScriptDir) -or $ScriptDir -eq $env:USERPROFILE -or $ScriptDir -match '^[a-zA-Z]:\\?$') {
        Write-Error "Refusing to purge protected root directory: $ScriptDir"
        exit 1
    }
    Write-Host "Purging repository at $ScriptDir..."
    Set-Location $env:USERPROFILE
    Remove-Item -LiteralPath $ScriptDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Repository directory purged completely."
}
