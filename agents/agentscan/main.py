"""Agentscan A2A Agent Service — entry point.

Dual mode:
- POST / (A2A) — LLM agent with x402 payment (if wallet configured)
- GET /api/* — Free direct-query proxy to Agentscan backend (no LLM)
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import uvicorn
from fastapi.responses import JSONResponse
from starlette.requests import Request

from agents_core.app import create_app, setup_logging
from agents_core.settings import Pricing, get_settings
from agent_config import SYSTEM_PROMPT, build_agent_card, MCP_TOOLS

# Agentscan API endpoints exposed as free direct queries (no LLM, no x402).
_PROXY_ROUTES: list[tuple[str, str]] = [
    ("/api/stats", "/api/stats"),
    ("/api/stats/registration-trend", "/api/stats/registration-trend"),
    ("/api/networks", "/api/networks"),
    ("/api/networks/stats", "/api/networks/stats"),
    ("/api/agents", "/api/agents"),
    ("/api/agents/trending", "/api/agents/trending"),
    ("/api/agents/featured", "/api/agents/featured"),
    ("/api/activities", "/api/activities"),
    ("/api/leaderboard", "/api/leaderboard"),
    ("/api/taxonomy/skills", "/api/taxonomy/skills"),
    ("/api/taxonomy/domains", "/api/taxonomy/domains"),
    ("/api/taxonomy/distribution", "/api/taxonomy/distribution"),
    ("/api/endpoint-health/quick-stats", "/api/endpoint-health/quick-stats"),
    ("/api/analytics/overview", "/api/analytics/overview"),
]


async def _proxy_get(url: str, params: dict | None = None) -> JSONResponse:
    """Forward GET request to Agentscan backend and return JSON response."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, params=params)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


def _add_proxy_routes(app, api_base: str) -> None:
    """Register free proxy routes on the FastAPI app."""

    # Static routes — pass through query params
    for local_path, remote_path in _PROXY_ROUTES:
        _url = api_base + remote_path

        @app.get(local_path, name=local_path.lstrip("/").replace("/", "_"))
        async def _proxy(request: Request, _u: str = _url) -> JSONResponse:
            return await _proxy_get(_u, params=dict(request.query_params))

    # Parameterised routes (agent_id / owner_address)
    @app.get("/api/agents/similar/{agent_id}")
    async def proxy_similar(agent_id: str, limit: int = 10) -> JSONResponse:
        return await _proxy_get(
            f"{api_base}/api/agents/similar/{agent_id}", {"limit": limit},
        )

    @app.get("/api/agents/by-owner/{owner_address}")
    async def proxy_by_owner(owner_address: str, page: int = 1) -> JSONResponse:
        return await _proxy_get(
            f"{api_base}/api/agents/by-owner/{owner_address}", {"page": page},
        )

    @app.get("/api/agents/{agent_id}/endpoint-health")
    async def proxy_endpoint_health(agent_id: str) -> JSONResponse:
        return await _proxy_get(f"{api_base}/api/agents/{agent_id}/endpoint-health")

    @app.get("/api/agents/{agent_id}/feedbacks")
    async def proxy_feedbacks(
        agent_id: str, page: int = 1, page_size: int = 10,
    ) -> JSONResponse:
        return await _proxy_get(
            f"{api_base}/api/agents/{agent_id}/feedbacks",
            {"page": page, "page_size": page_size},
        )

    @app.get("/api/agents/{agent_id}/reputation-summary")
    async def proxy_reputation(agent_id: str) -> JSONResponse:
        return await _proxy_get(
            f"{api_base}/api/agents/{agent_id}/reputation-summary",
        )

    @app.get("/api/activities/agent/{agent_id}")
    async def proxy_agent_activities(agent_id: str) -> JSONResponse:
        return await _proxy_get(f"{api_base}/api/activities/agent/{agent_id}")

    @app.get("/api/analytics/agent/{agent_id}/transactions")
    async def proxy_agent_tx(agent_id: str) -> JSONResponse:
        return await _proxy_get(
            f"{api_base}/api/analytics/agent/{agent_id}/transactions",
        )

    # Must be last — catches any remaining /api/agents/{agent_id}
    @app.get("/api/agents/{agent_id}")
    async def proxy_agent_detail(agent_id: str) -> JSONResponse:
        return await _proxy_get(f"{api_base}/api/agents/{agent_id}")


if __name__ == "__main__":
    settings = get_settings()
    pricing = Pricing(Path(__file__).parent / "config" / "pricing.toml")
    setup_logging(Path("logs"), "agentscan-agent")

    app = create_app(
        settings,
        pricing,
        agent_card=build_agent_card(settings),
        mcp_module="mcp_entry",
        system_prompt=SYSTEM_PROMPT,
        mcp_tools=MCP_TOOLS,
    )

    # Add free direct-query proxy routes (no LLM, no x402)
    api_base = os.environ.get("AM_AGENTSCAN_URL", "https://agentscan.info").rstrip("/")
    _add_proxy_routes(app, api_base)

    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
