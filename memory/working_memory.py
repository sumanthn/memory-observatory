"""
Working Memory — Current task scratchpad

Not persistent across sessions. Tracks the agent's current state:
what it's working on, what it has found, what questions remain.
"""


class WorkingMemory:
    def __init__(self):
        self.reset()

    def reset(self):
        self._state = {
            "current_objective": "",
            "plan_status": "",
            "key_facts_discovered": [],
            "open_questions": [],
            "tools_used": [],
            "step_count": 0,
        }

    def update(self, **kwargs):
        """Update specific fields of working memory."""
        for key, value in kwargs.items():
            if key in self._state:
                if isinstance(self._state[key], list) and not isinstance(value, list):
                    # Append to list fields
                    self._state[key].append(value)
                else:
                    self._state[key] = value

    def add_fact(self, fact: str):
        if fact not in self._state["key_facts_discovered"]:
            self._state["key_facts_discovered"].append(fact)

    def add_question(self, question: str):
        if question not in self._state["open_questions"]:
            self._state["open_questions"].append(question)

    def resolve_question(self, question: str):
        self._state["open_questions"] = [
            q for q in self._state["open_questions"] if q != question
        ]

    def add_tool_use(self, tool_name: str, args: dict, result_summary: str):
        self._state["tools_used"].append(
            {"tool": tool_name, "args": args, "result_summary": result_summary}
        )

    def increment_step(self):
        self._state["step_count"] += 1

    @property
    def state(self) -> dict:
        return self._state.copy()

    def to_string(self) -> str:
        """Format working memory for prompt injection."""
        lines = ["=== Working Memory (Current Session Scratchpad) ==="]

        if self._state["current_objective"]:
            lines.append(f"Objective: {self._state['current_objective']}")

        if self._state["plan_status"]:
            lines.append(f"Plan Status: {self._state['plan_status']}")

        if self._state["key_facts_discovered"]:
            lines.append("Key Facts Discovered:")
            for fact in self._state["key_facts_discovered"]:
                lines.append(f"  - {fact}")

        if self._state["open_questions"]:
            lines.append("Open Questions:")
            for q in self._state["open_questions"]:
                lines.append(f"  - {q}")

        lines.append(f"Steps taken so far: {self._state['step_count']}")

        return "\n".join(lines)

    def get_token_estimate(self) -> int:
        """Rough token estimate for the working memory text."""
        text = self.to_string()
        return int(len(text.split()) * 1.3)
