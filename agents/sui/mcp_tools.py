"""MCP server exposing Sui blockchain queries via sui client CLI (direct subprocess).

Community usage: claude mcp add sui -- uv run python -m mcp_entry
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
    "sui",
    instructions=(
        "Sui blockchain tools for object queries, balance checks, "
        "transaction lookups, and network info. "
        "Supports mainnet, devnet, and testnet environments."
    ),
)

SUI_BIN = os.environ.get("AM_SUI_BIN", shutil.which("sui") or "sui")

_envs: ChainRegistry | None = None


def _get_envs() -> ChainRegistry:
    global _envs
    if _envs is None:
        _envs = ChainRegistry(
            Path(__file__).parent / "config" / "envs.toml"
        )
    return _envs


def _resolve_env(env: str | None) -> str:
    """Resolve env slug to RPC URL via ChainRegistry."""
    return _get_envs().resolve_rpc(env)


def _run_cli(
    *args: str, url: str | None = None,
) -> dict | list | str:
    """Run sui client with --json flag and return parsed output."""
    cmd = [SUI_BIN, "client", *args, "--json"]
    if url:
        cmd.extend(["--url", url])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"sui CLI error: {result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


# -- Environment Discovery --


@mcp.tool()
def list_supported_envs() -> list[dict]:
    """List all supported Sui environments and whether they have an RPC URL configured."""
    return _get_envs().list_chains()


# -- Object --


@mcp.tool()
def get_object(object_id: str, env: str | None = None) -> dict | str:
    """Get full object details by ID — type, owner, version, content.

    Args:
        object_id: Sui object ID (hex string starting with 0x).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("object", object_id, url=url)


@mcp.tool()
def get_objects(address: str, env: str | None = None) -> list | str:
    """List all objects owned by an address.

    Args:
        address: Sui address (hex string starting with 0x).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("objects", "--address", address, url=url)


# -- Balance / Gas --


@mcp.tool()
def get_balance(address: str, env: str | None = None) -> dict | str:
    """Get SUI token balance for an address.

    Args:
        address: Sui address (hex string starting with 0x).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("balance", "--address", address, url=url)


@mcp.tool()
def get_gas(address: str, env: str | None = None) -> list | str:
    """List gas coins owned by an address with amounts.

    Args:
        address: Sui address (hex string starting with 0x).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("gas", "--address", address, url=url)


# -- Transaction --


@mcp.tool()
def get_tx_block(digest: str, env: str | None = None) -> dict | str:
    """Get transaction block details by digest — status, gas cost, effects, events.

    Args:
        digest: Transaction digest (base58 string).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("tx-block", digest, url=url)


# -- Dynamic Fields --


@mcp.tool()
def get_dynamic_field(
    object_id: str, env: str | None = None,
) -> dict | str:
    """Get dynamic fields for a parent object.

    Args:
        object_id: Parent object ID (hex string starting with 0x).
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("dynamic-field", object_id, url=url)


# -- Network Info --


@mcp.tool()
def get_chain_id(env: str | None = None) -> dict | str:
    """Get the chain identifier for the current environment.

    Args:
        env: Environment (mainnet, devnet, testnet). Defaults to configured default.
    """
    url = _resolve_env(env)
    return _run_cli("chain-identifier", url=url)


@mcp.tool()
def list_envs() -> dict | str:
    """List all environments configured in the local sui client config."""
    cmd = [SUI_BIN, "client", "envs", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(
            f"sui CLI error: {result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()
