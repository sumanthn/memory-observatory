#!/usr/bin/env python3
"""
Replay all 5 pilot sessions through the FIXED memory pipeline.

Shows exactly what memories the agent would receive at each session,
including the 59 semantic facts we backfilled. Compares against the
original run where semantic was empty.

No API key needed — uses the existing database and retriever logic.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from memory.memory_manager import MemoryManager
from core.prompt_builder import build_prompt, _build_memories_section
from tracking.token_tracker import estimate_tokens


def load_scenarios():
    path = os.path.join(os.path.dirname(__file__), "..", "config", "scenarios.json")
    with open(path) as f:
        return json.load(f)["sessions"][:5]  # Only the 5 pilot sessions


def load_original_traces():
    """Load the original with_memory traces to compare what was retrieved."""
    import glob as glob_mod

    traces_dir = os.path.join(os.path.dirname(__file__), "..", "output", "traces", "with_memory")
    original = {}
    for session_id in range(1, 6):
        session_dir = os.path.join(traces_dir, f"session_{session_id}")
        step1_files = sorted(glob_mod.glob(os.path.join(session_dir, "step_001_*.json")))
        all_steps = sorted(glob_mod.glob(os.path.join(session_dir, "step_*.json")))
        # Exclude summary.json from step count
        all_steps = [s for s in all_steps if "summary" not in s]

        if step1_files:
            with open(step1_files[0]) as f:
                data = json.load(f)
            # Memory items are at data["prompt"]["memory_items"]
            prompt_data = data.get("prompt", {})
            original[session_id] = {
                "memory_items": prompt_data.get("memory_items", []),
                "memory_tokens": prompt_data.get("memory_tokens", 0),
                "total_steps": len(all_steps),
            }
        else:
            original[session_id] = {"memory_items": [], "memory_tokens": 0, "total_steps": 0}
    return original


def main():
    db_path = os.path.join(os.path.dirname(__file__), "..", "output", "memories", "full_memory.db")
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found. Run backfill_semantic.py first.")
        sys.exit(1)

    scenarios = load_scenarios()
    original_traces = load_original_traces()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  MEMORY RETRIEVAL REPLAY — With Semantic Facts                 ║")
    print("║  Showing what each session receives from fixed memory pipeline  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # Initialize memory manager with all stores enabled
    mm = MemoryManager(
        db_path=db_path,
        enabled_stores=["episodic", "semantic", "procedural", "reflective"],
    )

    stats = mm.get_stats()
    print(f"\nMemory Database: {stats['total_memories']} total memories")
    print(f"  Episodic:   {stats['episodic_count']}")
    print(f"  Semantic:   {stats['semantic_count']}")
    print(f"  Procedural: {stats['procedural_count']}")
    print(f"  Reflective: {stats['reflective_count']}")
    print()

    for session in scenarios:
        sid = session["id"]
        task = session["task"]
        title = session.get("title", "")

        print(f"\n{'='*70}")
        print(f"SESSION {sid}: {title}")
        print(f"Task: {task}")
        print(f"{'='*70}")

        # Set session for recency scoring
        mm.set_session(sid)

        # Phase 1: Planning retrieval (steps 1-2)
        planning_memories = mm.retrieve(task, phase="planning")

        # Phase 2: Execution retrieval (steps 3+)
        exec_memories = mm.retrieve(task, phase="execution")

        # Build the prompt to show what agent would see
        memories_text = _build_memories_section(planning_memories)
        memory_tokens = estimate_tokens(memories_text)

        # Compare with original
        orig = original_traces.get(sid, {})
        orig_items = orig.get("memory_items", [])
        orig_tokens = orig.get("memory_tokens", 0)
        orig_types = {}
        for item in orig_items:
            t = item.get("type", item.get("memory_type", "unknown"))
            orig_types[t] = orig_types.get(t, 0) + 1

        new_types = {}
        for item in planning_memories:
            t = item.get("memory_type", "unknown")
            new_types[t] = new_types.get(t, 0) + 1

        print(f"\n  ORIGINAL RUN (no semantic facts):")
        print(f"    Retrieved: {len(orig_items)} items, {orig_tokens} tokens")
        print(f"    Types: {orig_types if orig_types else 'none'}")
        if orig_items:
            for item in orig_items:
                preview = item.get("content_preview", item.get("content", ""))[:80]
                score = item.get("score", 0)
                src = item.get("source_session", "?")
                t = item.get("type", item.get("memory_type", "?"))
                print(f"      [{t:10s}] (s{src}, score={score:.3f}) {preview}")

        print(f"\n  FIXED RUN (with 59 semantic facts):")
        print(f"    Retrieved: {len(planning_memories)} items, {memory_tokens} tokens")
        print(f"    Types: {new_types}")
        for item in planning_memories:
            content = item.get("content", "")[:80]
            score = item.get("score", 0)
            src = item.get("source_session") or item.get("session_id", "?")
            mem_type = item.get("memory_type", "?")
            breakdown = item.get("score_breakdown", {})
            rel = breakdown.get("relevance", 0)
            imp = breakdown.get("importance", 0)
            rec = breakdown.get("recency", 0)
            print(f"      [{mem_type:10s}] (s{src}, score={score:.4f} r={rel:.2f} i={imp:.2f} d={rec:.2f}) {content}")

        # Show the actual prompt section
        print(f"\n  PROMPT INJECTION (what agent sees):")
        print(f"  {'─'*60}")
        for line in memories_text.split("\n"):
            print(f"  │ {line}")
        print(f"  {'─'*60}")

        # Delta analysis
        new_semantic = [m for m in planning_memories if m.get("memory_type") == "semantic"]
        print(f"\n  DELTA:")
        print(f"    Semantic facts now available: {len(new_semantic)}")
        if new_semantic:
            entities = set(m.get("entity", "") for m in new_semantic)
            for entity in sorted(entities):
                facts = [m for m in new_semantic if m.get("entity") == entity]
                attrs = [m.get("attribute", "") for m in facts]
                print(f"      {entity}: {', '.join(attrs)}")
        print(f"    Token overhead: {memory_tokens} (was {orig_tokens}, delta: {memory_tokens - orig_tokens:+d})")

    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY: Impact of Semantic Memory on Each Session")
    print(f"{'='*70}")
    print()
    print(f"{'Session':<12} {'Task':<35} {'Orig Items':>12} {'New Items':>12} {'New Semantic':>14} {'Token Delta':>12}")
    print(f"{'─'*12} {'─'*35} {'─'*12} {'─'*12} {'─'*14} {'─'*12}")

    for session in scenarios:
        sid = session["id"]
        mm.set_session(sid)
        memories = mm.retrieve(session["task"], phase="planning")
        orig = original_traces.get(sid, {})
        orig_count = len(orig.get("memory_items", []))
        orig_tokens = orig.get("memory_tokens", 0)
        new_tokens = estimate_tokens(_build_memories_section(memories))
        sem_count = sum(1 for m in memories if m.get("memory_type") == "semantic")
        title = session.get("title", session["task"][:35])
        print(f"  {sid:<10} {title:<35} {orig_count:>10}   {len(memories):>10}   {sem_count:>12}   {new_tokens - orig_tokens:>+10}")

    print()


if __name__ == "__main__":
    main()
