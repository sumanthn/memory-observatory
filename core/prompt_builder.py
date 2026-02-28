"""
Prompt Builder — Assembles the full prompt for each LLM call

Key design principle: Each section is assembled and measured separately
so we can see exactly how many tokens MEMORY consumes vs HISTORY vs
TOOLS vs IDENTITY.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import AGENT_IDENTITY
from tracking.token_tracker import estimate_tokens


SYSTEM_TEMPLATE = """{identity}

{memories_section}

{working_memory_section}

Instructions:
- Think step by step about what information you need
- Use the provided tools to gather data — do not make up numbers
- Use financial_lookup to get specific metrics, sec_filing to read SEC filings, news_search for news, and calculate for math
- Be thorough: check financial metrics, read SEC filings for red flags, and review news
- When you have gathered sufficient data, provide your complete analysis directly as text
- Your final analysis should include: key financial metrics, strengths, risks, red flags found, and an investment recommendation"""


def build_prompt(
    retrieved_memories: list[dict],
    working_memory_text: str,
    conversation_history: list[dict],
    current_observation: str,
    tool_definitions: str,
    task: str,
) -> tuple[list[dict], dict]:
    """
    Assemble the prompt from components and return both the messages
    and metadata about token allocation.

    Returns:
        - messages: list of message dicts for Claude API
        - metadata: per-section token counts
    """
    # Build each section
    identity = AGENT_IDENTITY

    memories_section = _build_memories_section(retrieved_memories)
    working_section = working_memory_text if working_memory_text else ""

    system_prompt = SYSTEM_TEMPLATE.format(
        identity=identity,
        memories_section=memories_section,
        working_memory_section=working_section,
        tool_definitions=tool_definitions,
    )

    # Build messages
    messages = []

    # Add conversation history
    for msg in conversation_history:
        messages.append(msg)

    # Add current turn
    if current_observation:
        # This is a tool result being fed back
        user_content = f"Current task: {task}\n\nObservation: {current_observation}"
    else:
        # First turn
        user_content = f"Task: {task}"

    messages.append({"role": "user", "content": user_content})

    # Compute per-section token counts
    memory_tokens = estimate_tokens(memories_section)
    history_text = " ".join(
        m.get("content", "") for m in conversation_history if isinstance(m.get("content"), str)
    )

    metadata = {
        "system_tokens": estimate_tokens(identity),
        "memory_tokens": memory_tokens,
        "memory_items_included": [
            {
                "type": m.get("memory_type", "unknown"),
                "content_preview": m.get("content", "")[:100],
                "score": m.get("score", 0),
                "source_session": m.get("source_session") or m.get("session_id"),
            }
            for m in retrieved_memories
        ],
        "working_memory_tokens": estimate_tokens(working_section),
        "history_tokens": estimate_tokens(history_text),
        "tool_tokens": estimate_tokens(tool_definitions),
        "task_tokens": estimate_tokens(user_content),
        "total_tokens": estimate_tokens(system_prompt + " " + user_content + " " + history_text),
    }

    return system_prompt, messages, metadata


def _build_memories_section(memories: list[dict]) -> str:
    """Format retrieved memories for prompt injection."""
    if not memories:
        return "No relevant memories from prior sessions."

    lines = ["=== Relevant Memories from Prior Sessions ==="]

    # Group by type for clarity
    by_type = {}
    for mem in memories:
        mem_type = mem.get("memory_type", "unknown")
        by_type.setdefault(mem_type, []).append(mem)

    type_labels = {
        "episodic": "Past Experiences",
        "semantic": "Known Facts",
        "procedural": "Learned Strategies",
        "reflective": "Lessons & Insights",
    }

    for mem_type, items in by_type.items():
        label = type_labels.get(mem_type, mem_type.title())
        lines.append(f"\n[{label}]")
        for item in items:
            content = item.get("content", "")
            source = item.get("source_session") or item.get("session_id", "?")
            lines.append(f"  (from session {source}) {content}")

    lines.append("")
    return "\n".join(lines)
