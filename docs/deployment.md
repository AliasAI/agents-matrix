# Deployment Guide

## Prerequisites

- Docker & Docker Compose v2
- LLM API key (DeepSeek, OpenAI, or any OpenAI-compatible provider)
- Ethereum RPC URL (public or private)
- (Optional) EVM wallet for x402 payment gate

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Required
AM_LLM_API_KEY=sk-...
AM_DEFAULT_RPC_URL=https://eth.drpc.org

# Payment (optional — omit AM_WALLET_ADDRESS to disable x402)
AM_WALLET_ADDRESS=0x...
AM_FACILITATOR_URL=https://x402.org/facilitator
AM_CHAIN_NETWORK=eip155:84532

# Tuning
AM_PORT=9000
AM_LLM_MODEL=deepseek-chat
```

### 2. Deploy

```bash
./scripts/deploy.sh
```

This script:
1. Validates required env vars
2. Copies `cli-anything-cast` into Docker build context
3. Builds the image (installs Foundry cast) and starts the container
4. Cleans up the temporary copy

### 3. Verify

```bash
# Health check
curl http://localhost:9000/health
# Expected: {"status":"ok","service":"cast-transaction-agent"}

# Agent card
curl http://localhost:9000/.well-known/agent-card.json
# Expected: JSON with name, 6 skills, capabilities

# View logs
docker compose logs -f
```

---

## Manual Docker Build

If you prefer not to use the deploy script:

```bash
# Copy path dependency into build context
cp -r ../../CLI-Anything/cast/agent-harness ./cast-harness

# Build
docker compose build

# Start
docker compose up -d

# Cleanup
rm -rf ./cast-harness
```

## Bare Metal (no Docker)

```bash
# Install Foundry cast
curl -L https://foundry.paradigm.xyz | bash && foundryup

# Install dependencies
uv sync --prerelease=allow

# Run
uv run python main.py
```

---

## Verification Flow

### Level 1: Health & Agent Card

```bash
# 1. Health endpoint
curl -s http://localhost:9000/health | python -m json.tool

# 2. Agent card (A2A discovery)
curl -s http://localhost:9000/.well-known/agent-card.json | python -m json.tool
```

Expected: agent card with 6 skills, version "0.1.0".

### Level 2: MCP Server Standalone

Verify the MCP tool layer works independently:

```bash
# List available tools via MCP inspector
uv run mcp dev mcp_server/cast_tools.py
```

Or test directly in Claude Code:

```bash
claude mcp add cast -- uv run python -m mcp_server
```

Then ask Claude to "decode function selector transfer(address,uint256)" — it should call `get_selector`.

### Level 3: A2A Task (No Payment)

Disable x402 by leaving `AM_WALLET_ADDRESS` empty, then send a task:

```bash
curl -s -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": "test-1",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Show me the latest Ethereum block"}]
      }
    }
  }' | python -m json.tool
```

Expected: response containing a task with artifact text showing block details.

### Level 4: A2A + x402 Payment

With `AM_WALLET_ADDRESS` set, the `POST /` endpoint requires x402 payment headers.

```bash
# Without payment — should get 402
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tasks/send","id":"1","params":{"message":{"role":"user","parts":[{"kind":"text","text":"hello"}]}}}'
# Expected: 402

# With x402 client (Python)
uv run python -c "
from a2a.client import A2AClient
# Use x402-enabled HTTP client for real payment flow
# See x402 docs: https://docs.x402.org
"
```

### Level 5: On-Chain Registration

```bash
# Set AM_PRIVATE_KEY, AM_RPC_URL, AM_PINATA_JWT in .env
./scripts/register.sh
```

Expected: ERC-721 minted on Base Sepolia with agent metadata on IPFS.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `CLI error: command not found` | Foundry not installed in container | Check Dockerfile installs Foundry via `foundryup` |
| `AuthenticationError` | Bad API key | Verify `AM_LLM_API_KEY` in `.env` |
| `FileNotFoundError: cli-anything-cast` | MCP subprocess can't find CLI binary | Ensure `cli-anything-cast` is installed: `uv run which cli-anything-cast` |
| `502` from reverse proxy | App not ready yet | Wait for health check to pass; check `docker compose logs` |
| `402` on every request | x402 payment gate active | Either provide payment headers or unset `AM_WALLET_ADDRESS` for testing |
| RPC connection errors | Bad RPC URL | Verify `AM_DEFAULT_RPC_URL` in `.env` with `cast block latest --rpc-url <url>` |

## Architecture

```
Client (A2A)
    |
    v
FastAPI + x402 middleware (payment gate)
    |
    v
CastExecutor (A2A AgentExecutor)
    |  spawns stdio subprocess
    v
MCP Server (8 Cast tools)
    |  subprocess calls
    v
cli-anything-cast CLI
    |
    v
Foundry cast (tx, receipt, run, 4byte-decode, sig, logs, call, block)
```

The LLM agent loop sits between the executor and MCP server, using tool-use to understand intent and chain multiple tool calls as needed.
