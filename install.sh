#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "============================================================"
echo "Installing Thea Engineering Team Framework & Antigravity Plugin"
echo "============================================================"

# 1. Setup Python Virtual Environment
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "[1/3] Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
else
    echo "[1/3] Virtual environment already exists."
fi

echo "Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

# 2. Register Global Antigravity Plugin
echo "[2/3] Linking Antigravity global plugin..."
PLUGIN_TARGET="$HOME/.gemini/config/plugins/thea-engineering-team"
mkdir -p "$HOME/.gemini/config/plugins"
ln -sfn "$SCRIPT_DIR/plugin" "$PLUGIN_TARGET"
echo "Linked: $SCRIPT_DIR/plugin -> $PLUGIN_TARGET"

# 3. Verify
echo "[3/3] Verifying agent definitions..."
"$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/verify_agents.py"

echo "============================================================"
echo "Installation complete. The team is ready across all sessions."
echo "============================================================"
