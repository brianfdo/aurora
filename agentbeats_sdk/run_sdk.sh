#!/bin/bash

# Aurora Green Agent - SDK Version Runner
# Uses AppWorld-style APIs (no agentbeats package needed)

set -e

# Use Python 3.11.13 from pyenv
PYTHON="/Users/fern/.pyenv/versions/3.11.13/bin/python"

echo "=========================================="
echo "Aurora Green Agent - SDK Version"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "✓ Python: $PYTHON_VERSION"

# Check required packages
echo "✓ Checking dependencies..."
if ! $PYTHON -c "import flask" 2>/dev/null; then
    echo "⚠️  Missing flask, installing..."
    $PYTHON -m pip install flask flask-cors requests --quiet
fi

echo "✓ All dependencies ready"
echo ""

echo "Starting Aurora Green Agent (SDK Version)..."
echo "  Server:   http://0.0.0.0:8001"
echo "  Launcher: Built-in (/launcher/*)"
echo "  Agent:    Built-in (/a2a/*)"
echo "  APIs:     AppWorld-style (26 curated tracks)"
echo ""

# Default values
AGENT_HOST="${AGENT_HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-8001}"

# Run Aurora green server
# Note: This version uses AppWorld-style APIs directly (no agentbeats package needed)
$PYTHON aurora_green_server.py --host "$AGENT_HOST" --port "$AGENT_PORT"

