"""
Token Tracker — Counts tokens per section of the prompt

Uses a simple estimation: split by whitespace, multiply by 1.3.
This is rough but sufficient for a prototype — real token counting
would require the anthropic tokenizer.
"""


def estimate_tokens(text: str) -> int:
    """Estimate token count for a text string."""
    if not text:
        return 0
    return int(len(text.split()) * 1.3)


def count_section_tokens(sections: dict[str, str]) -> dict[str, int]:
    """
    Count tokens for each named section of a prompt.

    Args:
        sections: Dict mapping section names to their text content.
                  e.g. {"system": "...", "memory": "...", "history": "..."}

    Returns:
        Dict mapping section names to token counts, plus 'total'.
    """
    counts = {}
    total = 0
    for name, text in sections.items():
        count = estimate_tokens(text)
        counts[name] = count
        total += count
    counts["total"] = total
    return counts


class TokenTracker:
    """Tracks cumulative token usage across calls."""

    def __init__(self):
        self.calls = []
        self.cumulative_input = 0
        self.cumulative_output = 0

    def record(
        self,
        input_tokens: int,
        output_tokens: int,
        section_breakdown: dict[str, int] | None = None,
    ):
        """Record a single LLM call's token usage."""
        self.cumulative_input += input_tokens
        self.cumulative_output += output_tokens
        self.calls.append(
            {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cumulative_input": self.cumulative_input,
                "cumulative_output": self.cumulative_output,
                "section_breakdown": section_breakdown or {},
            }
        )

    def get_summary(self) -> dict:
        return {
            "total_calls": len(self.calls),
            "total_input_tokens": self.cumulative_input,
            "total_output_tokens": self.cumulative_output,
            "total_tokens": self.cumulative_input + self.cumulative_output,
            "calls": self.calls,
        }
