# Agents Matrix

A quick-launch boilerplate for building **paid AI agents** with [A2A protocol](https://github.com/google/A2A) + [x402 payment](https://www.x402.org/) + [ERC-8004 registration](https://github.com/agent0-labs/agent0-sdk).

Write 4–5 files, get a paid A2A agent. The tool backend is pluggable — CLI-Anything harness, direct CLI subprocess, REST API, Python library — anything that produces structured output works.

```
Backend Type                  Agent Example
──────────────────────        ──────────────────────────────────────
CLI-Anything harness     →    agents/cast/      EVM tx analysis        (Foundry cast)
CLI-Anything harness     →    agents/drawio/    Diagram creation       (draw.io)
Direct CLI subprocess    →    agents/solana/    Solana blockchain      (solana CLI)
Direct CLI subprocess    →    agents/sui/       Sui blockchain         (sui client)
```

## Architecture

```
agents-matrix/
  scripts/                      ← shared CLI scripts (auto-detect agent from CWD or $1)
    run.sh                        run agent locally
    deploy.sh                     deploy via Docker Compose
    register.sh                   ERC-8004 on-chain registration
    dev.sh                        launch MCP inspector
    health.sh                     health check running agent
    docker-gen.sh                 generate Dockerfile from template
    new-agent.sh                  scaffold a new agent
  framework/                    ← agents-core: shared package for all agents
    src/agents_core/
      app.py                      create_app() + run_agent() entry point
      executor.py                 MCPAgentExecutor (A2A → MCP bridge)
      loop.py                     LLM agentic loop (OpenAI-compatible)
      payment.py                  x402 middleware helpers
      registration.py             ERC-8004 on-chain registration
      settings.py                 Settings, ChainRegistry, Pricing
  agents/
    cast/                       ← CLI-Anything harness backend
    drawio/                     ← CLI-Anything harness backend
    solana/                     ← Direct CLI backend (solana binary)
    sui/                        ← Direct CLI backend (sui binary)
  pyproject.toml                ← uv workspace
```

Each agent only needs 4–5 tool-specific files. The framework handles everything else: A2A server, x402 payment gate, LLM tool-use loop, MCP subprocess management, and on-chain registration.

## Request Flow

```
Client (A2A JSON-RPC)
    │
    ▼
FastAPI + x402 middleware ── payment verification
    │
    ▼
MCPAgentExecutor ── spawns MCP subprocess
    │
    ▼
LLM Agent Loop ── tool-use with OpenAI-compatible API
    │
    ▼
MCP Server ── @mcp.tool() functions
    │
    ▼
Tool Backend ── CLI harness / direct CLI / API / library
```

## Quick Start

### Docker (recommended)

```bash
cp agents/cast/.env.example agents/cast/.env
# Edit .env: set AM_LLM_API_KEY and at least one AM_RPC_* URL

./scripts/deploy.sh cast
```

No need to install Foundry, Python, or uv on the host — the Docker image handles everything.

### Local Development

```bash
# Prerequisites: Python 3.12+, uv
# Agent-specific: Foundry cast, solana CLI, sui CLI, etc.

# Install workspace
uv sync --prerelease=allow --all-packages

# Configure
cp agents/cast/.env.example agents/cast/.env
# Edit .env

# Run
./scripts/run.sh cast
```

### Verify

```bash
# Health check
curl http://localhost:9000/health
# → {"status":"ok","service":"cast-transaction-agent"}

# A2A agent card
curl http://localhost:9000/.well-known/agent-card.json

# Send a task (with x402 payment disabled)
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": "test-1",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Decode tx 0xabc123... on ethereum"}]
      }
    }
  }'
```

## Agents

| Agent | Port | Backend | Description |
|-------|------|---------|-------------|
| [Cast](agents/cast/) | 9000 | CLI-Anything harness | Multi-chain EVM transaction analysis via Foundry cast |
| [Draw.io](agents/drawio/) | 9001 | CLI-Anything harness | Diagram creation, editing, and export via draw.io |
| [Solana](agents/solana/) | 9002 | Direct CLI | Solana blockchain queries via solana CLI |
| [Sui](agents/sui/) | 9003 | Direct CLI | Sui blockchain queries via sui client CLI |

## Adding a New Agent

### Scaffolding (recommended)

```bash
./scripts/new-agent.sh weather --port 9010
# Then edit agent_config.py and mcp_tools.py
uv sync --prerelease=allow --all-packages
```

### Manual

Create `agents/<name>/` with:

| File | Purpose |
|------|---------|
| `agent_config.py` | SYSTEM_PROMPT, SKILLS list, `build_agent_card()` |
| `mcp_tools.py` | `@mcp.tool()` functions calling your backend (CLI, API, library, etc.) |
| `mcp_entry.py` | `from mcp_tools import mcp; mcp.run()` |
| `main.py` | Thin entry point using `agents_core.app.run_agent()` |
| `pyproject.toml` | Depends on `agents-core` (+ optional backend deps) |
| `config/` | pricing.toml (required), chains.toml (if multi-chain/env) |
| `docker/install.sh` | (optional) Tool installation steps for Dockerfile |

Then run `uv sync --prerelease=allow --all-packages` from workspace root.

The backend can be anything that returns structured data:
- **CLI-Anything harness**: `subprocess.run(["cli-anything-<tool>", "--json", ...])` — see `agents/cast/`
- **Direct CLI**: `subprocess.run(["solana", "--output", "json", ...])` — see `agents/solana/`
- **REST API**: `httpx.get("https://api.example.com/...")` — just return JSON
- **Python library**: Direct function calls — no subprocess needed

## Environment Variables

All variables use the `AM_` prefix. See each agent's `.env.example` for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `AM_LLM_API_KEY` | Yes | LLM API key (DeepSeek, OpenAI, etc.) |
| `AM_DEFAULT_CHAIN` | Per agent | Default chain/cluster slug |
| `AM_RPC_*` | Per chain | RPC URL per chain (e.g. `AM_RPC_ETHEREUM`) |
| `AM_WALLET_ADDRESS` | No | EVM wallet — enables x402 payment gate |
| `AM_PRIVATE_KEY` | No | For ERC-8004 on-chain registration |

## Key Dependencies

| Package | Purpose |
|---------|---------|
| [a2a-sdk](https://github.com/google/A2A) | Google A2A protocol (agent-to-agent) |
| [x402](https://github.com/coinbase/x402) | Coinbase payment middleware (USDC) |
| [agent0-sdk](https://github.com/agent0-labs/agent0-sdk) | ERC-8004 on-chain agent registration |
| [mcp](https://modelcontextprotocol.io/) | Model Context Protocol tool server |
| [openai](https://github.com/openai/openai-python) | LLM agent loop (any OpenAI-compatible API) |

## License

MIT
