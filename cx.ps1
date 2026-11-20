# CortexOps Multi-Agent Framework CLI for Windows PowerShell
param (
    [Parameter(Position=0)]
    [string]$Command = "status",
    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $VenvPython = "python"
    } else {
        $VenvPython = "python3"
    }
}

switch ($Command.ToLower()) {
    "dashboard" {
        & $VenvPython (Join-Path $ScriptDir "src\dashboard.py") @RemainingArgs
    }
    "status" {
        & $VenvPython (Join-Path $ScriptDir "src\dashboard.py") @RemainingArgs
    }
    "watch" {
        & $VenvPython (Join-Path $ScriptDir "src\dashboard.py") "--watch" @RemainingArgs
    }
    "verify" {
        & $VenvPython (Join-Path $ScriptDir "verify_agents.py")
    }
    "install" {
        & (Join-Path $ScriptDir "install.ps1")
    }
    "uninstall" {
        & (Join-Path $ScriptDir "uninstall.ps1") @RemainingArgs
    }
    "run" {
        if (-not $RemainingArgs -or $RemainingArgs.Count -eq 0) {
            Write-Error "Goal argument required. Usage: .\cx.ps1 run `"<prompt>`""
            exit 1
        }
        & $VenvPython (Join-Path $ScriptDir "src\main.py") @RemainingArgs
    }
    Default {
        Write-Host "CortexOps Multi-Agent Framework CLI"
        Write-Host ""
        Write-Host "Usage: .\cx.ps1 [command]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  dashboard, status   Display the live operational & token telemetry dashboard"
        Write-Host "  watch               Continuously monitor the dashboard (auto-refresh)"
        Write-Host "  verify              Verify all 12 subagent definitions and plugin link"
        Write-Host "  install             Run the 1-click Windows installer and plugin junction"
        Write-Host "  uninstall           Unlink Antigravity plugin and remove virtual environment"
        Write-Host "  run `"<prompt>`"     Dispatch a multi-agent engineering task via Python SDK"
    }
}
