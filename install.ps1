# Cross-Platform Windows PowerShell Installer for Thea Senior Engineering Team
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "============================================================"
Write-Host "Installing Thea Engineering Team Framework on Windows"
Write-Host "============================================================"

# 1. Virtual Environment Setup
$VenvDir = Join-Path $ScriptDir ".venv"
$PythonExec = "python"
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    if (Get-Command "python3" -ErrorAction SilentlyContinue) {
        $PythonExec = "python3"
    } else {
        Write-Error "Python 3 is required but not found in PATH."
    }
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "[1/3] Creating Python virtual environment..."
    & $PythonExec -m venv $VenvDir
} else {
    Write-Host "[1/3] Virtual environment already exists."
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

Write-Host "Installing dependencies..."
& $VenvPip install --quiet --upgrade pip
& $VenvPip install --quiet -r (Join-Path $ScriptDir "requirements.txt")

# 2. Link Antigravity Global Plugin
Write-Host "[2/3] Linking Antigravity global plugin..."
$PluginSource = Join-Path $ScriptDir "plugin"
$PluginsRoot = Join-Path $env:USERPROFILE ".gemini\config\plugins"
$PluginTarget = Join-Path $PluginsRoot "thea-engineering-team"

if (-not (Test-Path $PluginsRoot)) {
    New-Item -ItemType Directory -Path $PluginsRoot -Force | Out-Null
}

if (Test-Path $PluginTarget) {
    cmd /c "rmdir `"$PluginTarget`"" 2>$null
    if (Test-Path $PluginTarget) {
        Remove-Item -Path $PluginTarget -Recurse -Force
    }
}

# Create Directory Junction (works without administrator privileges on Windows)
cmd /c "mklink /J `"$PluginTarget`" `"$PluginSource`"" | Out-Null
Write-Host "Linked: $PluginSource -> $PluginTarget"

# 3. Verify Subagents
Write-Host "[3/3] Verifying agent definitions..."
& $VenvPython (Join-Path $ScriptDir "verify_agents.py")

Write-Host "============================================================"
Write-Host "Installation complete. The team is ready across Windows sessions."
Write-Host "============================================================"
