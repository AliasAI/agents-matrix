# Agents Matrix — Cast Transaction Agent

Paid Agent-as-a-Service platform — Ethereum transaction analysis via A2A protocol + x402 payment.

## Architecture

```
Client (A2A) → FastAPI + x402 middleware → CastExecutor → MCP Server → cli-anything-cast → Foundry cast
```

- **Entry point**: `main.py` → `server/app.py` app factory
- **Config**: `config/settings.py` (pydantic-settings, `AM_` env prefix), `config/pricing.toml`
- **A2A executor**: `executor/cast_executor.py` — handles A2A task lifecycle
- **Agent loop**: `agent/loop.py` — LLM tool-use loop (OpenAI-compatible API) between executor and MCP
- **MCP tools**: `mcp_server/cast_tools.py` — 8 Cast tools exposed via MCP
- **Payment**: `server/payment.py` — x402 ASGI middleware on `POST /`
- **Agent card**: `server/agent_card.py` — A2A discovery endpoint (6 skills)
- **Registration**: `register/register_agent.py` — ERC-8004 on-chain registration

## Key Dependencies

- `a2a-sdk[http-server]` — Google A2A protocol
- `x402[fastapi,httpx,evm]` — Coinbase payment middleware
- `agent0-sdk` — ERC-8004 on-chain registration
- `openai` — LLM agent loop (DeepSeek / any OpenAI-compatible API)
- `mcp[cli]` — MCP tool server
- `cli-anything-cast` — path dependency from `../../CLI-Anything/cast/agent-harness`

## MCP Tools (8)

| Tool | Cast Command | Output | RPC |
|------|-------------|--------|-----|
| `get_transaction` | `cast tx --json` | JSON | Yes |
| `get_receipt` | `cast receipt --json` | JSON | Yes |
| `trace_transaction` | `cast run` | Text | Yes |
| `decode_calldata` | `cast 4byte-decode` | Text | No |
| `get_selector` | `cast sig` | Text | No |
| `query_logs` | `cast logs --json` | JSON | Yes |
| `call_contract` | `cast call` | Text | Yes |
| `get_block` | `cast block --json` | JSON | Yes |

## Commands

```bash
# Dev: run locally
uv run python main.py

# Deploy: Docker
./scripts/deploy.sh

# Register on-chain
./scripts/register.sh

# Test MCP server standalone
uv run mcp dev mcp_server/cast_tools.py
```

## Environment

- Python 3.12+, managed by `uv`
- `uv sync --prerelease=allow` required (agent0-sdk → ipfshttpclient)
- All env vars use `AM_` prefix — see `.env.example`
- Requires Foundry `cast` on PATH
- Never commit `.env` — it contains secrets (API keys, private keys)

## Conventions

- Keep files under 300 lines
- Use strong types (pydantic models, TypedDicts), avoid unstructured dicts
- Logs output to `logs/` directory
