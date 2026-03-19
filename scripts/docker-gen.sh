#!/usr/bin/env bash
# Generate a Dockerfile for an agent from shared template + per-agent install.sh.
# Usage: ./scripts/docker-gen.sh <agent_name> [--write]
#
# Without --write, prints Dockerfile to stdout.
# With --write, writes to agents/<name>/Dockerfile.
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <agent_name> [--write]"
  exit 1
fi

AGENT="$1"
WRITE="${2:-}"
AGENT_DIR="$ROOT/agents/$AGENT"

if [ ! -d "$AGENT_DIR" ]; then
  echo "ERROR: Agent directory not found: $AGENT_DIR"
  exit 1
fi

# Read package name from pyproject.toml
PKG_NAME="$(grep -m1 '^name' "$AGENT_DIR/pyproject.toml" | sed 's/.*"\(.*\)".*/\1/')"
PORT="$(grep -m1 '^AM_PORT=' "$AGENT_DIR/.env.example" 2>/dev/null | cut -d= -f2 || echo 9000)"

# Check for custom install script
INSTALL_SH="$AGENT_DIR/docker/install.sh"
HAS_INSTALL=false
if [ -f "$INSTALL_SH" ]; then
  HAS_INSTALL=true
fi

# Detect ENV PATH additions from install.sh
ENV_LINES=""
if $HAS_INSTALL; then
  # Extract export PATH lines and convert to Docker ENV
  while IFS= read -r line; do
    # Match: export PATH="...:${PATH}"
    path_val="$(echo "$line" | sed -n 's/^export PATH="\(.*\):\${PATH}"/\1/p')"
    if [ -n "$path_val" ]; then
      ENV_LINES="${ENV_LINES}ENV PATH=\"${path_val}:\${PATH}\"\n"
    fi
  done < "$INSTALL_SH"
fi

# ── Generate Dockerfile ──
generate() {
cat <<'HEADER'
FROM python:3.12-slim

HEADER

# Install step (if agent has docker/install.sh)
if $HAS_INSTALL; then
  echo "# Agent-specific tool installation"
  echo "COPY agents/$AGENT/docker/install.sh /tmp/install-tools.sh"
  echo "RUN chmod +x /tmp/install-tools.sh && /tmp/install-tools.sh && rm /tmp/install-tools.sh"
  echo ""
  # Add PATH env if detected
  if [ -n "$ENV_LINES" ]; then
    echo -e "$ENV_LINES"
  fi
fi

cat <<EOF
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root + framework + this agent
# NOTE: build context is agents-matrix/ root (set in docker-compose.yml)
COPY pyproject.toml /app/pyproject.toml
COPY framework /app/framework
COPY agents/$AGENT /app/agents/$AGENT

# Install dependencies
RUN cd /app && uv lock --prerelease=allow && uv sync --prerelease=allow --package $PKG_NAME

WORKDIR /app/agents/$AGENT

EXPOSE $PORT

CMD ["uv", "run", "--package", "$PKG_NAME", "python", "main.py"]
EOF
}

if [ "$WRITE" = "--write" ]; then
  generate > "$AGENT_DIR/Dockerfile"
  echo "Wrote $AGENT_DIR/Dockerfile"
else
  generate
fi
