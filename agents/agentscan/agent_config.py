"""Agentscan Agent — skill definitions, system prompt, agent card."""

from __future__ import annotations

from a2a.types import (
    AgentCard, AgentSkill, AgentCapabilities, AgentExtension, AgentInterface,
)

from agents_core.settings import Settings

SYSTEM_PROMPT = (
    "You are an ERC-8004 AI Agent Explorer and Analyst powered by Agentscan. "
    "You have deep access to on-chain data for AI agents across multiple blockchain "
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
        id="search",
        name="Agent Search",
        description=(
            "Search ERC-8004 agents with combinable filters: free text, network, "
            "OASF skill/domain slug, owner address, reputation range, date range, "
            "endpoint health status, quality level, and sort order."
        ),
        tags=["search_agents"],
        examples=[
            "Find DeFi agents on Base with a reputation score above 4",
            "Search for coding agents registered this week",
            "Show quality agents owned by 0x1234... on Ethereum",
            "Find agents with healthy endpoints on Polygon",
        ],
    ),
    AgentSkill(
        id="discover",
        name="Agent Discovery",
        description=(
            "Discover agents by similarity or trending status. "
            "find_similar_agents returns agents sharing skills and domains with a given agent. "
            "get_trending_agents returns top-ranked, featured, and newest quality agents."
        ),
        tags=["find_similar_agents", "get_trending_agents"],
        examples=[
            "Find agents similar to agent abc-123",
            "Show trending agents right now",
            "What agents are similar to this one?",
        ],
    ),
    AgentSkill(
        id="leaderboard",
        name="Leaderboard",
        description=(
            "Composite-scored agent rankings weighted by service quality, usage frequency, "
            "metadata freshness, and profile completeness. Filterable by network."
        ),
        tags=["get_leaderboard"],
        examples=[
            "Show the global agent leaderboard",
            "Who ranks highest on Base?",
            "Top 10 agents by composite score",
        ],
    ),
    AgentSkill(
        id="agent_profile",
        name="Agent Profile",
        description=(
            "Retrieve full metadata for a specific agent: OASF classification, "
            "on-chain registration data, wallet, endpoints, and capabilities."
        ),
        tags=["get_agent"],
        examples=[
            "Get full details for agent abc-123",
            "What chain is this agent registered on?",
            "Show the agent card for agent xyz",
        ],
    ),
    AgentSkill(
        id="agent_reputation",
        name="Agent Reputation",
        description=(
            "Fetch reputation data for an agent: aggregate score and feedback count "
            "via get_agent_reputation, or individual feedback items with scores, tags, "
            "and timestamps via get_agent_feedbacks."
        ),
        tags=["get_agent_reputation", "get_agent_feedbacks"],
        examples=[
            "What's the reputation score for agent abc-123?",
            "Show all user feedbacks for this agent",
            "How many validations does this agent have?",
        ],
    ),
    AgentSkill(
        id="agent_activity",
        name="Agent Activity & Transactions",
        description=(
            "On-chain history for a specific agent. "
            "get_agent_activities returns registration, update, and validation events. "
            "get_agent_transactions returns gas usage, fees, and transaction breakdown."
        ),
        tags=["get_agent_activities", "get_agent_transactions"],
        examples=[
            "Show on-chain activity history for agent abc-123",
            "What transactions has this agent made?",
            "When was this agent last updated on-chain?",
        ],
    ),
    AgentSkill(
        id="endpoint_health",
        name="Endpoint Health",
        description=(
            "Check live endpoint status. "
            "get_agent_endpoint_health checks all URLs for a single agent (response time, status). "
            "get_endpoint_health_stats returns platform-wide health rates, optionally filtered by network."
        ),
        tags=["get_agent_endpoint_health", "get_endpoint_health_stats"],
        examples=[
            "Are the endpoints for agent abc-123 responding?",
            "Show endpoint health stats for Monad testnet",
            "What percentage of agents have healthy endpoints?",
        ],
    ),
    AgentSkill(
        id="owner_portfolio",
        name="Owner Portfolio",
        description=(
            "List all agents registered by a wallet address with a cross-network summary: "
            "agent count per chain, total reputation, and active endpoint rate."
        ),
        tags=["get_owner_portfolio"],
        examples=[
            "Show all agents owned by 0x1234...",
            "What's the portfolio for this wallet?",
            "How many agents does this address own across all networks?",
        ],
    ),
    AgentSkill(
        id="platform_analytics",
        name="Platform Analytics",
        description=(
            "Platform-wide statistics and trends. "
            "get_stats returns total agent and network counts. "
            "get_registration_trend shows daily registrations over a configurable window. "
            "get_analytics_overview covers tx stats and per-network breakdowns. "
            "get_skill_ranking lists the most popular OASF skills by agent count. "
            "get_recent_activities is the platform-wide activity feed."
        ),
        tags=[
            "get_stats", "get_registration_trend", "get_analytics_overview",
            "get_skill_ranking", "get_recent_activities",
        ],
        examples=[
            "How many agents are registered in total?",
            "Show registration trend for the last 90 days",
            "What are the most popular agent skills on the platform?",
            "Show the full analytics overview",
        ],
    ),
    AgentSkill(
        id="network_analytics",
        name="Network Analytics",
        description=(
            "Per-network data across all supported blockchains. "
            "list_networks and get_network_stats return chain metadata and agent counts. "
            "get_network_distribution breaks down total, quality, and reputable agents per network."
        ),
        tags=["list_networks", "get_network_stats", "get_network_distribution"],
        examples=[
            "Which network has the most registered agents?",
            "List all supported blockchain networks",
            "Compare quality agent counts across networks",
        ],
    ),
    AgentSkill(
        id="taxonomy",
        name="OASF Taxonomy",
        description=(
            "Explore the OASF classification system. "
            "list_taxonomy_skills and list_taxonomy_domains return all valid slugs for use in filters. "
            "get_taxonomy_distribution shows how agents are distributed across skills and domains."
        ),
        tags=["get_taxonomy_distribution", "list_taxonomy_skills", "list_taxonomy_domains"],
        examples=[
            "What OASF skill slugs are available?",
            "Show how agents are distributed across domains",
            "List all taxonomy domains I can filter by",
        ],
    ),
]


# Flat list of MCP tool names derived from skill tags — passed to register()
# so they appear in the IPFS services array as an MCP endpoint entry.
MCP_TOOLS: list[str] = [tool for skill in SKILLS for tool in (skill.tags or [])]

# OASF classification slugs for ERC-8004 registration
OASF_SKILLS: list[str] = [
    "data_engineering/data_transformation_pipeline",
    "data_engineering/data_analysis",
    "information_retrieval/search",
    "information_retrieval/question_answering",
]

OASF_DOMAINS: list[str] = [
    "technology/blockchain",
    "data_analytics",
    "finance",
]


def build_agent_card(settings: Settings) -> AgentCard:
    return AgentCard(
        name="Agentscan Agent",
        description=(
            "AI agent for deep exploration and analysis of ERC-8004 registered "
            "AI agents across multiple blockchain networks. Rich search with combinable filters, "
            "agent deep-dives (reputation, feedbacks, endpoints, transactions), owner "
            "portfolio analysis, platform analytics, leaderboard, and OASF taxonomy. "
            "Powered by Agentscan. Tools exposed via MCP protocol. "
            "Accepts USDC payment via x402 protocol."
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
