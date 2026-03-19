"""MCP server exposing Solana blockchain queries via solana CLI (direct subprocess).

Community usage: claude mcp add solana -- uv run python -m mcp_entry
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from agents_core.settings import ChainRegistry

mcp = FastMCP(
    "solana",
    instructions=(
        "Solana blockchain tools for account queries, transaction lookups, "
        "block inspection, epoch info, validator status, and supply data. "
        "Supports mainnet-beta, devnet, and testnet clusters."
    ),
)

SOLANA_BIN = os.environ.get(
    "AM_SOLANA_BIN", shutil.which("solana") or "solana"
)

_clusters: ChainRegistry | None = None


def _get_clusters() -> ChainRegistry:
    global _clusters
    if _clusters is None:
        _clusters = ChainRegistry(
            Path(__file__).parent / "config" / "clusters.toml"
        )
    return _clusters


def _run_cli(*args: str, url: str | None = None) -> dict | list | str:
    """Run solana CLI with --output json and return parsed output."""
    cmd = [SOLANA_BIN, *args, "--output", "json"]
    if url:
        cmd.extend(["--url", url])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"solana CLI error: {result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


def _resolve_cluster(cluster: str | None) -> str:
    """Resolve cluster slug to RPC URL via ChainRegistry."""
    return _get_clusters().resolve_rpc(cluster)


# -- Cluster Discovery --


@mcp.tool()
def list_supported_clusters() -> list[dict]:
    """List all supported Solana clusters and whether they have an RPC URL configured."""
    return _get_clusters().list_chains()


# -- Account --


@mcp.tool()
def get_account(address: str, cluster: str | None = None) -> dict | str:
    """Get full account details — balance, owner, data size, executable flag.

    Args:
        address: Solana account public key (base58).
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("account", address, url=url)


@mcp.tool()
def get_balance(address: str, cluster: str | None = None) -> dict | str:
    """Get SOL balance for an address.

    Args:
        address: Solana account public key (base58).
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("balance", address, url=url)


# -- Transaction --


@mcp.tool()
def confirm_transaction(
    signature: str, cluster: str | None = None,
) -> dict | str:
    """Check if a transaction has been confirmed.

    Args:
        signature: Transaction signature (base58).
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("confirm", signature, url=url)


@mcp.tool()
def get_transaction_history(
    address: str, cluster: str | None = None,
) -> dict | str:
    """Get recent transaction history for an address.

    Args:
        address: Solana account public key (base58).
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("transaction-history", address, url=url)


# -- Block --


@mcp.tool()
def get_block(slot: int, cluster: str | None = None) -> dict | str:
    """Get block information by slot number.

    Args:
        slot: Block slot number.
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("block", str(slot), url=url)


@mcp.tool()
def get_slot(cluster: str | None = None) -> dict | str:
    """Get the current slot number.

    Args:
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("slot", url=url)


# -- Network / Epoch --


@mcp.tool()
def get_epoch_info(cluster: str | None = None) -> dict | str:
    """Get current epoch information — epoch number, slot index, slots remaining.

    Args:
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("epoch-info", url=url)


@mcp.tool()
def get_supply(cluster: str | None = None) -> dict | str:
    """Get total and circulating SOL supply.

    Args:
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("supply", url=url)


# -- Validators / Staking --


@mcp.tool()
def get_validators(cluster: str | None = None) -> dict | str:
    """List current validators with stake, commission, and version info.

    Args:
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("validators", url=url)


@mcp.tool()
def get_stake_account(
    address: str, cluster: str | None = None,
) -> dict | str:
    """Get stake account details — delegation, activation epoch, stake amount.

    Args:
        address: Stake account public key (base58).
        cluster: Cluster name (mainnet_beta, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_cluster(cluster)
    return _run_cli("stake-account", address, url=url)
