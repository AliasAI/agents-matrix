#!/usr/bin/env bash
# Health check for a running agent.
# Usage: ./scripts/health.sh [agent_name]
#        cd agents/cast && ../../scripts/health.sh
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

# Read port from .env or .env.example
if [ -f "$AGENT_DIR/.env" ]; then
  PORT="$(grep -m1 '^AM_PORT=' "$AGENT_DIR/.env" | cut -d= -f2)"
fi
PORT="${PORT:-$(grep -m1 '^AM_PORT=' "$AGENT_DIR/.env.example" 2>/dev/null | cut -d= -f2 || echo 9000)}"

BASE="http://localhost:$PORT"

echo "Checking $AGENT agent at $BASE ..."
echo ""

echo "── /health ──"
curl -sf "$BASE/health" && echo "" || echo "FAILED"
echo ""

echo "── /.well-known/agent-card.json ──"
curl -sf "$BASE/.well-known/agent-card.json" | python3 -m json.tool 2>/dev/null || echo "FAILED"
