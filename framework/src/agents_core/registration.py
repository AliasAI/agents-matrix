"""ERC-8004 on-chain agent registration via agent0-sdk."""

from __future__ import annotations

import logging
import sys

from agent0_sdk import SDK
from agent0_sdk.core.models import Endpoint, EndpointType
from web3.middleware import ExtraDataToPOAMiddleware

from agents_core.settings import Settings

# BSC PoA chain IDs that require ExtraDataToPOAMiddleware
_POA_CHAIN_IDS = {56, 97}  # BSC mainnet, BSC testnet

logger = logging.getLogger(__name__)


def register(
    settings: Settings,
    *,
    name: str,
    description: str,
    skills: list[str] | None = None,
    domains: list[str] | None = None,
    mcp_tools: list[str] | None = None,
    agent_id: str | None = None,
) -> None:
    """Register or update an agent on-chain (ERC-721 mint + IPFS metadata).

    Args:
        settings: Application settings (keys, RPC, etc.).
        name: Agent display name.
        description: Agent description for the registry.
        skills: OASF skill slugs (defaults to a generic pipeline skill).
        domains: OASF domain slugs (defaults to technology/blockchain).
        mcp_tools: MCP tool names to advertise in the IPFS services array.
            If provided, adds an MCP service entry pointing to settings.base_url.
        agent_id: Existing on-chain agent ID (e.g. "56:52001").
            If provided, loads the existing agent and updates its IPFS metadata
            instead of minting a new token.
    """
    if not settings.private_key:
        logger.error("AM_PRIVATE_KEY is required for registration")
        sys.exit(1)
    if not settings.rpc_url:
        logger.error("AM_RPC_URL is required for registration")
        sys.exit(1)
    if not settings.pinata_jwt:
        logger.error("AM_PINATA_JWT is required for registration")
        sys.exit(1)

    # agent0-sdk only has a handful of chains in DEFAULT_REGISTRIES.
    # The ERC-8004 contracts are deployed at the same addresses on every chain,
    # so we can supply them via registryOverrides for any unsupported chain.
    REGISTRY_ADDRESSES = {
        "IDENTITY":   "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
        "REPUTATION": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    }
    sdk = SDK(
        chainId=settings.chain_id,
        rpcUrl=settings.rpc_url,
        signer=settings.private_key,
        ipfs="pinata",
        pinataJwt=settings.pinata_jwt,
        registryOverrides={settings.chain_id: REGISTRY_ADDRESSES},
    )

    if agent_id:
        logger.info("Loading existing agent %s for update...", agent_id)
        agent = sdk.loadAgent(agent_id)
        agent.registration_file.name = name
        agent.registration_file.description = description
        # Clear existing endpoints so we rebuild them cleanly below
        agent.registration_file.endpoints = []
    else:
        agent = sdk.createAgent(name=name, description=description)

    # A2A endpoint — auto_fetch pulls a2aSkills from the live agent card
    a2a_url = settings.base_url + "/.well-known/agent-card.json"
    agent.setA2A(a2a_url)

    # MCP endpoint — added directly to the endpoints list so it appears in
    # the IPFS services array.  auto_fetch is disabled because MCP runs as
    # a stdio subprocess (no public HTTP MCP server); tools are supplied
    # explicitly via the mcp_tools parameter.
    if mcp_tools:
        mcp_ep = Endpoint(
            type=EndpointType.MCP,
            value=settings.base_url + "/",
            meta={"version": "2025-06-18", "mcpTools": mcp_tools},
        )
        agent.registration_file.endpoints.append(mcp_ep)
        logger.info("MCP endpoint registered with %d tools", len(mcp_tools))

    # OASF skills and domains
    for skill in (skills or ["data_engineering/data_transformation_pipeline"]):
        agent.addSkill(skill, validate_oasf=False)
    for domain in (domains or ["technology/blockchain"]):
        agent.addDomain(domain, validate_oasf=False)

    # Payment support — setX402Support is metadata (before registration)
    # setWallet requires agentId so must come after registerIPFS()
    agent.setX402Support(True)

    # Trust model
    agent.setTrust(reputation=True)
    agent.setActive(True)

    # On-chain metadata (stored as contract key-value, not in IPFS)
    agent.setMetadata({
        "version": "0.1.0",
        "framework": "agents-matrix",
        "payment_network": settings.chain_network,
    })

    # PoA chains (e.g. BSC) need extra middleware so web3.py doesn't choke
    # on the oversized extraData field in block headers.
    if settings.chain_id in _POA_CHAIN_IDS:
        sdk.web3_client.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        logger.info("Injected PoA middleware for chain %d", settings.chain_id)

    # Register on-chain (mint ERC-721 + upload metadata to IPFS)
    logger.info("Registering agent on chain %d...", settings.chain_id)
    reg_tx = agent.registerIPFS()
    confirmed = reg_tx.wait_confirmed(timeout=180)
    reg = confirmed.result

    logger.info("Agent registered!")
    logger.info("  TX Hash:   %s", confirmed.receipt.get("transactionHash", b"").hex())
    logger.info("  Agent ID:  %s", reg.agentId)
    logger.info("  Agent URI: %s", reg.agentURI)

    # setWallet must be called after registration (requires agentId)
    # wallet chain may differ from registration chain
    # (e.g. register on BSC but accept x402 payments on Base)
    if settings.wallet_address:
        # AM_CHAIN_NETWORK format: "eip155:<chain_id>" (x402 payment chain)
        try:
            payment_chain_id = int(settings.chain_network.split(":")[-1])
        except (ValueError, IndexError):
            payment_chain_id = settings.chain_id
        agent.setWallet(settings.wallet_address, chainId=payment_chain_id)
