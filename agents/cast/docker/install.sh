#!/usr/bin/env bash
# Cast agent: install Foundry + clone harness from GitHub.
# Sourced by scripts/docker-gen.sh during Dockerfile generation.
set -euo pipefail

# System deps
apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*

# Install Foundry (cast)
curl -L https://foundry.paradigm.xyz | bash
/root/.foundry/bin/foundryup
export PATH="/root/.foundry/bin:${PATH}"

# Clone cast harness (sparse checkout)
HARNESS_REPO="${HARNESS_REPO:-https://github.com/0xouzm/CLI-Anything.git}"
HARNESS_REF="${HARNESS_REF:-main}"
git clone --depth 1 --branch "$HARNESS_REF" --filter=blob:none --sparse \
  "$HARNESS_REPO" /tmp/cli-anything
cd /tmp/cli-anything && git sparse-checkout set cast/agent-harness
cp -r cast/agent-harness /app/cast-harness
rm -rf /tmp/cli-anything

# Rewrite path dependency for Docker context
sed -i 's|path = "../../../../CLI-Anything/cast/agent-harness"|path = "/app/cast-harness"|' /app/agents/cast/pyproject.toml
