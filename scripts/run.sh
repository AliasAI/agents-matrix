#!/usr/bin/env bash
# Run an agent locally.
# Usage: ./scripts/run.sh [agent_name]
#        cd agents/cast && ../../scripts/run.sh
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"

# Auto-detect agent from $1 or CWD
if [ -n "${1:-}" ]; then
  AGENT="$1"
elif [[ "$(pwd)" == */agents/* ]]; then
  AGENT="$(basename "$(pwd)")"
else
  echo "Usage: $0 <agent_name>"
  echo "  Or run from inside agents/<name>/"
  exit 1
fi

AGENT_DIR="$ROOT/agents/$AGENT"
if [ ! -d "$AGENT_DIR" ]; then
  echo "ERROR: Agent directory not found: $AGENT_DIR"
  exit 1
fi

cd "$AGENT_DIR"
exec uv run python main.py
