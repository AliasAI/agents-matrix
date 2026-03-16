"""App factory: compose FastAPI + A2A + x402 into a single ASGI application."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from x402.http.middleware.fastapi import PaymentMiddlewareASGI

from config.settings import Settings, Pricing
from server.agent_card import build_agent_card
from server.payment import build_resource_server, build_route_config
from executor.cast_executor import CastExecutor

logger = logging.getLogger(__name__)


def create_app(settings: Settings, pricing: Pricing) -> FastAPI:
    """Build the full application stack."""
    app = FastAPI(title="Cast Transaction Agent", version="0.1.0")

    # ── A2A agent ──
    agent_card = build_agent_card()
    executor = CastExecutor(settings=settings)
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    a2a_app.add_routes_to_app(app)

    # ── x402 payment gate ──
    if settings.wallet_address:
        resource_server = build_resource_server(settings)
        route_config = build_route_config(settings, pricing)
        app.add_middleware(PaymentMiddlewareASGI, routes=route_config, server=resource_server)
        logger.info("x402 payment gate enabled for POST /")
    else:
        logger.warning("No wallet address configured — x402 payment gate DISABLED")

    # ── Utility endpoints ──
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "cast-transaction-agent"}

    return app
