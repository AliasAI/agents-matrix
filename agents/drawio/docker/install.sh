#!/usr/bin/env bash
# Drawio agent: clone harness from GitHub.
# Sourced by scripts/docker-gen.sh during Dockerfile generation.
set -euo pipefail

# System deps
apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*

# Clone drawio harness (sparse checkout)
HARNESS_REPO="${HARNESS_REPO:-https://github.com/0xouzm/CLI-Anything.git}"
HARNESS_REF="${HARNESS_REF:-main}"
git clone --depth 1 --branch "$HARNESS_REF" --filter=blob:none --sparse \
  "$HARNESS_REPO" /tmp/cli-anything
cd /tmp/cli-anything && git sparse-checkout set drawio/agent-harness
cp -r drawio/agent-harness /app/drawio-harness
rm -rf /tmp/cli-anything

# Rewrite path dependency for Docker context
sed -i 's|path = "../../../../CLI-Anything/drawio/agent-harness"|path = "/app/drawio-harness"|' /app/agents/drawio/pyproject.toml
