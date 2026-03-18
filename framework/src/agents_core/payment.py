"""x402 payment middleware configuration for the A2A task endpoint."""

from __future__ import annotations

import base64
import os
import time

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

from agents_core.settings import Settings, Pricing


def _build_cdp_auth_provider(key_id: str, private_key_b64: str):
    """Build a CDP JWT auth provider for the x402 facilitator.

    CDP Secret API Keys use Ed25519 (EdDSA). The key is 64 raw bytes (base64):
    first 32 bytes = Ed25519 seed (private key), last 32 = public key.
    JWT claims: sub=key_id, iss="cdp", aud=["cdp_service"], uri="METHOD host/path".
    """
    import jwt
    from x402.http.facilitator_client_base import CreateHeadersAuthProvider
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    raw = base64.b64decode(private_key_b64)
    # First 32 bytes are the Ed25519 seed
    private_key = Ed25519PrivateKey.from_private_bytes(raw[:32])

    host = "api.cdp.coinbase.com"
    base_path = "/platform/v2/x402"

    def _make_token(method: str, path: str) -> str:
        now = int(time.time())
        payload = {
            "sub": key_id,
            "iss": "cdp",
            "aud": ["cdp_service"],
            "nbf": now,
            "exp": now + 120,
            "uri": f"{method} {host}{path}",
        }
        return jwt.encode(
            payload,
            private_key,
            algorithm="EdDSA",
            headers={"kid": key_id, "nonce": os.urandom(16).hex()},
        )

    def create_headers() -> dict[str, dict[str, str]]:
        return {
            "supported": {"Authorization": f"Bearer {_make_token('GET', base_path + '/supported')}"},
            "verify":    {"Authorization": f"Bearer {_make_token('POST', base_path + '/verify')}"},
            "settle":    {"Authorization": f"Bearer {_make_token('POST', base_path + '/settle')}"},
        }

    return CreateHeadersAuthProvider(create_headers)


def build_resource_server(settings: Settings) -> x402ResourceServer:
    """Create an x402 resource server with EVM payment verification."""
    auth_provider = None
    if settings.cdp_key_id and settings.cdp_private_key:
        auth_provider = _build_cdp_auth_provider(settings.cdp_key_id, settings.cdp_private_key)

    facilitator = HTTPFacilitatorClient(
        FacilitatorConfig(url=settings.facilitator_url, auth_provider=auth_provider)
    )
    server = x402ResourceServer(facilitator)
    server.register(settings.chain_network, ExactEvmServerScheme())
    return server


def build_route_config(settings: Settings, pricing: Pricing) -> dict[str, RouteConfig]:
    """Build x402 route config protecting the A2A JSON-RPC endpoint.

    The A2A protocol uses POST / for all task operations.
    Agent card at /.well-known/agent-card.json stays free.
    """
    return {
        "POST /": RouteConfig(
            accepts=[
                PaymentOption(
                    scheme="exact",
                    price=pricing.default_price,
                    network=settings.chain_network,
                    pay_to=settings.wallet_address,
                ),
            ],
            mime_type="application/json",
            description="A2A task execution",
        ),
    }
