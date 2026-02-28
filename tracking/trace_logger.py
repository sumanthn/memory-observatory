"""
Trace Logger — Full trace of every LLM call

Writes one JSON file per LLM call, organized by experiment/session.
Also writes session summaries and experiment summaries.
"""

import json
import os
import uuid
from datetime import datetime


class TraceLogger:
    def __init__(self, output_dir: str = "output/traces"):
        self.output_dir = output_dir
        self.traces = []  # All traces for the current experiment
        self.experiment_name = ""
        self.current_session = 0

    def set_experiment(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.traces = []

    def set_session(self, session_id: int):
        self.current_session = session_id

    def log_call(
        self,
        step: int,
        prompt_metadata: dict,
        response_content: str,
        response_metadata: dict,
        cost: dict,
        memory_items: list[dict] | None = None,
    ) -> dict:
        """
        Log a single LLM call with full trace information.

        Args:
            step: Step number within the current session
            prompt_metadata: Token counts and breakdown from prompt_builder
            response_content: Full response text
            response_metadata: Output tokens, action parsed, latency, etc.
            cost: Cost breakdown from cost_calculator
            memory_items: List of memory items included in this call

        Returns:
            The trace dict (also saved to file)
        """
        trace = {
            "call_id": str(uuid.uuid4()),
            "experiment": self.experiment_name,
            "session": self.current_session,
            "step": step,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": {
                "system_tokens": prompt_metadata.get("system_tokens", 0),
                "memory_tokens": prompt_metadata.get("memory_tokens", 0),
                "memory_items": self._format_memory_items(memory_items),
                "conversation_history_tokens": prompt_metadata.get(
                    "history_tokens", 0
                ),
                "tool_definitions_tokens": prompt_metadata.get("tool_tokens", 0),
                "task_context_tokens": prompt_metadata.get("task_tokens", 0),
                "working_memory_tokens": prompt_metadata.get(
                    "working_memory_tokens", 0
                ),
                "total_input_tokens": prompt_metadata.get("total_tokens", 0),
            },
            "response": {
                "content": response_content,
                "output_tokens": response_metadata.get("output_tokens", 0),
                "action": response_metadata.get("action"),
                "is_final_answer": response_metadata.get("is_final_answer", False),
                "latency_ms": response_metadata.get("latency_ms", 0),
            },
            "cost": {
                "input_cost_usd": cost.get("input_cost_usd", 0),
                "output_cost_usd": cost.get("output_cost_usd", 0),
                "total_cost_usd": cost.get("total_cost_usd", 0),
                "cumulative_session_cost_usd": cost.get("session_cost_usd", 0),
                "cumulative_experiment_cost_usd": cost.get("cumulative_cost_usd", 0),
            },
        }

        self.traces.append(trace)
        self._write_trace(trace)
        return trace

    def save_session_summary(self, session_id: int, summary: dict):
        """Write a session summary JSON."""
        dir_path = os.path.join(
            self.output_dir, self.experiment_name, f"session_{session_id}"
        )
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, "summary.json")
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)

    def save_experiment_summary(self, summary: dict):
        """Write an experiment-level summary JSON."""
        dir_path = os.path.join(self.output_dir, self.experiment_name)
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, "experiment_summary.json")
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)

    def get_session_traces(self, session_id: int) -> list[dict]:
        return [t for t in self.traces if t["session"] == session_id]

    def get_all_traces(self) -> list[dict]:
        return self.traces.copy()

    def _write_trace(self, trace: dict):
        """Write a single trace to its own JSON file."""
        dir_path = os.path.join(
            self.output_dir,
            self.experiment_name,
            f"session_{trace['session']}",
        )
        os.makedirs(dir_path, exist_ok=True)
        filename = f"step_{trace['step']:03d}_{trace['call_id'][:8]}.json"
        path = os.path.join(dir_path, filename)
        with open(path, "w") as f:
            json.dump(trace, f, indent=2)

    def _format_memory_items(self, items: list[dict] | None) -> list[dict]:
        """Format memory items for trace (strip embeddings, keep metadata)."""
        if not items:
            return []
        formatted = []
        for item in items:
            formatted.append(
                {
                    "type": item.get("memory_type", "unknown"),
                    "content": item.get("content", "")[:200],
                    "source_session": item.get("source_session")
                    or item.get("session_id"),
                    "retrieval_score": item.get("score", 0),
                }
            )
        return formatted
