"""
Experiment: Run sessions WITHOUT memory

Each session starts completely fresh. No cross-session knowledge.
This is the control — shows what happens without memory.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.orchestrator import Orchestrator


def load_scenarios():
    scenarios_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "scenarios.json"
    )
    with open(scenarios_path) as f:
        return json.load(f)["sessions"]


def run(session_range: tuple[int, int] | None = None) -> dict:
    """Run the no-memory experiment. Returns experiment summary.

    Args:
        session_range: Optional (start, end) inclusive range to filter sessions.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT: WITHOUT MEMORY")
    print("No memory system — each session is independent")
    if session_range:
        print(f"Session range: {session_range[0]}-{session_range[1]}")
    print("=" * 70)

    orchestrator = Orchestrator(
        memory_manager=None,
        experiment_name="without_memory",
    )

    scenarios = load_scenarios()
    if session_range:
        scenarios = [s for s in scenarios if session_range[0] <= s["id"] <= session_range[1]]
    for session in scenarios:
        try:
            result = orchestrator.run_session(
                task=session["task"],
                session_id=session["id"],
            )
        except Exception as e:
            print(f"  ERROR in session {session['id']}: {e}")
            import traceback
            traceback.print_exc()
            continue

    summary = orchestrator.get_experiment_summary()
    print(f"\nExperiment complete. Avg quality: {summary['avg_quality']}/10, "
          f"Total cost: ${summary['total_cost_usd']:.4f}")
    return summary


if __name__ == "__main__":
    run()
