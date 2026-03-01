"""
Consolidator — Post-session reflection and memory extraction

Runs AFTER each session completes. This is where learning happens.
Makes 2-3 LLM calls to:
  1. REFLECT: Extract lessons and insights from the trajectory
  2. EXTRACT PROCEDURES: Derive reusable WHEN-THEN strategies
  3. EXTRACT FACTS: Pull out factual knowledge as entity-attribute-value
  4. COMPRESS EPISODE: Summarize the full trajectory into compact memory

Each LLM call is fully traced and costed (consolidation has cost too).
"""

import json


# Prompts for each consolidation step
REFLECT_PROMPT = """Review this research trajectory from a financial analysis session.

TASK: {task}

TRAJECTORY:
{trajectory}

FINAL ANSWER:
{final_answer}

Answer these questions:
1. What strategies worked well in this research?
2. What mistakes were made or what was missed?
3. What would you do differently next time?
4. Any patterns you notice?

Format each insight as a separate lesson. Return as JSON:
{{
  "lessons": [
    {{
      "lesson": "The key insight or lesson",
      "context": "What situation or observation led to this lesson",
      "importance_score": 0.0 to 1.0
    }}
  ]
}}

Return ONLY valid JSON, nothing else."""

EXTRACT_PROCEDURES_PROMPT = """Based on this research experience, extract any reusable strategies.

TASK: {task}

TRAJECTORY:
{trajectory}

Format as WHEN-THEN rules. These should be specific enough to be actionable.
Return as JSON:
{{
  "procedures": [
    {{
      "trigger_condition": "WHEN this situation arises...",
      "strategy": "THEN do this..."
    }}
  ]
}}

Return ONLY valid JSON, nothing else."""

EXTRACT_FACTS_PROMPT = """Extract the most important factual knowledge discovered during this research session.
Limit to the TOP 15 most important facts (key financial metrics, risk indicators, and critical findings).

TASK: {task}

TRAJECTORY:
{trajectory}

Format as entity-attribute-value triples. Keep values concise.
Return as JSON:
{{
  "facts": [
    {{
      "entity": "Company or subject name",
      "attribute": "The specific metric or property",
      "value": "The value discovered",
      "context": "Brief context (time period, source)"
    }}
  ]
}}

Return ONLY valid JSON, nothing else."""

COMPRESS_EPISODE_PROMPT = """Summarize this research session into a compact episode summary (under 200 words).

TASK: {task}

TRAJECTORY:
{trajectory}

OUTCOME: {outcome}

Include:
- What was the task
- What approach was taken
- What key findings emerged
- What was the outcome

Return as JSON:
{{
  "task_summary": "Brief task description",
  "trajectory_summary": "What the agent did and found",
  "outcome": "success/partial/failure",
  "key_findings": ["finding 1", "finding 2", ...]
}}

Return ONLY valid JSON, nothing else."""


class Consolidator:
    def __init__(self, llm_client, memory_manager):
        """
        Args:
            llm_client: The LLM client (for making consolidation calls)
            memory_manager: The memory manager (for storing extracted memories)
        """
        self.llm_client = llm_client
        self.memory_manager = memory_manager

    def process(
        self,
        trajectory: list[dict],
        task: str,
        session_id: int,
        final_answer: str = "",
    ) -> dict:
        """
        Run full post-session consolidation.

        Returns:
            dict with consolidation metrics (tokens used, cost, items stored)
        """
        metrics = {
            "llm_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "lessons_stored": 0,
            "procedures_stored": 0,
            "facts_stored": 0,
            "episode_stored": False,
        }

        # Format trajectory as readable text
        trajectory_text = self._format_trajectory(trajectory)
        outcome = "success" if final_answer else "partial"

        enabled = self.memory_manager.enabled_stores

        # 1. REFLECT — extract lessons (if reflective store enabled)
        if "reflective" in enabled:
            lessons = self._extract_lessons(task, trajectory_text, final_answer, metrics)
            if lessons:
                self.memory_manager.store_reflective(lessons)
                metrics["lessons_stored"] = len(lessons)

        # 2. EXTRACT PROCEDURES (if procedural store enabled)
        if "procedural" in enabled:
            procedures = self._extract_procedures(task, trajectory_text, metrics)
            if procedures:
                self.memory_manager.store_procedural(procedures)
                metrics["procedures_stored"] = len(procedures)

        # 3. EXTRACT FACTS (if semantic store enabled)
        if "semantic" in enabled:
            facts = self._extract_facts(task, trajectory_text, session_id, metrics)
            if facts:
                self.memory_manager.store_semantic(facts)
                metrics["facts_stored"] = len(facts)

        # 4. COMPRESS EPISODE (if episodic store enabled)
        if "episodic" in enabled:
            episode = self._compress_episode(
                task, trajectory_text, outcome, session_id, metrics
            )
            if episode:
                metrics["episode_stored"] = True

        return metrics

    # Consolidation calls need more output tokens than agent calls
    # because they produce structured JSON with many items.
    # 16384 gives headroom; if model caps lower, truncated JSON repair kicks in.
    CONSOLIDATION_MAX_TOKENS = 16384

    def _extract_lessons(
        self, task: str, trajectory_text: str, final_answer: str, metrics: dict
    ) -> list[dict]:
        prompt = REFLECT_PROMPT.format(
            task=task, trajectory=trajectory_text, final_answer=final_answer
        )
        response = self.llm_client.call(
            messages=[{"role": "user", "content": prompt}],
            system="You are analyzing a research session to extract lessons learned. Return valid JSON only.",
            metadata={"purpose": "consolidation_reflect"},
            max_tokens=self.CONSOLIDATION_MAX_TOKENS,
        )
        metrics["llm_calls"] += 1
        metrics["total_input_tokens"] += response.get("input_tokens", 0)
        metrics["total_output_tokens"] += response.get("output_tokens", 0)
        metrics["total_cost_usd"] += response.get("cost_usd", 0)

        return self._parse_json_field(response.get("content", ""), "lessons")

    def _extract_procedures(
        self, task: str, trajectory_text: str, metrics: dict
    ) -> list[dict]:
        prompt = EXTRACT_PROCEDURES_PROMPT.format(
            task=task, trajectory=trajectory_text
        )
        response = self.llm_client.call(
            messages=[{"role": "user", "content": prompt}],
            system="You are analyzing a research session to extract reusable strategies. Return valid JSON only.",
            metadata={"purpose": "consolidation_procedures"},
            max_tokens=self.CONSOLIDATION_MAX_TOKENS,
        )
        metrics["llm_calls"] += 1
        metrics["total_input_tokens"] += response.get("input_tokens", 0)
        metrics["total_output_tokens"] += response.get("output_tokens", 0)
        metrics["total_cost_usd"] += response.get("cost_usd", 0)

        return self._parse_json_field(response.get("content", ""), "procedures")

    def _extract_facts(
        self, task: str, trajectory_text: str, session_id: int, metrics: dict
    ) -> list[dict]:
        prompt = EXTRACT_FACTS_PROMPT.format(task=task, trajectory=trajectory_text)
        response = self.llm_client.call(
            messages=[{"role": "user", "content": prompt}],
            system="You are analyzing a research session to extract factual knowledge. Return valid JSON only.",
            metadata={"purpose": "consolidation_facts"},
            max_tokens=self.CONSOLIDATION_MAX_TOKENS,
        )
        metrics["llm_calls"] += 1
        metrics["total_input_tokens"] += response.get("input_tokens", 0)
        metrics["total_output_tokens"] += response.get("output_tokens", 0)
        metrics["total_cost_usd"] += response.get("cost_usd", 0)

        content = response.get("content", "")
        was_truncated = response.get("stop_reason") == "length"
        facts = self._parse_json_field(content, "facts", truncated=was_truncated)
        if not facts:
            stop = response.get("stop_reason", "?")
            print(f"    [consolidator] Fact extraction returned 0 facts "
                  f"({len(content)} chars, stop={stop})")
            if content:
                print(f"    [consolidator]   Response preview: {content[:200]}")
        else:
            print(f"    [consolidator] Extracted {len(facts)} facts")
        # Tag each fact with session source
        for fact in facts:
            fact["source_session"] = session_id
        return facts

    def _compress_episode(
        self,
        task: str,
        trajectory_text: str,
        outcome: str,
        session_id: int,
        metrics: dict,
    ) -> bool:
        prompt = COMPRESS_EPISODE_PROMPT.format(
            task=task, trajectory=trajectory_text, outcome=outcome
        )
        response = self.llm_client.call(
            messages=[{"role": "user", "content": prompt}],
            system="You are compressing a research session into a compact episode summary. Return valid JSON only.",
            metadata={"purpose": "consolidation_episode"},
            max_tokens=self.CONSOLIDATION_MAX_TOKENS,
        )
        metrics["llm_calls"] += 1
        metrics["total_input_tokens"] += response.get("input_tokens", 0)
        metrics["total_output_tokens"] += response.get("output_tokens", 0)
        metrics["total_cost_usd"] += response.get("cost_usd", 0)

        try:
            content = response.get("content", "")
            data = self._parse_json(content)
            if data:
                self.memory_manager.store_episode(
                    session_id=session_id,
                    task_summary=data.get("task_summary", task[:200]),
                    trajectory_summary=data.get("trajectory_summary", ""),
                    outcome=data.get("outcome", outcome),
                    key_findings=data.get("key_findings", []),
                    importance_score=0.7,
                )
                return True
        except Exception:
            # Fallback: store a basic episode even if parsing fails
            self.memory_manager.store_episode(
                session_id=session_id,
                task_summary=task[:200],
                trajectory_summary=trajectory_text[:500],
                outcome=outcome,
                key_findings=[],
                importance_score=0.5,
            )
            return True

        return False

    def _format_trajectory(self, trajectory: list[dict]) -> str:
        """Format the list of trajectory steps into readable text."""
        lines = []
        for i, step in enumerate(trajectory, 1):
            lines.append(f"--- Step {i} ---")
            if "thought" in step:
                lines.append(f"Thought: {step['thought']}")
            if "action" in step:
                lines.append(f"Action: {step['action']}")
            if "action_input" in step:
                lines.append(f"Action Input: {step['action_input']}")
            if "observation" in step:
                lines.append(f"Observation: {step['observation']}")
            if "final_answer" in step:
                lines.append(f"Final Answer: {step['final_answer']}")
            lines.append("")
        return "\n".join(lines)

    def _parse_json(self, text: str, repair_truncated: bool = False) -> dict | list | None:
        """Parse JSON from LLM response, handling markdown code blocks and edge cases.

        Args:
            text: Raw LLM response text
            repair_truncated: If True, attempt to salvage partial JSON from truncated output
        """
        text = text.strip()

        # Strip BOM if present
        text = text.lstrip("\ufeff")

        # Strip markdown code blocks if present
        if "```" in text:
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()

        # Try direct parse first (handles both objects and arrays)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find a JSON array [...]
        arr_start = text.find("[")
        arr_end = text.rfind("]") + 1
        if arr_start >= 0 and arr_end > arr_start:
            try:
                result = json.loads(text[arr_start:arr_end])
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass

        # Try to find a JSON object {...}
        obj_start = text.find("{")
        obj_end = text.rfind("}") + 1
        if obj_start >= 0 and obj_end > obj_start:
            try:
                return json.loads(text[obj_start:obj_end])
            except json.JSONDecodeError:
                pass

        # Attempt to repair truncated JSON (e.g., from stop_reason=length)
        if repair_truncated and text:
            repaired = self._repair_truncated_json(text)
            if repaired is not None:
                return repaired

        return None

    def _repair_truncated_json(self, text: str) -> list[dict] | None:
        """Attempt to salvage entries from truncated JSON array output.

        When the model hits max_tokens mid-JSON, we get something like:
          {"facts": [{"entity": "A", ...}, {"entity": "B", ...}, {"ent
        This finds the last complete object and closes the structure.
        """
        # Find the start of the array
        arr_start = text.find("[")
        if arr_start < 0:
            return None

        arr_text = text[arr_start:]

        # Walk backwards from the end to find the last complete "}" that ends an object
        last_complete = -1
        depth = 0
        for i in range(len(arr_text) - 1, -1, -1):
            ch = arr_text[i]
            if ch == "}":
                if depth == 0:
                    # Check if closing this brace yields a valid array
                    candidate = arr_text[: i + 1] + "]"
                    try:
                        result = json.loads(candidate)
                        if isinstance(result, list) and result:
                            print(f"    [consolidator] Repaired truncated JSON: "
                                  f"salvaged {len(result)} items")
                            return result
                    except json.JSONDecodeError:
                        pass
                depth += 1
            elif ch == "{":
                depth -= 1

        return None

    def _parse_json_field(self, text: str, field: str, truncated: bool = False) -> list[dict]:
        """Parse a specific list field from JSON response.

        Handles multiple formats:
        - {"field": [...]}           — standard wrapper
        - [...]                      — raw array (no wrapper key)
        - {"other_key": [...]}       — alternative key names

        Args:
            truncated: If True, attempt to repair truncated JSON on initial parse failure
        """
        data = self._parse_json(text)
        if data is None and truncated and text:
            # First parse failed on truncated output — try repair
            data = self._parse_json(text, repair_truncated=True)
        if data is None:
            print(f"    [consolidator] WARNING: Failed to parse JSON for '{field}'")
            if text:
                print(f"    [consolidator]   Response preview: {text[:200]}")
            return []

        # Case 1: Got a dict with the exact field name
        if isinstance(data, dict) and field in data:
            return data[field]

        # Case 2: Got a raw list (LLM skipped the wrapper key)
        if isinstance(data, list):
            # Validate items look like the right type
            if data and isinstance(data[0], dict):
                print(f"    [consolidator] INFO: LLM returned raw array for '{field}' (no wrapper key)")
                return data
            return []

        # Case 3: Got a dict with a different key name — find the first list value
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    print(f"    [consolidator] INFO: Found '{field}' under alt key '{key}'")
                    return value

        print(f"    [consolidator] WARNING: No '{field}' found in parsed data (type={type(data).__name__})")
        return []
