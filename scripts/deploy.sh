#!/usr/bin/env bash
# Deploy an agent via Docker Compose.
# Usage: ./scripts/deploy.sh [agent_name]
#        cd agents/cast && ../../scripts/deploy.sh
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

# ── Pre-flight checks ──
if [ ! -f .env ]; then
  echo "ERROR: .env file not found in $AGENT_DIR"
  echo "  cp .env.example .env"
  echo "  # Then configure required variables"
  exit 1
fi

# Source .env for local variable access
set -a; source .env; set +a

# Validate LLM key
if [ -z "${AM_LLM_API_KEY:-}" ]; then
  echo "ERROR: AM_LLM_API_KEY is not set in .env"
  exit 1
fi

# Validate default chain/cluster RPC if agent has chain config
if [ -f config/chains.toml ] || [ -f config/clusters.toml ] || [ -f config/envs.toml ]; then
  DEFAULT_CHAIN="${AM_DEFAULT_CHAIN:-}"
  if [ -n "$DEFAULT_CHAIN" ]; then
    RPC_VAR="AM_RPC_$(echo "$DEFAULT_CHAIN" | tr '[:lower:]' '[:upper:]')"
    if [ -z "${!RPC_VAR:-}" ]; then
      echo "ERROR: $RPC_VAR is not set in .env (required for default chain '$DEFAULT_CHAIN')"
      exit 1
    fi
  fi
fi

if [ -z "${AM_WALLET_ADDRESS:-}" ]; then
  echo "NOTICE: AM_WALLET_ADDRESS not set — x402 payment gate disabled"
fi

# Read port from .env or .env.example
PORT="${AM_PORT:-$(grep -m1 '^AM_PORT=' .env.example 2>/dev/null | cut -d= -f2 || echo 9000)}"

# ── Build & Deploy ──
echo "Building and starting $AGENT agent..."
docker compose up -d --build

echo ""
echo "Deployment complete. Service running at http://localhost:$PORT"
echo ""
echo "  Verify:"
echo "    curl http://localhost:$PORT/health"
echo "    curl http://localhost:$PORT/.well-known/agent-card.json"
echo ""
echo "  Logs:"
echo "    docker compose logs -f"
