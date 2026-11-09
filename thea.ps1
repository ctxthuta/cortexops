# Compatibility wrapper forwarding to cx.ps1
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $ScriptDir "cx.ps1") @args
