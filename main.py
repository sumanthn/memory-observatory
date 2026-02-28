#!/usr/bin/env python3
"""
Memory Observatory — Main Entry Point

Runs agent memory experiments and generates comparison reports.

Usage:
    python main.py                                              # Run all experiments
    python main.py --experiment with_memory                     # Run only full memory
    python main.py --experiment with_memory --sessions 1-10     # Run sessions 1-10 only
    python main.py --experiment without_memory --sessions 51-75 # Run subset
    python main.py --compare-only                               # Regenerate report
"""

import argparse
import os
import sys

# Ensure we can import from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.run_with_memory import run as run_with_memory
from experiments.run_without_memory import run as run_without_memory
from experiments.run_partial_memory import run as run_partial_memory
from experiments.compare_results import run as run_comparison


def parse_session_range(value: str) -> tuple[int, int]:
    """Parse a session range like '1-50' or '10' into (start, end) inclusive."""
    if "-" in value:
        parts = value.split("-", 1)
        return int(parts[0]), int(parts[1])
    n = int(value)
    return n, n


def main():
    parser = argparse.ArgumentParser(
        description="Memory Observatory — Agent Memory Experiments"
    )
    parser.add_argument(
        "--experiment",
        choices=["all", "with_memory", "without_memory", "partial_memory"],
        default="all",
        help="Which experiment to run (default: all)",
    )
    parser.add_argument(
        "--sessions",
        type=str,
        default=None,
        help="Session range to run, e.g. '1-50' or '11-20' (default: all sessions)",
    )
    parser.add_argument(
        "--compare-only",
        action="store_true",
        help="Skip experiments, just regenerate the comparison report",
    )
    args = parser.parse_args()

    session_range = None
    if args.sessions:
        session_range = parse_session_range(args.sessions)

    # Set working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if args.compare_only:
        run_comparison()
        return

    print("╔══════════════════════════════════════════════════╗")
    print("║         MEMORY OBSERVATORY                      ║")
    print("║  Transparent Agent Memory Experiments            ║")
    print("╚══════════════════════════════════════════════════╝")

    summaries = {}

    if args.experiment in ("all", "without_memory"):
        summaries["without_memory"] = run_without_memory(session_range=session_range)

    if args.experiment in ("all", "partial_memory"):
        summaries["partial_memory"] = run_partial_memory(session_range=session_range)

    if args.experiment in ("all", "with_memory"):
        summaries["with_memory"] = run_with_memory(session_range=session_range)

    # Generate comparison report
    if len(summaries) > 1 or args.experiment == "all":
        run_comparison(summaries)

    print("\n╔══════════════════════════════════════════════════╗")
    print("║  ALL EXPERIMENTS COMPLETE                        ║")
    print("║                                                  ║")
    print("║  Results:                                        ║")
    print("║    output/report.md          — Comparison report  ║")
    print("║    output/dashboard_data.json — Dashboard data    ║")
    print("║    output/traces/            — Full LLM traces    ║")
    print("║    output/memories/          — Memory snapshots   ║")
    print("║    output/costs/             — Cost breakdowns    ║")
    print("║                                                  ║")
    print("║  Open dashboard/observatory.html to explore       ║")
    print("╚══════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
