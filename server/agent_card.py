"""Build the A2A AgentCard with Cast transaction analysis skill definitions."""

from __future__ import annotations

from a2a.types import AgentCard, AgentSkill, AgentCapabilities

from config.settings import get_settings


SKILLS: list[AgentSkill] = [
    AgentSkill(
        id="tx_decode",
        name="Decode Transaction",
        description="Fetch and decode a transaction by hash — shows from, to, value, gas, and input data.",
        tags=["transaction", "decode", "ethereum", "web3"],
        examples=[
            "Decode transaction 0xabc123...",
            "What did this transaction do?",
        ],
    ),
    AgentSkill(
        id="receipt_parse",
        name="Parse Receipt",
        description="Get transaction receipt with status, gas usage analysis, and emitted event logs.",
        tags=["receipt", "gas", "logs", "ethereum"],
        examples=[
            "Show me the receipt for tx 0xabc123...",
            "How much gas did this transaction use?",
        ],
    ),
    AgentSkill(
        id="trace",
        name="Trace Transaction",
        description="Trace the full execution of a transaction showing internal calls and state changes.",
        tags=["trace", "debug", "execution", "ethereum"],
        examples=[
            "Trace the execution of tx 0xabc123...",
            "Show internal calls for this transaction",
        ],
    ),
    AgentSkill(
        id="calldata_decode",
        name="Decode Calldata",
        description="Decode hex-encoded calldata using the 4byte signature database (no RPC needed).",
        tags=["calldata", "decode", "4byte", "selector"],
        examples=[
            "Decode this calldata: 0xa9059cbb...",
            "What function does selector 0xa9059cbb call?",
        ],
    ),
    AgentSkill(
        id="log_query",
        name="Query Logs",
        description="Query event logs from a contract address with optional topic and block range filters.",
        tags=["logs", "events", "contract", "ethereum"],
        examples=[
            "Show Transfer events from USDC contract",
            "Query logs from 0x1234... in the last 100 blocks",
        ],
    ),
    AgentSkill(
        id="block_info",
        name="Block Info",
        description="Get block details by number, hash, or tag (latest, earliest, etc.).",
        tags=["block", "chain", "ethereum"],
        examples=[
            "Show me the latest block",
            "Get info for block 18000000",
        ],
    ),
]


def build_agent_card() -> AgentCard:
    settings = get_settings()
    return AgentCard(
        name="Cast Transaction Agent",
        description=(
            "Paid AI agent for Ethereum transaction analysis — decode transactions, "
            "parse receipts, trace execution, query logs, and inspect blocks. "
            "Powered by Foundry cast. Accepts USDC payment via x402 protocol."
        ),
        url=settings.base_url + "/",
        version="0.1.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        skills=SKILLS,
    )
