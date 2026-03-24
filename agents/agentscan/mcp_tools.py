"""Agentscan MCP tools — REST API backend via httpx."""

from __future__ import annotations

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "agentscan",
    instructions=(
        "Tools for deep exploration and analysis of ERC-8004 AI agents across 21 "
        "blockchain networks. Rich search, data analysis, reputation, taxonomy, "
        "leaderboard, owner portfolio, and activity tracking."
    ),
)

_BASE_URL: str | None = None


def _base_url() -> str:
    global _BASE_URL
    if _BASE_URL is None:
        _BASE_URL = os.environ.get(
            "AM_AGENTSCAN_URL", "https://agentscan.info"
        ).rstrip("/")
    return _BASE_URL


def _get(path: str, params: dict | None = None, timeout: int = 30) -> dict | list:
    """GET request to Agentscan API."""
    url = f"{_base_url()}/api{path}"
    resp = httpx.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════
# SEARCH & DISCOVERY
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def search_agents(
    query: str | None = None,
    network: str | None = None,
    skill: str | None = None,
    domain: str | None = None,
    owner: str | None = None,
    quality: str | None = None,
    has_reputation: bool | None = None,
    has_endpoints: bool | None = None,
    reputation_min: float | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    sort_field: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Search ERC-8004 AI agents with rich combinable filters.

    Args:
        query: Text search across name, description, and wallet address.
        network: Network slug (ethereum, base, arbitrum, bsc, polygon, monad, celo, etc.).
        skill: OASF skill filter (partial match, e.g. 'defi', 'coding', 'agent_orchestration').
        domain: OASF domain filter (partial match, e.g. 'finance', 'healthcare', 'scientific').
        owner: Owner wallet address (exact match).
        quality: 'all', 'basic' (has name+description), or 'verified' (has reputation).
        has_reputation: True to show only agents with feedback/reputation.
        has_endpoints: True to show only agents with working endpoints.
        reputation_min: Minimum reputation score.
        created_after: ISO date string, e.g. '2026-03-01'.
        created_before: ISO date string, e.g. '2026-03-31'.
        sort_field: 'created_at', 'name', 'reputation_score', or 'reputation_count'.
        sort_order: 'asc' or 'desc'.
        page: Page number (default 1).
        page_size: Results per page (default 20, max 100).
    """
    params: dict = {
        "page": page, "page_size": page_size,
        "sort_field": sort_field, "sort_order": sort_order,
    }
    _set(params, "search", query)
    _set(params, "network", network)
    _set(params, "skill", skill)
    _set(params, "domain", domain)
    _set(params, "owner", owner)
    _set(params, "quality", quality)
    _set(params, "has_reputation", has_reputation)
    _set(params, "has_endpoints", has_endpoints)
    _set(params, "reputation_min", reputation_min)
    _set(params, "created_after", created_after)
    _set(params, "created_before", created_before)
    return _get("/agents", params)


@mcp.tool()
def find_similar_agents(agent_id: str, limit: int = 10) -> list:
    """Find agents similar to a given agent based on shared skills, domains, and network.

    Args:
        agent_id: The agent's UUID.
        limit: Max results (default 10, max 50).
    """
    return _get(f"/agents/similar/{agent_id}", {"limit": limit})


@mcp.tool()
def get_trending_agents(limit: int = 5) -> dict:
    """Get trending, top-ranked (by reputation), and featured (most reviews) agents.

    Args:
        limit: Max agents per category (default 5, max 20).
    """
    return _get("/agents/trending", {"limit": limit})


@mcp.tool()
def get_leaderboard(
    network: str | None = None,
    sort_by: str = "score",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Get ranked agent leaderboard with composite scores.

    Agents are scored on: service (working endpoints), usage (feedback count),
    freshness (recent reputation updates), and profile (name, description, skills).

    Args:
        network: Filter by network slug (optional).
        sort_by: 'score', 'service', 'usage', 'freshness', or 'profile'.
        page: Page number.
        page_size: Results per page.
    """
    params: dict = {"page": page, "page_size": page_size, "sort_by": sort_by}
    _set(params, "network", network)
    return _get("/leaderboard", params)


# ═══════════════════════════════════════════════════════════════════════
# AGENT DETAILS & HISTORY
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def get_agent(agent_id: str) -> dict:
    """Get full details of an agent — metadata, OASF classification, reputation,
    owner, endpoints, on-chain data, agent wallet.

    Args:
        agent_id: The agent's UUID.
    """
    return _get(f"/agents/{agent_id}")


@mcp.tool()
def get_agent_reputation(agent_id: str) -> dict:
    """Get reputation summary — feedback count, average score, validation count.

    Args:
        agent_id: The agent's UUID.
    """
    return _get(f"/agents/{agent_id}/reputation-summary")


@mcp.tool()
def get_agent_feedbacks(
    agent_id: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """Get actual feedback items for an agent — scores, tags, timestamps, client addresses.

    Shows individual reputation feedback with value, tag categories (starred, uptime,
    successrate, responsetime), client address, and transaction hash.

    Args:
        agent_id: The agent's UUID.
        page: Page number.
        page_size: Results per page (max 50).
    """
    return _get(f"/agents/{agent_id}/feedbacks", {"page": page, "page_size": page_size})


@mcp.tool()
def get_agent_activities(agent_id: str) -> list:
    """Get activity history for an agent — registrations, reputation updates, validations.

    Shows on-chain events with timestamps, tx hashes, and descriptions.

    Args:
        agent_id: The agent's UUID.
    """
    return _get(f"/activities/agent/{agent_id}")


@mcp.tool()
def get_agent_endpoint_health(agent_id: str) -> dict:
    """Check endpoint health for a specific agent — which URLs are reachable,
    response times, status codes.

    Args:
        agent_id: The agent's UUID.
    """
    return _get(f"/agents/{agent_id}/endpoint-health", timeout=60)


@mcp.tool()
def get_agent_transactions(agent_id: str) -> dict:
    """Get detailed transaction breakdown for an agent — gas used, fees, tx types.

    Args:
        agent_id: The agent's UUID.
    """
    return _get(f"/analytics/agent/{agent_id}/transactions")


# ═══════════════════════════════════════════════════════════════════════
# OWNER / PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def get_owner_portfolio(owner_address: str) -> dict:
    """Get all agents owned by a wallet address with portfolio summary.

    Returns: total agents, active networks, total reputation, total feedbacks,
    unique skills/domains, and the full agent list.

    Args:
        owner_address: The owner's wallet address (0x...).
    """
    return _get(f"/agents/by-owner/{owner_address}")


# ═══════════════════════════════════════════════════════════════════════
# PLATFORM ANALYTICS
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def get_stats() -> dict:
    """Get platform-wide statistics — total agents, active agents, networks, activities, sync status."""
    return _get("/stats")


@mcp.tool()
def get_registration_trend(days: int = 30) -> dict:
    """Get daily agent registration counts over time.

    Args:
        days: Number of days to look back (default 30, max 365).
    """
    return _get("/stats/registration-trend", {"days": days})


@mcp.tool()
def get_analytics_overview(
    days: int = 30,
    network: str | None = None,
) -> dict:
    """Get comprehensive analytics — transaction stats, daily trends by tx type,
    per-network breakdown, gas/fee totals, quality rates.

    Args:
        days: Lookback period in days (default 30).
        network: Filter by network slug (optional).
    """
    params: dict = {"days": days}
    _set(params, "network", network)
    return _get("/analytics/overview", params)


@mcp.tool()
def get_network_distribution() -> dict:
    """Get agent distribution across all networks — total, quality, and reputable agent
    counts per network. Shows which networks have the most/best agents."""
    return _get("/stats/network-distribution")


@mcp.tool()
def get_skill_ranking(limit: int = 30) -> dict:
    """Get most popular skills by agent count — which capabilities are most common.

    Args:
        limit: Number of top skills to return (default 30, max 136).
    """
    return _get("/stats/skill-ranking", {"limit": limit})


@mcp.tool()
def get_recent_activities(page: int = 1, page_size: int = 20) -> dict:
    """Get recent platform-wide activities — new registrations, reputation updates, validations.

    Args:
        page: Page number.
        page_size: Results per page.
    """
    return _get("/activities", {"page": page, "page_size": page_size})


# ═══════════════════════════════════════════════════════════════════════
# NETWORKS & HEALTH
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def list_networks() -> list:
    """List all 21 supported blockchain networks and their configurations."""
    return _get("/networks")


@mcp.tool()
def get_network_stats() -> list:
    """Get all networks with agent count statistics."""
    return _get("/networks/stats")


@mcp.tool()
def get_endpoint_health_stats(network: str | None = None) -> dict:
    """Get endpoint health overview — total scanned, working agents, health rate, top agents.

    Args:
        network: Filter by network slug (optional).
    """
    params: dict = {}
    _set(params, "network", network)
    return _get("/endpoint-health/quick-stats", params or None)


# ═══════════════════════════════════════════════════════════════════════
# TAXONOMY
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool()
def get_taxonomy_distribution() -> dict:
    """Get OASF taxonomy distribution — skills and domains across all classified agents."""
    return _get("/taxonomy/distribution")


@mcp.tool()
def list_taxonomy_skills() -> dict:
    """List all 136 OASF skill categories with slugs. Use slugs for search_agents skill filter."""
    return _get("/taxonomy/skills")


@mcp.tool()
def list_taxonomy_domains() -> dict:
    """List all 204 OASF domain categories with slugs. Use slugs for search_agents domain filter."""
    return _get("/taxonomy/domains")


# ── Helpers ───────────────────────────────────────────────────────────


def _set(params: dict, key: str, value) -> None:
    """Set param if value is not None."""
    if value is not None:
        params[key] = value
