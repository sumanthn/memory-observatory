"""
Experiment: Run with ONLY episodic memory

Tests whether raw recall is enough vs higher-level memory types.
Only episodic store is enabled — no procedural learning, no reflective
insights, no semantic fact extraction.
"""


import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager


def load_scenarios():
    scenarios_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "scenarios.json"
    )
    with open(scenarios_path) as f:
        return json.load(f)["sessions"]


def snapshot_memory_db(session_id: int, experiment_name: str, db_path: str):
    """Copy the memory DB after each session for later analysis."""
    snapshot_dir = os.path.join("output", "memories", experiment_name)
    os.makedirs(snapshot_dir, exist_ok=True)
    snapshot_path = os.path.join(
        snapshot_dir, f"memory_after_session_{session_id}.db"
    )
    shutil.copy2(db_path, snapshot_path)


def run(session_range: tuple[int, int] | None = None) -> dict:
    """Run the episodic-only experiment. Returns experiment summary.

    Args:
        session_range: Optional (start, end) inclusive range to filter sessions.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT: PARTIAL MEMORY (Episodic Only)")
    print("Only episodic memory — raw recall without higher-level learning")
    if session_range:
        print(f"Session range: {session_range[0]}-{session_range[1]}")
    print("=" * 70)

    db_path = os.path.join("output", "memories", "partial_memory.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Only remove old DB if starting from session 1 (or no range specified)
    if os.path.exists(db_path) and (session_range is None or session_range[0] == 1):
        os.remove(db_path)

    memory_manager = MemoryManager(
        db_path=db_path,
        enabled_stores=["episodic"],  # Only episodic
    )

    orchestrator = Orchestrator(
        memory_manager=memory_manager,
        experiment_name="partial_memory",
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
            snapshot_memory_db(session["id"], "partial_memory", db_path)
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
