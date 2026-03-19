"""Solana A2A Agent Service — entry point."""

from pathlib import Path

from agents_core.app import run_agent
from agents_core.settings import get_settings
from agent_config import SYSTEM_PROMPT, build_agent_card

if __name__ == "__main__":
    run_agent(
        agent_card=build_agent_card(get_settings()),
        mcp_module="mcp_entry",
        system_prompt=SYSTEM_PROMPT,
        log_name="solana-agent",
        pricing_path=Path(__file__).parent / "config" / "pricing.toml",
    )
