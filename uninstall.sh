#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE=false
PURGE=false

for arg in "$@"; do
    case "$arg" in
        -y|--yes|--force)
            FORCE=true
            ;;
        --purge)
            PURGE=true
            ;;
    esac
done

echo "============================================================"
echo "Uninstalling CortexOps Multi-Agent Framework"
echo "============================================================"

if [ "$FORCE" = false ]; then
    read -p "Are you sure you want to uninstall and unregister all subagents? [y/N]: " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Uninstallation aborted."
        exit 0
    fi
fi

# Plugin removal
for p in "cortexops" "thea-engineering-team"; do
    PLUGIN_PATH="$HOME/.gemini/config/plugins/$p"
    if [ -L "$PLUGIN_PATH" ] || [ -d "$PLUGIN_PATH" ]; then
        echo "Removing Antigravity global plugin link ($p)..."
        rm -rf "$PLUGIN_PATH"
        echo "Removed: $PLUGIN_PATH"
    fi
done

# Virtual environment cleanup
VENV_PATH="$SCRIPT_DIR/.venv"
if [ -d "$VENV_PATH" ]; then
    echo "Removing Python virtual environment..."
    rm -rf "$VENV_PATH"
    echo "Removed: $VENV_PATH"
else
    echo "Virtual environment not present."
fi

# Artifact and cache cleanup
echo "Cleaning up Python caches and temporary files..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf "$SCRIPT_DIR/workspaces/"* 2>/dev/null || true
echo "Cleaned up Python caches and workspace artifacts."

echo "============================================================"
echo "Uninstallation complete. Antigravity plugin unlinked."
echo "============================================================"

# Optional Repository Purge
if [ "$PURGE" = true ]; then
    echo "Purging repository at $SCRIPT_DIR..."
    cd "$HOME"
    rm -rf "$SCRIPT_DIR"
    echo "Repository directory purged completely."
fi
