"""Agent-friendly service discovery: /discovery (JSON) and /llms.txt (markdown).

Auto-generates from AgentCard + Pricing + Settings so every agent gets these
endpoints for free, following industry best practices:
  - /discovery — machine-readable JSON (inspired by AsterPay, NANDA AgentFacts)
  - /llms.txt  — LLM-optimized plaintext (llmstxt.org standard by Jeremy Howard)
"""

from __future__ import annotations

from a2a.types import AgentCard

from agents_core.settings import Settings, Pricing


def build_discovery(
    agent_card: AgentCard,
    pricing: Pricing,
    settings: Settings,
    mcp_tools: list[str] | None = None,
) -> dict:
    """Build a JSON discovery response aggregating capabilities, pricing, and payment."""
    skills = []
    for skill in agent_card.skills:
        skills.append({
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "price": pricing.price_for(skill.id),
            "tags": list(skill.tags),
            "examples": list(skill.examples),
        })

    x402_enabled = bool(settings.wallet_address)

    return {
        "name": agent_card.name,
        "description": agent_card.description,
        "version": agent_card.version or "0.1.0",
        "protocols": {
            "a2a": {
                "version": "0.3",
                "spec": "https://a2a-protocol.org",
                "agent_card": "/.well-known/agent-card.json",
            },
            **({"mcp": {
                "spec": "https://modelcontextprotocol.io",
                "transport": "http",
                "url": settings.base_url + "/",
                "tools": mcp_tools,
                "install": {
                    "claude_desktop": {
                        "config_key": "mcpServers",
                        "entry": {
                            agent_card.name.lower().replace(" ", "_"): {
                                "url": settings.base_url + "/",
                                "transport": "http",
                            }
                        },
                    },
                    "cursor": {
                        "config_key": "mcpServers",
                        "entry": {
                            agent_card.name.lower().replace(" ", "_"): {
                                "url": settings.base_url + "/",
                                "transport": "http",
                            }
                        },
                    },
                },
            }} if mcp_tools else {}),
            "x402": {
                "enabled": x402_enabled,
                "spec": "https://x402.org",
                "network": settings.chain_network,
                "asset": "USDC",
                "pay_to": settings.wallet_address or None,
                "default_price": pricing.default_price,
                "facilitator": settings.facilitator_url,
            },
        },
        "skills": skills,
        "endpoints": {
            "task": {
                "method": "POST",
                "path": "/",
                "paid": x402_enabled,
                "price": pricing.default_price,
                "description": "A2A JSON-RPC task execution",
            },
            "agent_card": {
                "method": "GET",
                "path": "/.well-known/agent-card.json",
                "paid": False,
                "description": "A2A agent card (capabilities, skills)",
            },
            "discovery": {
                "method": "GET",
                "path": "/discovery",
                "paid": False,
                "description": "Agent-friendly service discovery (this endpoint)",
            },
            "llms_txt": {
                "method": "GET",
                "path": "/llms.txt",
                "paid": False,
                "description": "LLM-optimized plaintext API reference",
            },
            "health": {
                "method": "GET",
                "path": "/health",
                "paid": False,
                "description": "Health check",
            },
        },
    }


def build_llms_txt(
    agent_card: AgentCard,
    pricing: Pricing,
    settings: Settings,
    mcp_tools: list[str] | None = None,
) -> str:
    """Build an llms.txt-style markdown document (llmstxt.org format).

    Structure: H1 title, blockquote summary, then structured sections for
    skills, payment, endpoints, and integration examples.
    """
    name = agent_card.name
    desc = agent_card.description
    base = settings.base_url
    x402_enabled = bool(settings.wallet_address)

    lines: list[str] = []
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"> {desc}")
    lines.append("")

    # ── Skills ──
    lines.append("## Skills")
    lines.append("")
    lines.append("| Skill | Price | Description |")
    lines.append("|-------|-------|-------------|")
    for skill in agent_card.skills:
        price = pricing.price_for(skill.id)
        lines.append(f"| {skill.name} | {price} | {skill.description} |")
    lines.append("")

    for skill in agent_card.skills:
        price = pricing.price_for(skill.id)
        examples = ", ".join(f'"{e}"' for e in skill.examples[:2])
        lines.append(f"- **{skill.name}** (`{skill.id}`, {price}): {skill.description}")
        if examples:
            lines.append(f"  - Examples: {examples}")
    lines.append("")

    # ── Payment ──
    lines.append("## Payment")
    lines.append("")
    if x402_enabled:
        lines.append(f"- Protocol: x402 (HTTP 402 Payment Required)")
        lines.append(f"- Network: {settings.chain_network}")
        lines.append(f"- Asset: USDC")
        lines.append(f"- Default price: {pricing.default_price}")
        lines.append(f"- Pay to: {settings.wallet_address}")
        lines.append(f"- Facilitator: {settings.facilitator_url}")
        lines.append("")
        lines.append("### Flow")
        lines.append("")
        lines.append("1. POST / with A2A JSON-RPC task request")
        lines.append("2. Receive HTTP 402 + `PAYMENT-REQUIRED` header with payment details")
        lines.append(f"3. Sign USDC authorization (EIP-712) on {settings.chain_network}")
        lines.append("4. Retry the same request with `X-PAYMENT` header containing signed proof")
        lines.append("5. Receive 200 response with task result")
    else:
        lines.append("Payment is not currently enabled for this agent.")
    lines.append("")

    # ── Endpoints ──
    lines.append("## Endpoints")
    lines.append("")
    lines.append("| Method | Path | Paid | Description |")
    lines.append("|--------|------|------|-------------|")
    paid_label = f"Yes ({pricing.default_price})" if x402_enabled else "No"
    lines.append(f"| POST | / | {paid_label} | A2A JSON-RPC task execution |")
    lines.append("| GET | /.well-known/agent-card.json | No | A2A agent card |")
    lines.append("| GET | /discovery | No | JSON service discovery |")
    lines.append("| GET | /llms.txt | No | This document |")
    lines.append("| GET | /health | No | Health check |")
    lines.append("")

    # ── Integration ──
    lines.append("## Integration")
    lines.append("")
    lines.append("```python")
    lines.append("import httpx")
    lines.append("")
    lines.append(f'resp = httpx.post("{base}/", json={{')
    lines.append('    "jsonrpc": "2.0",')
    lines.append('    "method": "message/send",')
    lines.append("    \"params\": {")
    lines.append('        "message": {')
    lines.append('            "role": "user",')
    lines.append('            "parts": [{"kind": "text", "text": "YOUR PROMPT HERE"}]')
    lines.append("        }")
    lines.append("    },")
    lines.append('    "id": "1"')
    lines.append("})")
    lines.append("# Returns 402 if payment required, 200 with result if paid")
    lines.append("```")
    lines.append("")

    # ── MCP ──
    if mcp_tools:
        lines.append("## MCP (Model Context Protocol)")
        lines.append("")
        lines.append(
            "This agent exposes its tools via the [Model Context Protocol](https://modelcontextprotocol.io) "
            "(MCP), Anthropic's open standard for connecting AI clients to external tools. "
            "Any MCP-compatible host (Claude, Cursor, etc.) can invoke these tools directly."
        )
        lines.append("")
        lines.append(f"**Endpoint:** `{settings.base_url}/`  ")
        lines.append("**Transport:** HTTP (Streamable HTTP)")
        lines.append("")
        lines.append("**Available tools:**")
        lines.append("")
        for tool in mcp_tools:
            lines.append(f"- `{tool}`")
        lines.append("")

        mcp_key = agent_card.name.lower().replace(" ", "_")
        lines.append("### Installation")
        lines.append("")
        lines.append("**Claude Desktop** — add to `claude_desktop_config.json`:")
        lines.append("```json")
        lines.append('{')
        lines.append('  "mcpServers": {')
        lines.append(f'    "{mcp_key}": {{')
        lines.append(f'      "url": "{settings.base_url}/",')
        lines.append('      "transport": "http"')
        lines.append('    }')
        lines.append('  }')
        lines.append('}')
        lines.append("```")
        lines.append("")
        lines.append("**Cursor / Windsurf / other MCP hosts** — same `mcpServers` config block.")
        lines.append("")

    # ── Standards ──
    lines.append("## Standards")
    lines.append("")
    lines.append("- [A2A Protocol](https://a2a-protocol.org) — Agent-to-Agent communication")
    if mcp_tools:
        lines.append("- [MCP](https://modelcontextprotocol.io) — Model Context Protocol (tool invocation)")
    lines.append("- [x402](https://x402.org) — HTTP-native payment protocol")
    lines.append("- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) — Trustless AI agent registry")
    lines.append("- [llms.txt](https://llmstxt.org) — LLM-friendly documentation standard")
    lines.append("")

    return "\n".join(lines)
