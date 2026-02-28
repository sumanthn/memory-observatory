"""
Latency Tracker — Measures time per LLM call and per step

Records per-call and cumulative latency for transparency.
"""

import time
from contextlib import contextmanager


class LatencyTracker:
    """Tracks timing for LLM calls and overall session execution."""

    def __init__(self):
        self.calls = []
        self.cumulative_ms = 0.0

    @contextmanager
    def track(self):
        """
        Context manager for timing an operation.

        Usage:
            with latency_tracker.track() as timer:
                result = llm_client.call(...)
            elapsed_ms = timer.elapsed_ms
        """
        timer = _Timer()
        timer.start()
        try:
            yield timer
        finally:
            timer.stop()
            self.cumulative_ms += timer.elapsed_ms
            self.calls.append(
                {
                    "latency_ms": round(timer.elapsed_ms, 2),
                    "cumulative_ms": round(self.cumulative_ms, 2),
                }
            )

    def record(self, latency_ms: float):
        """Manually record a latency measurement."""
        self.cumulative_ms += latency_ms
        self.calls.append(
            {
                "latency_ms": round(latency_ms, 2),
                "cumulative_ms": round(self.cumulative_ms, 2),
            }
        )

    def get_summary(self) -> dict:
        latencies = [c["latency_ms"] for c in self.calls]
        return {
            "total_calls": len(self.calls),
            "total_latency_ms": round(self.cumulative_ms, 2),
            "avg_latency_ms": (
                round(sum(latencies) / len(latencies), 2) if latencies else 0
            ),
            "min_latency_ms": round(min(latencies), 2) if latencies else 0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0,
            "calls": self.calls,
        }


class _Timer:
    """Simple timer helper for the context manager."""

    def __init__(self):
        self._start = 0.0
        self._end = 0.0
        self.elapsed_ms = 0.0

    def start(self):
        self._start = time.perf_counter()

    def stop(self):
        self._end = time.perf_counter()
        self.elapsed_ms = (self._end - self._start) * 1000
