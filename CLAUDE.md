# Agents Matrix

Quick-launch boilerplate for paid AI agents — A2A protocol + x402 payment + ERC-8004 registration. Tool backend is pluggable: CLI-Anything harness, direct CLI subprocess, REST API, Python library.

## Monorepo Structure

```
agents-matrix/
  scripts/                      ← shared CLI scripts (auto-detect agent from CWD or $1)
    run.sh                      ← run agent locally
    deploy.sh                   ← deploy via Docker Compose
    register.sh                 ← ERC-8004 on-chain registration
    dev.sh                      ← launch MCP inspector
    health.sh                   ← health check running agent
    docker-gen.sh               ← generate Dockerfile from template
    new-agent.sh                ← scaffold a new agent
  framework/                    ← agents-core shared package
    src/agents_core/
      settings.py               ← Settings, ChainRegistry, Pricing, ChainInfo
      executor.py               ← Generic MCPAgentExecutor
      loop.py                   ← run_agent_loop() (system_prompt as param)
      app.py                    ← create_app() + run_agent() entry point
      payment.py                ← x402 middleware helpers
      registration.py           ← ERC-8004 helper (generic)
  agents/
    cast/                       ← Cast Transaction Agent (CLI-Anything harness)
    drawio/                     ← Draw.io Diagram Agent (CLI-Anything harness)
    solana/                     ← Solana Agent (direct CLI)
    sui/                        ← Sui Agent (direct CLI)
  pyproject.toml                ← uv workspace
```

## Backend Patterns

### CLI-Anything Harness (cast, drawio)
```python
def _run_cli(*args: str) -> str | dict | list:
    cmd = ["cli-anything-<tool>", "--json", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return json.loads(result.stdout)
```

### Direct CLI Subprocess (solana, sui)
```python
BIN = os.environ.get("AM_<TOOL>_BIN", shutil.which("<tool>") or "<tool>")
def _run_cli(*args: str) -> dict | list | str:
    cmd = [BIN, *args, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return json.loads(result.stdout)
```

## Adding a New Agent

```bash
./scripts/new-agent.sh <name> --port <PORT>
# Then edit agent_config.py and mcp_tools.py
```

Or manually create `agents/<name>/` with:
- `agent_config.py` — SYSTEM_PROMPT, SKILLS, build_agent_card()
- `mcp_tools.py` — @mcp.tool() functions calling any backend
- `mcp_entry.py` — `from mcp_tools import mcp; mcp.run()`
- `main.py` — thin entry using `agents_core.app.run_agent()`
- `pyproject.toml` — depends on `agents-core` (+ optional backend deps)
- `config/` — pricing.toml, chains.toml (if multi-chain/env)
- `docker/install.sh` — (optional) tool installation for Dockerfile

## Multi-Chain/Cluster/Env Support

All multi-environment tools use `ChainRegistry` from agents-core with same `[chains.*]` schema in config TOML. RPC URLs from `AM_RPC_{SLUG}` env vars. Passed as CLI flag to backend.

## Key Dependencies

- `a2a-sdk[http-server]` — Google A2A protocol
- `x402[fastapi,httpx,evm]` — Coinbase payment middleware
- `agent0-sdk` — ERC-8004 on-chain registration
- `openai` — LLM agent loop (DeepSeek / any OpenAI-compatible API)
- `mcp[cli]` — MCP tool server

## Commands

```bash
# Install workspace
uv sync --prerelease=allow --all-packages

# Root-level scripts (auto-detect agent from CWD or accept $1)
./scripts/run.sh cast              # run agent locally
./scripts/deploy.sh solana         # deploy via Docker
./scripts/register.sh cast         # ERC-8004 on-chain registration
./scripts/dev.sh drawio            # launch MCP inspector
./scripts/health.sh cast           # health check running agent
./scripts/docker-gen.sh sui        # generate Dockerfile to stdout
./scripts/new-agent.sh weather --port 9010  # scaffold new agent

# Per-agent scripts still work (thin wrappers to root scripts)
cd agents/cast && ./scripts/run.sh
cd agents/cast && ./scripts/deploy.sh
```

## Environment

- Python 3.12+, managed by `uv` (workspace mode)
- `uv sync --prerelease=allow --all-packages` required
- All env vars use `AM_` prefix — see each agent's `.env.example`
- Never commit `.env` — it contains secrets

## Production Server Notes

### `uv run` fails with "Distribution not found: CLI-Anything/..."

The workspace includes cast and drawio, whose `pyproject.toml` reference local
editable paths (`../../../../CLI-Anything/cast/agent-harness`) that only exist
on dev machines. On the production server these paths are absent, so `uv run`
fails for **any** workspace member — even agents that have no harness deps.

**`register.sh` handles this automatically**: if `../../CLI-Anything` is not
found it detects the running Docker container for that agent and execs inside
it (injecting env vars from the agent's local `.env`). No manual steps needed:

```bash
./scripts/register.sh agentscan   # works on both dev and prod
```

Docker builds for cast/drawio are not affected — their Dockerfiles patch the
harness path and call `uv lock` independently before `uv sync`.

### nginx — agent card returns 403

Each agent must have a `location ^~ /<name>/` block in `/etc/nginx/sites-available/empath`.
Without it, requests to `/<name>/.well-known/agent-card.json` fall through to
the catch-all `location ~ /\.` → `deny all` → 403. Add new agent routes before
the `# 前端入口 + SPA 路由 fallback` comment.

## Conventions

- Keep files under 300 lines
- Use strong types (pydantic models, dataclasses), avoid unstructured dicts
- Logs output to `logs/` directory
- All responses must be in English or Chinese — never Korean
- Code comments must be in English only
