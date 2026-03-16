#!/usr/bin/env bash
# Deploy agents-matrix (Cast Transaction Agent) via Docker Compose.
# Usage: ./scripts/deploy.sh [--build]
set -euo pipefail
cd "$(dirname "$0")/.."

# ── Pre-flight checks ──
if [ ! -f .env ]; then
  echo "ERROR: .env file not found. Copy .env.example and fill in values:"
  echo "  cp .env.example .env"
  exit 1
fi

# Source .env for local variable access
set -a; source .env; set +a

# Validate required vars
for var in AM_LLM_API_KEY AM_DEFAULT_RPC_URL; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set in .env"
    exit 1
  fi
done

if [ -z "${AM_WALLET_ADDRESS:-}" ]; then
  echo "NOTICE: AM_WALLET_ADDRESS not set — x402 payment gate disabled"
fi

# ── Copy cli-anything-cast for Docker build context ──
HARNESS_SRC="../../CLI-Anything/cast/agent-harness"
HARNESS_DST="./cast-harness"
if [ -d "$HARNESS_SRC" ]; then
  echo "Copying cli-anything-cast into build context..."
  rm -rf "$HARNESS_DST"
  cp -r "$HARNESS_SRC" "$HARNESS_DST"
else
  echo "ERROR: cli-anything-cast not found at $HARNESS_SRC"
  exit 1
fi

# ── Build & Deploy ──
echo "Building and starting services..."
docker compose up -d --build

# ── Cleanup build context copy ──
rm -rf "$HARNESS_DST"

echo ""
echo "Deployment complete. Service running at http://localhost:${AM_PORT:-9000}"
echo "  Health:     curl http://localhost:${AM_PORT:-9000}/health"
echo "  Agent card: curl http://localhost:${AM_PORT:-9000}/.well-known/agent-card.json"
echo "  Logs:       docker compose logs -f"
