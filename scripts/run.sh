#!/bin/bash
# Aurora Green Agent Runner

PYTHON="/Users/fern/.pyenv/versions/3.11.13/bin/python"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

case "$1" in
  green)
    $PYTHON -m agents.green_agent --port 8001
    ;;
  green-a2a)
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    $PYTHON -m agents.green_agent_a2a --port 8001
    ;;
  white)
    $PYTHON -m agents.white_agent --port 9000
    ;;
  white-llm)
    [ -z "$OPENAI_API_KEY" ] && echo "ERROR: OPENAI_API_KEY not set" && exit 1
    $PYTHON -m agents.white_agent_llm --port 9000
    ;;
  kickoff)
    $PYTHON scripts/kickoff.py
    ;;
  *)
    echo "Usage: ./scripts/run.sh [green|green-a2a|white|white-llm|kickoff]"
    ;;
esac
