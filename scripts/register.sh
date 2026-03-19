#!/usr/bin/env bash
# Register an agent on-chain via ERC-8004.
# Usage: ./scripts/register.sh [agent_name]
#        cd agents/cast && ../../scripts/register.sh
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
uv run python -c "
from agents_core.settings import get_settings
from agents_core.registration import register
from agent_config import build_agent_card
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s  %(message)s')
settings = get_settings()
card = build_agent_card(settings)
register(settings, name=card.name, description=card.description)
"
