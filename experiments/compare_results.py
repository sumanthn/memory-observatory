"""
Compare Results — Generates comparison report and dashboard data

Reads all three experiment outputs and generates:
1. output/report.md — Markdown comparison report with tables
2. output/dashboard_data.json — Structured data for the dashboard
3. output/costs/comparison.json — Cost breakdown data
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _load_scenarios() -> dict:
    """Load scenarios.json and return {id: title} mapping."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "config", "scenarios.json"
    )
    with open(path) as f:
        sessions = json.load(f)["sessions"]
    return {s["id"]: s["title"] for s in sessions}


def load_experiment_summary(experiment_name: str) -> dict | None:
    """Load an experiment summary from output/traces/."""
    path = os.path.join(
        "output", "traces", experiment_name, "experiment_summary.json"
    )
    if not os.path.exists(path):
        print(f"  Warning: No summary found for '{experiment_name}' at {path}")
        return None
    with open(path) as f:
        return json.load(f)


def generate_report(summaries: dict[str, dict]) -> str:
    """Generate the markdown comparison report."""
    lines = [
        "# Memory Observatory — Experiment Comparison Report\n",
        "## Overview\n",
        f"Experiments compared: {', '.join(summaries.keys())}\n",
    ]

    # Cost Comparison Table
    lines.append("## Cost Comparison\n")
    lines.append("| Metric | No Memory | Episodic Only | Full Memory |")
    lines.append("|---|---|---|---|")

    experiments = ["without_memory", "partial_memory", "with_memory"]
    labels = ["No Memory", "Episodic Only", "Full Memory"]

    def get_val(exp, key, default="N/A"):
        s = summaries.get(exp)
        if s is None:
            return default
        return s.get(key, default)

    lines.append(
        f"| Total LLM calls | "
        f"{get_val('without_memory', 'total_llm_calls')} | "
        f"{get_val('partial_memory', 'total_llm_calls')} | "
        f"{get_val('with_memory', 'total_llm_calls')} |"
    )
    lines.append(
        f"| Total input tokens | "
        f"{get_val('without_memory', 'total_input_tokens')} | "
        f"{get_val('partial_memory', 'total_input_tokens')} | "
        f"{get_val('with_memory', 'total_input_tokens')} |"
    )
    lines.append(
        f"| Total output tokens | "
        f"{get_val('without_memory', 'total_output_tokens')} | "
        f"{get_val('partial_memory', 'total_output_tokens')} | "
        f"{get_val('with_memory', 'total_output_tokens')} |"
    )

    for exp in experiments:
        s = summaries.get(exp)
        if s:
            cost = s.get("total_cost_usd", 0)
            summaries[exp]["_total_cost_formatted"] = f"${cost:.4f}"

    lines.append(
        f"| Total cost ($) | "
        f"{get_val('without_memory', '_total_cost_formatted')} | "
        f"{get_val('partial_memory', '_total_cost_formatted')} | "
        f"{get_val('with_memory', '_total_cost_formatted')} |"
    )
    lines.append("")

    # Quality Comparison Table
    lines.append("## Quality Comparison\n")
    lines.append("| Session | No Memory | Episodic Only | Full Memory |")
    lines.append("|---|---|---|---|")

    session_titles = _load_scenarios()

    # Determine session IDs from actual experiment data
    all_sids = set()
    for exp in experiments:
        s = summaries.get(exp)
        if s:
            for k in s.get("quality_scores", {}):
                all_sids.add(int(k) if isinstance(k, str) else k)
    session_ids = sorted(all_sids) if all_sids else sorted(session_titles.keys())

    for sid in session_ids:
        scores = []
        for exp in experiments:
            s = summaries.get(exp)
            if s:
                q_scores = s.get("quality_scores", {})
                score = q_scores.get(sid, q_scores.get(str(sid), "N/A"))
                scores.append(f"{score}/10")
            else:
                scores.append("N/A")

        lines.append(
            f"| {sid}: {session_titles.get(sid, '')} | "
            f"{scores[0]} | {scores[1]} | {scores[2]} |"
        )

    # Average quality
    avgs = []
    for exp in experiments:
        s = summaries.get(exp)
        if s:
            avgs.append(f"{s.get('avg_quality', 'N/A')}/10")
        else:
            avgs.append("N/A")
    lines.append(f"| **Average** | {avgs[0]} | {avgs[1]} | {avgs[2]} |")
    lines.append("")

    # Improvement Over Time (Full Memory)
    with_mem = summaries.get("with_memory")
    if with_mem:
        lines.append("## Improvement Over Time (Full Memory)\n")

        # Use first and last session dynamically
        q_scores = with_mem.get("quality_scores", {})
        steps = with_mem.get("steps_per_session", {})
        all_keys = sorted(int(k) if isinstance(k, str) else k for k in q_scores)
        first_sid = all_keys[0] if all_keys else 1
        last_sid = all_keys[-1] if all_keys else 1

        lines.append(f"| Metric | Session {first_sid} | Session {last_sid} | Change |")
        lines.append("|---|---|---|---|")

        s_first_steps = steps.get(first_sid, steps.get(str(first_sid), "N/A"))
        s_last_steps = steps.get(last_sid, steps.get(str(last_sid), "N/A"))
        if isinstance(s_first_steps, (int, float)) and isinstance(s_last_steps, (int, float)):
            change = s_last_steps - s_first_steps
            lines.append(f"| Steps to complete | {s_first_steps} | {s_last_steps} | {change:+d} |")
        else:
            lines.append(f"| Steps to complete | {s_first_steps} | {s_last_steps} | N/A |")

        s_first_q = q_scores.get(first_sid, q_scores.get(str(first_sid), "N/A"))
        s_last_q = q_scores.get(last_sid, q_scores.get(str(last_sid), "N/A"))
        if isinstance(s_first_q, (int, float)) and isinstance(s_last_q, (int, float)):
            change = s_last_q - s_first_q
            lines.append(f"| Quality score | {s_first_q}/10 | {s_last_q}/10 | {change:+.1f} |")
        else:
            lines.append(f"| Quality score | {s_first_q}/10 | {s_last_q}/10 | N/A |")

        lines.append("")

    # Memory stats
    if with_mem and with_mem.get("memory_final_stats"):
        stats = with_mem["memory_final_stats"]
        lines.append("## Final Memory Stats (Full Memory)\n")
        lines.append(f"- Episodic memories: {stats.get('episodic_count', 0)}")
        lines.append(f"- Semantic memories: {stats.get('semantic_count', 0)}")
        lines.append(f"- Procedural memories: {stats.get('procedural_count', 0)}")
        lines.append(f"- Reflective memories: {stats.get('reflective_count', 0)}")
        lines.append(f"- **Total memories: {stats.get('total_memories', 0)}**")
        lines.append("")

    lines.append("---\n")
    lines.append("*Generated by Memory Observatory*\n")

    return "\n".join(lines)


def generate_dashboard_data(summaries: dict[str, dict]) -> dict:
    """Generate the JSON data structure for the dashboard."""
    experiments = ["without_memory", "partial_memory", "with_memory"]

    session_titles = _load_scenarios()
    dashboard = {
        "experiments": {},
        "session_titles": {str(k): v for k, v in session_titles.items()},
    }

    for exp in experiments:
        s = summaries.get(exp)
        if not s:
            continue

        dashboard["experiments"][exp] = {
            "label": {
                "without_memory": "No Memory",
                "partial_memory": "Episodic Only",
                "with_memory": "Full Memory",
            }.get(exp, exp),
            "total_cost_usd": s.get("total_cost_usd", 0),
            "total_llm_calls": s.get("total_llm_calls", 0),
            "total_input_tokens": s.get("total_input_tokens", 0),
            "total_output_tokens": s.get("total_output_tokens", 0),
            "avg_quality": s.get("avg_quality", 0),
            "quality_scores": s.get("quality_scores", {}),
            "session_costs": s.get("session_costs", {}),
            "steps_per_session": s.get("steps_per_session", {}),
            "memory_final_stats": s.get("memory_final_stats"),
            "session_results": s.get("session_results", {}),
        }

    # Load trace data for Prompt X-Ray panel
    for exp in experiments:
        traces_dir = os.path.join("output", "traces", exp)
        if not os.path.exists(traces_dir):
            continue

        traces = []
        for session_dir in sorted(os.listdir(traces_dir)):
            session_path = os.path.join(traces_dir, session_dir)
            if not os.path.isdir(session_path):
                continue
            for trace_file in sorted(os.listdir(session_path)):
                if trace_file.startswith("step_") and trace_file.endswith(".json"):
                    trace_path = os.path.join(session_path, trace_file)
                    with open(trace_path) as f:
                        traces.append(json.load(f))

        if exp in dashboard["experiments"]:
            dashboard["experiments"][exp]["traces"] = traces

    return dashboard


def run(summaries: dict[str, dict] | None = None):
    """
    Generate comparison report and dashboard data.

    Args:
        summaries: Pre-loaded experiment summaries. If None, loads from disk.
    """
    print("\n" + "=" * 70)
    print("GENERATING COMPARISON REPORT")
    print("=" * 70)

    if summaries is None:
        summaries = {}
        for exp_name in ["without_memory", "partial_memory", "with_memory"]:
            s = load_experiment_summary(exp_name)
            if s:
                summaries[exp_name] = s
                print(f"  Loaded: {exp_name}")

    if not summaries:
        print("  ERROR: No experiment summaries found. Run experiments first.")
        return

    # Generate report
    report = generate_report(summaries)
    os.makedirs("output", exist_ok=True)
    with open("output/report.md", "w") as f:
        f.write(report)
    print(f"  Report written to output/report.md")

    # Generate dashboard data
    dashboard = generate_dashboard_data(summaries)
    with open("output/dashboard_data.json", "w") as f:
        json.dump(dashboard, f, indent=2)
    print(f"  Dashboard data written to output/dashboard_data.json")

    # Generate cost comparison
    os.makedirs("output/costs", exist_ok=True)
    cost_comparison = {
        exp: {
            "total_cost_usd": s.get("total_cost_usd", 0),
            "session_costs": s.get("session_costs", {}),
            "total_llm_calls": s.get("total_llm_calls", 0),
        }
        for exp, s in summaries.items()
    }
    with open("output/costs/comparison.json", "w") as f:
        json.dump(cost_comparison, f, indent=2)
    print(f"  Cost comparison written to output/costs/comparison.json")

    print("\nComparison complete!")
    return dashboard


if __name__ == "__main__":
    run()
