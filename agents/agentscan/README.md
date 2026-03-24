# Agentscan Agent

ERC-8004 AI Agent Explorer & Analyst — deep search, data analysis, and insights across 146,000+ on-chain AI agents on 21 blockchain networks.

**Backend pattern**: REST API (httpx → [agentscan.info](https://agentscan.info))
**Port**: 9010
**Protocol**: A2A + x402

---

## Quick Start

```bash
cd agents/agentscan
cp .env.example .env   # fill in AM_LLM_API_KEY
./scripts/run.sh
# Agent at http://localhost:9010
# Health: http://localhost:9010/health
# Card: http://localhost:9010/.well-known/agent-card.json
```

---

## 23 MCP Tools

### Search & Discovery

| Tool | Description |
|------|-------------|
| `search_agents` | Rich search with 15 combinable filters: text, network, skill, domain, owner, reputation, date range, endpoint health, quality, sorting |
| `find_similar_agents` | Discover agents with shared skills/domains/network |
| `get_trending_agents` | Top-ranked (reputation), featured (most reviews), trending (newest quality) |
| `get_leaderboard` | Composite-scored ranking by service, usage, freshness, profile |

### Agent Deep Dive

| Tool | Description |
|------|-------------|
| `get_agent` | Full details — metadata, OASF classification, on-chain data, agent wallet |
| `get_agent_reputation` | Reputation summary — feedback count, average score, validation count |
| `get_agent_feedbacks` | Individual feedback items with scores, tags, timestamps, client addresses |
| `get_agent_activities` | On-chain event history — registrations, reputation updates, validations |
| `get_agent_endpoint_health` | Live endpoint checks — URLs, response times, status codes |
| `get_agent_transactions` | Transaction breakdown — gas used, fees, tx types |

### Owner / Portfolio

| Tool | Description |
|------|-------------|
| `get_owner_portfolio` | All agents by owner address + cross-network portfolio summary (total reputation, networks, skills) |

### Platform Analytics

| Tool | Description |
|------|-------------|
| `get_stats` | Platform totals — agents, active agents, networks, activities, sync status |
| `get_registration_trend` | Daily registration counts over configurable time range (1-365 days) |
| `get_analytics_overview` | Full analytics — tx stats, daily trends by type, per-network breakdown, gas/fees |
| `get_network_distribution` | Agent count per network — total, quality, reputable breakdown |
| `get_skill_ranking` | Most popular skills by agent count |
| `get_recent_activities` | Platform-wide activity feed — new registrations, updates, validations |

### Networks & Health

| Tool | Description |
|------|-------------|
| `list_networks` | All 21 supported blockchain networks |
| `get_network_stats` | Networks with agent count statistics |
| `get_endpoint_health_stats` | Platform-wide endpoint health overview — scan rate, working agents |

### OASF Taxonomy

| Tool | Description |
|------|-------------|
| `get_taxonomy_distribution` | Skill/domain distribution across all classified agents |
| `list_taxonomy_skills` | All 136 OASF skill categories with slugs (for search filters) |
| `list_taxonomy_domains` | All 204 OASF domain categories with slugs (for search filters) |

---

## search_agents Filter Reference

```
search_agents(
    query="DeFi",                    # text search (name, description, address)
    network="base",                  # network slug
    skill="defi",                    # OASF skill (partial match)
    domain="finance",                # OASF domain (partial match)
    owner="0x1234...",               # owner wallet (exact)
    quality="verified",              # all | basic | verified
    has_reputation=True,             # only agents with feedback
    has_endpoints=True,              # only agents with working endpoints
    reputation_min=10.0,             # minimum reputation score
    created_after="2026-03-01",      # ISO date range start
    created_before="2026-03-31",     # ISO date range end
    sort_field="reputation_score",   # created_at | name | reputation_score | reputation_count
    sort_order="desc",               # asc | desc
    page=1,                          # pagination
    page_size=20,                    # results per page (max 100)
)
```

All filters are optional and combinable.

---

## Example Queries

**Search & Discovery**
- "Find DeFi agents on Base with reputation"
- "Search agents with coding skills created this week"
- "Show verified agents owned by 0x1234..."
- "Find agents with working endpoints on Ethereum"

**Agent Analysis**
- "Analyze agent abc-123 in detail"
- "Show all feedbacks for this agent"
- "Check which endpoints are working for this agent"
- "What's the transaction history?"

**Data Analysis**
- "Show registration trend for the last 90 days"
- "Which network has the most agents?"
- "What are the most popular agent skills?"
- "Compare agent counts across networks"
- "Show the analytics overview with transaction stats"

**Owner Portfolio**
- "Show all agents owned by 0x1234..."
- "What's this wallet's agent portfolio across networks?"

**Leaderboard**
- "Show the top agents leaderboard"
- "Who's ranked highest on Base network?"
- "Sort leaderboard by service score"

---

## Supported Networks (21)

Ethereum, Arbitrum, Avalanche, Base, BSC, Celo, Gnosis, Linea, Mantle, MegaETH, Monad, Optimism, Polygon, Scroll, Soneium, XLayer, Abstract, GOAT, Metis, SKALE, Taiko

---

## Agentscan Backend Changes

This agent requires backend enhancements deployed to Agentscan (`/agents` endpoint):

**New filters on `GET /api/agents`:**
- `skill` — OASF skill filter (partial match)
- `domain` — OASF domain filter (partial match)
- `owner` — owner wallet address (exact match)
- `created_after` / `created_before` — date range
- `has_endpoints` — working endpoint filter
- `reputation_count` — new sort field

**New endpoints:**
- `GET /api/agents/similar/{id}` — similar agent discovery
- `GET /api/agents/by-owner/{address}` — owner portfolio with aggregation
- `GET /api/stats/network-distribution` — per-network agent distribution
- `GET /api/stats/skill-ranking` — most popular skills

These changes are in `/home/ubuntu/Agentscan/backend/src/api/agents.py` and `stats.py`.

---

## Architecture

```
User (natural language)
    ↓ A2A protocol
Agentscan Agent (port 9010)
    ↓ LLM (DeepSeek/OpenRouter)
    ↓ MCP tools (httpx)
Agentscan REST API (agentscan.info)
    ↓ SQLAlchemy queries
SQLite/PostgreSQL (146K+ agents, 21 networks)
    ↑ Synced from ERC-8004 contracts
21 Mainnet Networks (Web3.py)
```

---

## Docker

```bash
# Build and run
docker compose up --build

# Or via script
./scripts/deploy.sh
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AM_LLM_API_KEY` | Yes | — | LLM API key |
| `AM_AGENTSCAN_URL` | No | `https://agentscan.info` | Agentscan API base URL |
| `AM_LLM_BASE_URL` | No | `https://api.deepseek.com` | LLM endpoint |
| `AM_LLM_MODEL` | No | `deepseek-chat` | LLM model |
| `AM_PORT` | No | `9010` | Agent port |
| `AM_BASE_URL` | No | `http://localhost:9010` | Public URL |
| `AM_WALLET_ADDRESS` | No | — | x402 payment wallet |
