"""MCP server exposing Foundry cast operations via cli-anything-cast CLI.

Community usage: claude mcp add cast -- uv run python -m mcp_server
"""

from __future__ import annotations

import json
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cast", instructions="Foundry cast tools for Ethereum transaction analysis, decoding, and block queries.")


def _run_cli(*args: str) -> str | dict | list:
    """Run cli-anything-cast with --json flag and return parsed output.

    For commands that return JSON, parses and returns dict/list.
    For plain-text commands (4byte-decode, sig, call, trace), returns
    the structured dict that the harness wraps around the text output.
    """
    cmd = ["cli-anything-cast", "--json", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout)


# ── Transaction ──


@mcp.tool()
def get_transaction(tx_hash: str, rpc_url: str | None = None) -> dict:
    """Get full transaction details by hash (from, to, value, gas, input data, etc.).

    Args:
        tx_hash: The transaction hash to look up.
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    args = ["tx", "info", tx_hash]
    if rpc_url:
        args = ["-r", rpc_url] + args
    return _run_cli(*args)


@mcp.tool()
def get_receipt(tx_hash: str, rpc_url: str | None = None) -> dict:
    """Get transaction receipt (status, gas used, logs, contract address, etc.).

    Args:
        tx_hash: The transaction hash to look up.
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    args = ["receipt", "info", tx_hash]
    if rpc_url:
        args = ["-r", rpc_url] + args
    return _run_cli(*args)


# ── Trace ──


@mcp.tool()
def trace_transaction(tx_hash: str, rpc_url: str | None = None) -> dict:
    """Trace a transaction execution showing internal calls and gas usage.

    Args:
        tx_hash: The transaction hash to trace.
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    args = ["decode", "trace", tx_hash]
    if rpc_url:
        args = ["-r", rpc_url] + args
    return _run_cli(*args)


# ── Decode ──


@mcp.tool()
def decode_calldata(calldata: str) -> dict:
    """Decode hex calldata using the 4byte signature database (no RPC needed).

    Args:
        calldata: Hex-encoded calldata starting with 0x (e.g. "0xa9059cbb...").
    """
    return _run_cli("decode", "calldata", calldata)


@mcp.tool()
def get_selector(signature: str) -> dict:
    """Get the 4-byte function selector for a Solidity function signature (no RPC needed).

    Args:
        signature: Function signature string (e.g. "transfer(address,uint256)").
    """
    return _run_cli("decode", "sig", signature)


# ── Logs ──


@mcp.tool()
def query_logs(
    address: str,
    sig: str | None = None,
    from_block: str | None = None,
    to_block: str | None = None,
    rpc_url: str | None = None,
) -> list:
    """Query event logs from a contract address with optional filters.

    Args:
        address: Contract address to query logs from.
        sig: Event signature to filter (e.g. "Transfer(address,address,uint256)").
        from_block: Starting block number or tag.
        to_block: Ending block number or tag.
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    args = ["logs", "query", address]
    if sig:
        args.extend(["--sig", sig])
    if from_block:
        args.extend(["--from-block", from_block])
    if to_block:
        args.extend(["--to-block", to_block])
    if rpc_url:
        args = ["-r", rpc_url] + args
    return _run_cli(*args)


# ── Call ──


@mcp.tool()
def call_contract(
    to: str,
    sig: str,
    args: list[str] | None = None,
    rpc_url: str | None = None,
) -> dict:
    """Call a contract function (read-only, no state change).

    Args:
        to: Target contract address.
        sig: Function signature (e.g. "balanceOf(address)").
        args: Function arguments.
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    cmd_args = ["decode", "call", to, sig]
    if args:
        cmd_args.extend(args)
    if rpc_url:
        cmd_args = ["-r", rpc_url] + cmd_args
    return _run_cli(*cmd_args)


# ── Block ──


@mcp.tool()
def get_block(block: str = "latest", rpc_url: str | None = None) -> dict:
    """Get block information by number, hash, or tag (latest, earliest, etc.).

    Args:
        block: Block number, hash, or tag. Defaults to "latest".
        rpc_url: Ethereum RPC URL. Falls back to ETH_RPC_URL or AM_DEFAULT_RPC_URL env.
    """
    args = ["block", "info", block]
    if rpc_url:
        args = ["-r", rpc_url] + args
    return _run_cli(*args)
