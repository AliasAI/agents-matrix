#!/usr/bin/env bash
# Solana agent: install Solana CLI.
# Sourced by scripts/docker-gen.sh during Dockerfile generation.
set -euo pipefail

# System deps
apt-get update && apt-get install -y --no-install-recommends curl bzip2 && rm -rf /var/lib/apt/lists/*

# Install Solana CLI
SOLANA_VERSION="${SOLANA_VERSION:-v2.2.12}"
curl -sSfL "https://release.anza.xyz/${SOLANA_VERSION}/install" | sh
export PATH="/root/.local/share/solana/install/active_release/bin:${PATH}"
