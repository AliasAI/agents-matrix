#!/usr/bin/env bash
# Register an agent on-chain via ERC-8004.
# Usage: ./scripts/register.sh [agent_name]
#        cd agents/cast && ../../scripts/register.sh
#
# On dev machines (CLI-Anything repo present at ../../CLI-Anything), runs via
# local uv. On production servers where that path is absent, automatically
# falls back to exec-ing the running Docker container for that agent.
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

# Write registration script to a temp file (avoids shell quoting issues)
TMP_PY=$(mktemp /tmp/register_XXXXXX.py)
trap 'rm -f "$TMP_PY"' EXIT
cat > "$TMP_PY" << 'PYEOF'
import os, sys
sys.path.insert(0, ".")
from agents_core.settings import get_settings
from agents_core.registration import register
from agent_config import build_agent_card
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
settings = get_settings()
card = build_agent_card(settings)
# Pull optional agent-specific registration extras (MCP tools, OASF overrides)
try:
    from agent_config import MCP_TOOLS
except ImportError:
    MCP_TOOLS = None
try:
    from agent_config import OASF_SKILLS, OASF_DOMAINS
except ImportError:
    OASF_SKILLS = OASF_DOMAINS = None
# AM_AGENT_ID in .env triggers an update instead of a new mint
agent_id = os.environ.get("AM_AGENT_ID") or None
if agent_id:
    logging.getLogger(__name__).info("Updating existing agent %s", agent_id)
else:
    logging.getLogger(__name__).info("No AM_AGENT_ID set — minting new agent")
register(
    settings,
    name=card.name,
    description=card.description,
    mcp_tools=MCP_TOOLS,
    skills=OASF_SKILLS,
    domains=OASF_DOMAINS,
    agent_id=agent_id,
)
PYEOF

# On dev machines the CLI-Anything harness repo lives at ../../CLI-Anything
# relative to the workspace root.  On production servers it is absent, and
# the uv workspace lock will fail to resolve cast/drawio harness paths.
CLI_ANYTHING="$ROOT/../CLI-Anything"

if [ -d "$CLI_ANYTHING" ]; then
  # Local dev: harness present, run directly via uv
  cd "$AGENT_DIR"
  uv run python "$TMP_PY"
else
  # Production: find the running Docker container and exec inside it.
  # All required env vars (AM_PRIVATE_KEY, AM_RPC_URL, AM_PINATA_JWT, …)
  # are already loaded from the agent's .env via docker-compose env_file.
  CONTAINER=$(docker ps --filter "name=${AGENT}-agent" --format "{{.Names}}" | head -1)
  if [ -z "$CONTAINER" ]; then
    echo "ERROR: No running Docker container found for agent '$AGENT'."
    echo "  Start the agent first:  ./scripts/deploy.sh $AGENT"
    exit 1
  fi
  echo "INFO: CLI-Anything not present locally — running inside container: $CONTAINER"
  # Load the agent's .env so we can inject up-to-date values (the running
  # container may have been started with an older .env snapshot).
  set -a; [ -f "$AGENT_DIR/.env" ] && source "$AGENT_DIR/.env"; set +a
  docker cp "$TMP_PY" "$CONTAINER:/tmp/register_agent.py"
  docker exec -w "/app/agents/$AGENT" \
    -e AM_PRIVATE_KEY="${AM_PRIVATE_KEY:-}" \
    -e AM_RPC_URL="${AM_RPC_URL:-}" \
    -e AM_CHAIN_NETWORK="${AM_CHAIN_NETWORK:-}" \
    -e AM_CHAIN_ID="${AM_CHAIN_ID:-}" \
    -e AM_WALLET_ADDRESS="${AM_WALLET_ADDRESS:-}" \
    -e AM_BASE_URL="${AM_BASE_URL:-}" \
    -e AM_PINATA_JWT="${AM_PINATA_JWT:-}" \
    -e AM_AGENT_ID="${AM_AGENT_ID:-}" \
    "$CONTAINER" uv run python /tmp/register_agent.py
  docker exec "$CONTAINER" rm -f /tmp/register_agent.py
fi
