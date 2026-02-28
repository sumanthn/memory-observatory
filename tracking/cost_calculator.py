"""
Cost Calculator — Computes dollar cost per LLM call

Uses rates from settings.py. Tracks per-call and cumulative costs.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import INPUT_COST_PER_1K, OUTPUT_COST_PER_1K


def calculate_cost(input_tokens: int, output_tokens: int) -> dict:
    """
    Calculate cost for a single LLM call.

    Returns:
        dict with input_cost_usd, output_cost_usd, total_cost_usd
    """
    input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K
    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
    }


class CostCalculator:
    """Tracks cumulative costs across an experiment."""

    def __init__(self):
        self.calls = []
        self.cumulative_cost = 0.0
        self.session_costs = {}  # session_id -> cumulative cost

    def record(
        self,
        input_tokens: int,
        output_tokens: int,
        session_id: int = 0,
    ) -> dict:
        """Record cost for a single call. Returns the cost breakdown."""
        cost = calculate_cost(input_tokens, output_tokens)
        self.cumulative_cost += cost["total_cost_usd"]

        if session_id not in self.session_costs:
            self.session_costs[session_id] = 0.0
        self.session_costs[session_id] += cost["total_cost_usd"]

        record = {
            **cost,
            "cumulative_cost_usd": round(self.cumulative_cost, 6),
            "session_cost_usd": round(self.session_costs[session_id], 6),
            "session_id": session_id,
        }
        self.calls.append(record)
        return record

    def get_summary(self) -> dict:
        return {
            "total_calls": len(self.calls),
            "total_cost_usd": round(self.cumulative_cost, 6),
            "session_costs": {
                k: round(v, 6) for k, v in self.session_costs.items()
            },
            "calls": self.calls,
        }
