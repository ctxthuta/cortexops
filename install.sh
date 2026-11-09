#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "============================================================"
echo "Installing CortexOps Multi-Agent Framework & Antigravity Plugin"
echo "============================================================"

# Virtual environment bootstrap
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
else
    echo "Virtual environment already exists."
fi

echo "Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Antigravity global plugin registration
echo "Linking Antigravity global plugin..."
mkdir -p "$HOME/.gemini/config/plugins"
PLUGIN_TARGET="$HOME/.gemini/config/plugins/cortexops"
LEGACY_TARGET="$HOME/.gemini/config/plugins/thea-engineering-team"
ln -sfn "$SCRIPT_DIR/plugin" "$PLUGIN_TARGET"
ln -sfn "$SCRIPT_DIR/plugin" "$LEGACY_TARGET"
echo "Linked: $SCRIPT_DIR/plugin -> $PLUGIN_TARGET"

# Agent definition verification
echo "Verifying agent definitions..."
"$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/verify_agents.py"

echo "============================================================"
echo "Installation complete. The team is ready across all sessions."
echo "============================================================"
