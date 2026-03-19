#!/usr/bin/env bash
# Scaffold a new agent with all boilerplate.
# Usage: ./scripts/new-agent.sh <name> [--port PORT]
#
# Example: ./scripts/new-agent.sh weather --port 9010
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"

# ── Parse args ──
if [ -z "${1:-}" ]; then
  echo "Usage: $0 <name> [--port PORT]"
  echo "  Example: $0 weather --port 9010"
  exit 1
fi

NAME="$1"; shift
PORT=9000

while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

AGENT_DIR="$ROOT/agents/$NAME"
PKG_NAME="${NAME}-agent"
# Title case for display
DISPLAY_NAME="$(echo "$NAME" | sed 's/.*/\u&/') Agent"
LOG_NAME="${NAME}-agent"

if [ -d "$AGENT_DIR" ]; then
  echo "ERROR: Agent directory already exists: $AGENT_DIR"
  exit 1
fi

echo "Scaffolding agent: $NAME (port $PORT)"

# ── Create directories ──
mkdir -p "$AGENT_DIR"/{config,scripts}

# ── pyproject.toml ──
cat > "$AGENT_DIR/pyproject.toml" <<EOF
[project]
name = "$PKG_NAME"
version = "0.1.0"
description = "$DISPLAY_NAME — TODO: add description"
requires-python = ">=3.12"
dependencies = [
    "agents-core",
]

[tool.uv]
prerelease = "allow"

[tool.uv.sources]
agents-core = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["agent_config", "mcp_tools", "mcp_entry"]
EOF

# ── agent_config.py ──
cat > "$AGENT_DIR/agent_config.py" <<'PYEOF'
"""Agent configuration — system prompt, skills, and AgentCard builder."""

from __future__ import annotations

from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from agents_core.settings import Settings

SYSTEM_PROMPT = """\
You are a helpful agent. TODO: describe your agent's purpose and capabilities.
"""

SKILLS: list[AgentSkill] = [
    # TODO: define skills
    # AgentSkill(
    #     id="example",
    #     name="Example Skill",
    #     description="TODO: describe skill",
    #     tags=["example"],
    # ),
]


def build_agent_card(settings: Settings) -> AgentCard:
    return AgentCard(
        name="TODO Agent Name",
        description="TODO: describe this agent",
        url=settings.base_url,
        version="0.1.0",
        capabilities=AgentCapabilities(streaming=False),
        skills=SKILLS,
    )
PYEOF

# ── mcp_tools.py ──
cat > "$AGENT_DIR/mcp_tools.py" <<'PYEOF'
"""MCP tool definitions."""

from __future__ import annotations

import json
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TODO-Agent")


def _run_cli(*args: str) -> dict | list | str:
    """Run a CLI command and return parsed JSON output."""
    cmd = ["echo", "TODO: replace with actual CLI command", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


# TODO: define @mcp.tool() functions
# @mcp.tool()
# def example_tool(param: str) -> str:
#     """TODO: describe tool."""
#     return _run_cli("subcommand", param)
PYEOF

# ── mcp_entry.py ──
cat > "$AGENT_DIR/mcp_entry.py" <<'PYEOF'
"""Entry point: python -m mcp_entry (stdio mode)."""

from mcp_tools import mcp

if __name__ == "__main__":
    mcp.run()
PYEOF

# ── main.py ──
cat > "$AGENT_DIR/main.py" <<PYEOF
"""$DISPLAY_NAME A2A Agent Service — entry point."""

from pathlib import Path

from agents_core.app import run_agent
from agents_core.settings import get_settings
from agent_config import SYSTEM_PROMPT, build_agent_card

if __name__ == "__main__":
    run_agent(
        agent_card=build_agent_card(get_settings()),
        mcp_module="mcp_entry",
        system_prompt=SYSTEM_PROMPT,
        log_name="$LOG_NAME",
        pricing_path=Path(__file__).parent / "config" / "pricing.toml",
    )
PYEOF

# ── config/pricing.toml ──
cat > "$AGENT_DIR/config/pricing.toml" <<'EOF'
# Per-skill USDC pricing for x402 payment gate.
# Format: "$<amount>" — parsed by x402 PaymentOption.

default = "$0.01"

[skills]
# TODO: add per-skill pricing
# example = "$0.02"
EOF

# ── .env.example ──
cat > "$AGENT_DIR/.env.example" <<EOF
# ── Required ──
AM_LLM_API_KEY=sk-...

# ── LLM (defaults to DeepSeek) ──
AM_LLM_BASE_URL=https://api.deepseek.com
AM_LLM_MODEL=deepseek-chat

# ── Server ──
AM_HOST=0.0.0.0
AM_PORT=$PORT
AM_BASE_URL=http://localhost:$PORT

# ── x402 Payment (optional) ──
AM_WALLET_ADDRESS=
AM_FACILITATOR_URL=https://x402.org/facilitator
AM_CHAIN_NETWORK=eip155:84532

# ── ERC-8004 Registration (optional) ──
AM_PRIVATE_KEY=
AM_CHAIN_ID=84532
AM_RPC_URL=
AM_PINATA_JWT=
EOF

# ── scripts/ (thin wrappers) ──
for SCRIPT in run deploy register; do
  cat > "$AGENT_DIR/scripts/$SCRIPT.sh" <<'WRAPPER'
#!/usr/bin/env bash
exec "$(dirname "$0")/../../../scripts/SCRIPT_NAME.sh" "$@"
WRAPPER
  sed -i '' "s/SCRIPT_NAME/$SCRIPT/" "$AGENT_DIR/scripts/$SCRIPT.sh"
  chmod +x "$AGENT_DIR/scripts/$SCRIPT.sh"
done

echo ""
echo "Agent scaffolded at: agents/$NAME/"
echo ""
echo "  Files created:"
echo "    pyproject.toml      — package config (depends on agents-core)"
echo "    agent_config.py     — system prompt, skills, AgentCard"
echo "    mcp_tools.py        — MCP tool definitions (TODO)"
echo "    mcp_entry.py        — MCP stdio entry"
echo "    main.py             — service entry point"
echo "    config/pricing.toml — per-skill pricing"
echo "    .env.example        — environment template"
echo "    scripts/             — run, deploy, register wrappers"
echo ""
echo "  Next steps:"
echo "    1. Edit agent_config.py — set name, description, skills"
echo "    2. Edit mcp_tools.py — implement your tools"
echo "    3. uv sync --prerelease=allow --all-packages"
echo "    4. cp agents/$NAME/.env.example agents/$NAME/.env && edit .env"
echo "    5. ./scripts/run.sh $NAME"
