"""
Orchestrator — Main agent loop with native tool calling + memory hooks

Uses the OpenAI-compatible tool calling API instead of text-based
ReAct parsing. The model calls tools natively, and results are fed
back as tool messages. This is more reliable across different models.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import MAX_ITERATIONS_PER_TASK
from core.llm_client import LLMClient
from core.prompt_builder import build_prompt
from core.tool_registry import (
    execute_tool,
    get_tool_definitions,
    get_tool_definitions_for_api,
)
from memory.memory_manager import MemoryManager
from memory.working_memory import WorkingMemory
from memory.consolidator import Consolidator
from tracking.token_tracker import TokenTracker
from tracking.cost_calculator import CostCalculator
from tracking.latency_tracker import LatencyTracker
from tracking.quality_scorer import QualityScorer
from tracking.trace_logger import TraceLogger


class Orchestrator:
    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        experiment_name: str = "default",
        output_dir: str = "output",
    ):
        self.memory_manager = memory_manager
        self.memory_enabled = memory_manager is not None and len(
            memory_manager.enabled_stores
        ) > 0
        self.experiment_name = experiment_name

        # Core components
        self.llm_client = LLMClient(experiment_name=experiment_name)
        self.working_memory = WorkingMemory()

        # Tracking
        self.token_tracker = TokenTracker()
        self.cost_calculator = CostCalculator()
        self.latency_tracker = LatencyTracker()
        self.quality_scorer = QualityScorer()
        self.trace_logger = TraceLogger(
            output_dir=os.path.join(output_dir, "traces")
        )
        self.trace_logger.set_experiment(experiment_name)

        # Session results storage
        self.session_results = {}

    def run_session(self, task: str, session_id: int) -> dict:
        """
        Run a single research session using native tool calling.

        The loop:
        1. Retrieve relevant memories (if enabled)
        2. Build prompt with memories + conversation history
        3. Call LLM with tool definitions via API
        4. If model calls a tool: execute it, feed result back
        5. If model gives final text: that's the answer
        6. Update working memory after each step
        7. Loop until done or max iterations

        Post-task:
        8. Consolidate memories (if enabled)
        9. Score quality against ground truth
        10. Save traces and summaries
        """
        print(f"\n{'='*60}")
        print(f"[{self.experiment_name}] Session {session_id}: {task[:60]}...")
        print(f"{'='*60}")

        # Setup
        self.llm_client.set_session(session_id)
        self.trace_logger.set_session(session_id)
        if self.memory_manager:
            self.memory_manager.set_session(session_id)

        self.working_memory.reset()
        self.working_memory.update(current_objective=task)

        # API tool definitions
        api_tools = get_tool_definitions_for_api()
        # Text tool definitions for token counting in metadata
        text_tool_defs = get_tool_definitions()

        # Build the conversation as a rolling message list
        messages = [{"role": "user", "content": f"Task: {task}"}]
        trajectory = []
        final_answer = ""

        for step in range(1, MAX_ITERATIONS_PER_TASK + 1):
            print(f"  Step {step}/{MAX_ITERATIONS_PER_TASK}...", end=" ")

            # 1. Retrieve memories (if enabled)
            retrieved_memories = []
            if self.memory_enabled:
                phase = "planning" if step <= 2 else "execution"
                # Use task + recent context for retrieval
                recent_context = ""
                for m in reversed(messages[-4:]):
                    if isinstance(m.get("content"), str):
                        recent_context += " " + m["content"][:200]
                context = f"{task} {recent_context}"
                retrieved_memories = self.memory_manager.retrieve(
                    context, phase=phase
                )

            # 2. Build system prompt (with memories injected)
            system_prompt, _, prompt_metadata = build_prompt(
                retrieved_memories=retrieved_memories,
                working_memory_text=self.working_memory.to_string(),
                conversation_history=[],  # History is in messages already
                current_observation="",
                tool_definitions=text_tool_defs,
                task=task,
            )

            # 3. Call LLM with native tool calling
            with self.latency_tracker.track() as timer:
                response = self.llm_client.call(
                    messages=messages,
                    system=system_prompt,
                    tools=api_tools,
                    metadata={
                        "session_id": session_id,
                        "step": step,
                        "experiment": self.experiment_name,
                    },
                )

            # Track tokens and cost
            input_tokens = response.get("input_tokens", 0)
            output_tokens = response.get("output_tokens", 0)
            self.token_tracker.record(
                input_tokens, output_tokens, prompt_metadata
            )
            cost_record = self.cost_calculator.record(
                input_tokens, output_tokens, session_id
            )

            content = response.get("content", "")
            tool_use = response.get("tool_use")
            stop_reason = response.get("stop_reason", "")

            # Record trajectory step
            traj_step = {
                "step": step,
                "thought": content[:500] if content else "",
                "memories_retrieved": len(retrieved_memories),
            }

            # 4. Handle response
            if tool_use:
                # Model wants to call a tool
                tool_name = tool_use.get("name", "")
                tool_args = tool_use.get("input", {})
                tool_call_id = tool_use.get("id", f"call_{step}")

                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}

                # Execute the tool
                observation = execute_tool(tool_name, tool_args)

                traj_step["action"] = tool_name
                traj_step["action_input"] = tool_args
                traj_step["observation"] = observation
                trajectory.append(traj_step)

                print(f"Tool: {tool_name} -> {len(observation)} chars")

                # Log trace
                self.trace_logger.log_call(
                    step=step,
                    prompt_metadata=prompt_metadata,
                    response_content=content,
                    response_metadata={
                        "output_tokens": output_tokens,
                        "action": {"tool": tool_name, "args": tool_args},
                        "is_final_answer": False,
                        "latency_ms": timer.elapsed_ms,
                    },
                    cost=cost_record,
                    memory_items=retrieved_memories,
                )

                # Add assistant message with tool call to conversation
                assistant_msg = {"role": "assistant", "content": content or None}
                assistant_msg["tool_calls"] = [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args),
                        },
                    }
                ]
                messages.append(assistant_msg)

                # Add tool result
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": observation,
                    }
                )

                # Update working memory
                self.working_memory.increment_step()
                self.working_memory.add_tool_use(
                    tool_name, tool_args, observation[:200]
                )

            else:
                # No tool call — this is the final answer (or thinking)
                if content and (stop_reason in ("stop", "end_turn") or step >= 3):
                    # Treat as final answer
                    final_answer = content
                    traj_step["action"] = "final_answer"
                    traj_step["final_answer"] = final_answer
                    trajectory.append(traj_step)

                    # Log trace
                    self.trace_logger.log_call(
                        step=step,
                        prompt_metadata=prompt_metadata,
                        response_content=content,
                        response_metadata={
                            "output_tokens": output_tokens,
                            "action": None,
                            "is_final_answer": True,
                            "latency_ms": timer.elapsed_ms,
                        },
                        cost=cost_record,
                        memory_items=retrieved_memories,
                    )

                    print(f"FINAL ANSWER ({len(final_answer)} chars)")
                    break
                else:
                    # Early step with no tool call — ask it to continue
                    trajectory.append(traj_step)
                    messages.append({"role": "assistant", "content": content})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Please use the available tools to gather data. "
                                "Do not make up numbers — use financial_lookup, "
                                "sec_filing, and news_search to research the company."
                            ),
                        }
                    )
                    print("(nudging to use tools)")
                    self.working_memory.increment_step()

        # If we hit max iterations without final answer
        if not final_answer:
            print(f"  WARNING: Hit max iterations ({MAX_ITERATIONS_PER_TASK})")
            # Ask for a final answer explicitly
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Based on all the information gathered so far, "
                        "please provide your complete financial analysis now. "
                        "Include all findings, risks, red flags, and your recommendation."
                    ),
                }
            )
            response = self.llm_client.call(
                messages=messages,
                system=system_prompt,
                metadata={"purpose": "forced_final_answer"},
            )
            final_answer = response.get("content", content)

        # Post-task processing
        # 8. Consolidate memories (if enabled)
        consolidation_metrics = None
        if self.memory_enabled:
            print(f"  Consolidating memories...")
            consolidator = Consolidator(self.llm_client, self.memory_manager)
            consolidation_metrics = consolidator.process(
                trajectory=trajectory,
                task=task,
                session_id=session_id,
                final_answer=final_answer,
            )
            print(
                f"  Stored: {consolidation_metrics.get('facts_stored', 0)} facts, "
                f"{consolidation_metrics.get('procedures_stored', 0)} procedures, "
                f"{consolidation_metrics.get('lessons_stored', 0)} lessons"
            )

        # 9. Score quality
        quality = self.quality_scorer.score(session_id, final_answer)
        print(
            f"  Quality score: {quality['score']}/10 "
            f"({quality['matched_criteria']}/{quality['total_criteria']} criteria)"
        )

        # Build session result
        result = {
            "session_id": session_id,
            "task": task,
            "experiment": self.experiment_name,
            "final_answer": final_answer,
            "steps": len(trajectory),
            "quality": quality,
            "cost": self.cost_calculator.get_summary(),
            "tokens": self.token_tracker.get_summary(),
            "latency": self.latency_tracker.get_summary(),
            "trajectory": trajectory,
            "consolidation": consolidation_metrics,
            "memory_stats": (
                self.memory_manager.get_stats() if self.memory_manager else None
            ),
        }

        # Save session summary
        self.trace_logger.save_session_summary(
            session_id,
            {
                "session_id": session_id,
                "task": task,
                "experiment": self.experiment_name,
                "steps": len(trajectory),
                "quality_score": quality["score"],
                "final_answer_length": len(final_answer),
                "cost_usd": self.cost_calculator.get_summary()["total_cost_usd"],
                "memory_stats": result["memory_stats"],
            },
        )

        self.session_results[session_id] = result
        return result

    def get_experiment_summary(self) -> dict:
        """Generate a full experiment summary across all sessions."""
        session_scores = []
        session_costs = []
        session_steps = []

        for sid, result in sorted(self.session_results.items()):
            session_scores.append(result["quality"]["score"])
            session_costs.append(result["cost"]["session_costs"].get(sid, 0))
            session_steps.append(result["steps"])

        summary = {
            "experiment": self.experiment_name,
            "sessions_completed": len(self.session_results),
            "quality_scores": {
                sid: r["quality"]["score"]
                for sid, r in sorted(self.session_results.items())
            },
            "avg_quality": (
                round(sum(session_scores) / len(session_scores), 2)
                if session_scores
                else 0
            ),
            "total_cost_usd": self.cost_calculator.get_summary()["total_cost_usd"],
            "session_costs": {
                sid: round(c, 6)
                for sid, c in zip(
                    sorted(self.session_results.keys()), session_costs
                )
            },
            "total_llm_calls": self.llm_client.call_count,
            "total_input_tokens": self.llm_client.cumulative_input_tokens,
            "total_output_tokens": self.llm_client.cumulative_output_tokens,
            "steps_per_session": {
                sid: r["steps"]
                for sid, r in sorted(self.session_results.items())
            },
            "memory_final_stats": (
                self.memory_manager.get_stats() if self.memory_manager else None
            ),
            "session_results": {
                sid: {
                    "task": r["task"],
                    "steps": r["steps"],
                    "quality_score": r["quality"]["score"],
                    "final_answer": r["final_answer"],
                    "quality_details": r["quality"]["criteria_results"],
                }
                for sid, r in sorted(self.session_results.items())
            },
        }

        self.trace_logger.save_experiment_summary(summary)
        return summary
