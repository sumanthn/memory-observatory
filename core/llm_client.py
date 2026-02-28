"""
LLM Client — OpenRouter API wrapper that LOGS EVERYTHING

Uses StepFun Step 3.5 Flash via OpenRouter (OpenAI-compatible API).
Every API call is fully traced: input tokens, output tokens, latency,
cost, and the complete prompt and response.
"""

import json
import os
import time
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import (
    MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    OPENROUTER_BASE_URL,
    OPENROUTER_APP_NAME,
)
from tracking.token_tracker import estimate_tokens
from tracking.cost_calculator import calculate_cost

try:
    from openai import OpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class LLMClient:
    def __init__(self, experiment_name: str = "", session_id: int = 0):
        self.experiment_name = experiment_name
        self.session_id = session_id
        self.call_count = 0
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        self.cumulative_cost = 0.0

        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if HAS_OPENAI and api_key:
            self.client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=api_key,
            )
        else:
            self.client = None
            if not HAS_OPENAI:
                print("  [LLM] openai package not installed — running in mock mode")
            elif not api_key:
                print("  [LLM] OPENROUTER_API_KEY not set — running in mock mode")

    def set_session(self, session_id: int):
        self.session_id = session_id

    def call(
        self,
        messages: list[dict],
        system: str = "",
        tools: list[dict] | None = None,
        metadata: dict | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """
        Call the LLM via OpenRouter and return a fully-traced response.

        Args:
            messages: List of message dicts (role + content)
            system: System prompt (will be prepended as a system message)
            tools: Tool definitions (OpenAI format)
            metadata: Additional metadata (e.g., purpose)
            max_tokens: Override MAX_TOKENS for this call (e.g. for consolidation)

        Returns:
            dict with:
                - content: response text
                - input_tokens: int
                - output_tokens: int
                - cost_usd: float
                - latency_ms: float
                - tool_use: dict or None
                - stop_reason: str
        """
        self.call_count += 1
        start_time = time.perf_counter()
        self._max_tokens_override = max_tokens

        if self.client:
            result = self._call_api(messages, system, tools)
        else:
            result = self._call_mock(messages, system, tools)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Track tokens and cost
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)
        cost = calculate_cost(input_tokens, output_tokens)

        self.cumulative_input_tokens += input_tokens
        self.cumulative_output_tokens += output_tokens
        self.cumulative_cost += cost["total_cost_usd"]

        result["latency_ms"] = round(elapsed_ms, 2)
        result["cost_usd"] = cost["total_cost_usd"]
        result["cost_breakdown"] = cost
        result["cumulative_cost_usd"] = round(self.cumulative_cost, 6)
        result["call_number"] = self.call_count
        result["metadata"] = metadata or {}

        return result

    def _call_api(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict] | None,
    ) -> dict:
        """Call the actual LLM via OpenRouter (OpenAI-compatible API)."""

        # Build message list with system prompt first
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})
        api_messages.extend(messages)

        effective_max_tokens = getattr(self, '_max_tokens_override', None) or MAX_TOKENS
        kwargs = {
            "model": MODEL,
            "max_tokens": effective_max_tokens,
            "temperature": TEMPERATURE,
            "messages": api_messages,
            "extra_headers": {
                "X-OpenRouter-Title": OPENROUTER_APP_NAME,
            },
        }

        # Add tools if provided (OpenAI format)
        if tools:
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("input_schema", tool.get("parameters", {})),
                    },
                })
            kwargs["tools"] = openai_tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            print(f"  [LLM] API error: {e}")
            # Fallback to mock on API error
            return self._call_mock(messages, system, tools)

        # Extract content and tool calls
        choice = response.choices[0] if response.choices else None
        content_text = ""
        tool_use = None
        stop_reason = "end_turn"

        if choice:
            msg = choice.message
            content_text = msg.content or ""
            stop_reason = choice.finish_reason or "end_turn"

            # Warn when output is truncated — often causes silent failures
            if not content_text and stop_reason == "length":
                print(f"  [LLM] WARNING: Empty content with stop_reason=length "
                      f"(max_tokens={effective_max_tokens}). "
                      f"Model may need a higher output token limit.")

            # Check for tool calls
            if msg.tool_calls:
                tc = msg.tool_calls[0]  # Take the first tool call
                try:
                    tool_args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    tool_args = tc.function.arguments
                tool_use = {
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": tool_args,
                }

        # Extract token usage
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else estimate_tokens(system + " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str)))
        output_tokens = usage.completion_tokens if usage else estimate_tokens(content_text)

        return {
            "content": content_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tool_use": tool_use,
            "stop_reason": stop_reason,
        }

    def _call_mock(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict] | None,
    ) -> dict:
        """
        Mock LLM call for testing without API access.
        Estimates token counts from the prompt and returns a placeholder.
        """
        all_text = system + " " + " ".join(
            m.get("content", "")
            if isinstance(m.get("content"), str)
            else str(m.get("content", ""))
            for m in messages
        )
        input_tokens = estimate_tokens(all_text)

        content = (
            "Thought: I need to gather more information to complete this analysis.\n"
            "Action: final_answer\n"
            "Action Input: This is a mock response. "
            "Install 'openai' package and set OPENROUTER_API_KEY "
            "to run with the actual Step 3.5 Flash model via OpenRouter."
        )
        output_tokens = estimate_tokens(content)

        return {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tool_use": None,
            "stop_reason": "end_turn",
        }

    def get_stats(self) -> dict:
        return {
            "total_calls": self.call_count,
            "cumulative_input_tokens": self.cumulative_input_tokens,
            "cumulative_output_tokens": self.cumulative_output_tokens,
            "cumulative_cost_usd": round(self.cumulative_cost, 6),
        }
