"""Agentscan Agent — skill definitions, system prompt, agent card."""

from __future__ import annotations

from a2a.types import (
    AgentCard, AgentSkill, AgentCapabilities, AgentExtension, AgentInterface,
)

from agents_core.settings import Settings

SYSTEM_PROMPT = (
    "You are an ERC-8004 AI Agent Explorer and Analyst powered by Agentscan. "
    "You have deep access to on-chain data for 146,000+ AI agents across 21 blockchain "
    "networks. You can search, analyze, and provide insights on any aspect of the "
    "AI agent ecosystem.\n\n"
    "## TOOLS BY USE CASE\n\n"
    "**Search & Discovery:**\n"
    "- search_agents: Rich filters — text, network, skill, domain, owner, reputation, "
    "date range, endpoint health. Combine freely.\n"
    "- find_similar_agents: Discover related agents by shared skills/domains.\n"
    "- get_trending_agents: Top-ranked, featured, and newest quality agents.\n"
    "- get_leaderboard: Composite-scored ranking (service, usage, freshness, profile).\n\n"
    "**Agent Deep Dive:**\n"
    "- get_agent: Full metadata, OASF classification, on-chain data, agent wallet.\n"
    "- get_agent_reputation: Feedback count, average score, validation count.\n"
    "- get_agent_feedbacks: Individual feedback items with scores, tags, timestamps.\n"
    "- get_agent_activities: On-chain event history (registration, updates, validations).\n"
    "- get_agent_endpoint_health: Live endpoint checks — URLs, response times, status.\n"
    "- get_agent_transactions: Gas usage, fees, transaction breakdown.\n\n"
    "**Owner / Portfolio:**\n"
    "- get_owner_portfolio: All agents by owner address with cross-network summary.\n"
    "- search_agents(owner=...): Filter by owner in search.\n\n"
    "**Data Analysis & Stats:**\n"
    "- get_stats: Platform totals — agents, networks, activities.\n"
    "- get_registration_trend: Daily registration counts over time.\n"
    "- get_analytics_overview: Full analytics — tx stats, daily trends, per-network breakdown.\n"
    "- get_network_distribution: Agent count per network (total, quality, reputable).\n"
    "- get_skill_ranking: Most popular skills by agent count.\n"
    "- get_recent_activities: Platform-wide activity feed.\n\n"
    "**Taxonomy:**\n"
    "- get_taxonomy_distribution: Skill/domain distribution across agents.\n"
    "- list_taxonomy_skills / list_taxonomy_domains: All OASF categories (for filter slugs).\n\n"
    "**Networks & Health:**\n"
    "- list_networks / get_network_stats: Network info and agent counts.\n"
    "- get_endpoint_health_stats: Platform-wide endpoint health overview.\n\n"
    "## TIPS\n"
    "- For skill/domain filters in search_agents, use slugs like 'defi', 'coding', "
    "'agent_orchestration', 'finance'. Use list_taxonomy_skills to discover slugs.\n"
    "- Combine multiple tools for analysis: e.g. search + get_agent + get_agent_feedbacks.\n"
    "- For 'which network has the most agents', use get_network_distribution.\n"
    "- For 'show me this owner's agents', use get_owner_portfolio.\n"
    "- For competitive analysis, use find_similar_agents + get_leaderboard.\n"
    "- Always provide clear, structured summaries with key metrics highlighted."
)

SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="deep_search",
        name="Deep Search",
        description=(
            "Search AI agents with 12+ combinable filters: text, network, OASF skill/domain, "
            "owner address, reputation range, date range, endpoint health, quality level, "
            "and flexible sorting."
        ),
        tags=["search", "filter", "erc8004", "multichain"],
        examples=[
            "Find DeFi agents on Base with reputation",
            "Search agents with coding skills created this week",
            "Show verified agents owned by 0x1234...",
            "Find agents with working endpoints on Ethereum",
        ],
    ),
    AgentSkill(
        id="agent_analysis",
        name="Agent Analysis",
        description=(
            "Deep-dive into any agent: metadata, reputation breakdown, individual feedbacks, "
            "on-chain activities, endpoint health checks, transaction history, and similar agents."
        ),
        tags=["agent", "analysis", "reputation", "health"],
        examples=[
            "Analyze agent abc-123 in detail",
            "Show all feedbacks for this agent",
            "Check which endpoints are working",
            "What's the transaction history?",
        ],
    ),
    AgentSkill(
        id="owner_portfolio",
        name="Owner Portfolio",
        description="View all agents owned by a wallet address with cross-network portfolio summary.",
        tags=["owner", "portfolio", "wallet"],
        examples=[
            "Show all agents owned by 0x1234...",
            "What's this wallet's agent portfolio?",
        ],
    ),
    AgentSkill(
        id="data_analysis",
        name="Data Analysis",
        description=(
            "Platform-wide analytics: registration trends, network distribution, "
            "skill rankings, transaction stats, endpoint health rates, and leaderboard."
        ),
        tags=["analytics", "stats", "trends", "data"],
        examples=[
            "Show registration trend for the last 90 days",
            "Which network has the most agents?",
            "What are the most popular agent skills?",
            "Show the analytics overview",
        ],
    ),
    AgentSkill(
        id="leaderboard",
        name="Leaderboard",
        description=(
            "Composite-scored agent rankings based on service quality, usage, "
            "freshness, and profile completeness."
        ),
        tags=["leaderboard", "ranking", "score"],
        examples=[
            "Show the top agents leaderboard",
            "Who's ranked highest on Base?",
        ],
    ),
    AgentSkill(
        id="taxonomy",
        name="OASF Taxonomy",
        description="Explore 136 skills and 204 domains in the OASF classification system and their distribution.",
        tags=["taxonomy", "oasf", "skills", "domains"],
        examples=[
            "What skills are available?",
            "Show taxonomy distribution",
        ],
    ),
    AgentSkill(
        id="network_intel",
        name="Network Intelligence",
        description="Network-level stats, agent distribution, and endpoint health across 21 blockchains.",
        tags=["networks", "health", "monitoring"],
        examples=[
            "Compare agent counts across networks",
            "Show endpoint health stats for Monad",
        ],
    ),
]


def build_agent_card(settings: Settings) -> AgentCard:
    return AgentCard(
        name="Agentscan Agent",
        description=(
            "AI agent for deep exploration and analysis of 146,000+ ERC-8004 registered "
            "AI agents across 21 blockchain networks. Rich search with 12+ filters, "
            "agent deep-dives (reputation, feedbacks, endpoints, transactions), owner "
            "portfolio analysis, platform analytics, leaderboard, and OASF taxonomy. "
            "Powered by Agentscan. Accepts USDC payment via x402 protocol."
        ),
        supported_interfaces=[AgentInterface(url=settings.base_url + "/")],
        version="0.3.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False,
            extensions=[
                AgentExtension(
                    uri="https://github.com/google-a2a/a2a-x402/v0.1",
                    description="Accepts USDC payments via x402 protocol.",
                    required=False,
                ),
            ] if settings.wallet_address else [],
        ),
        skills=SKILLS,
    )
