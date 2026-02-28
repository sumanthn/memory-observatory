# Memory Observatory — Prototype Plan

## Mission

Build a **transparent, instrumented agent** that solves a real multi-session financial research problem while **visualizing exactly what memory does at every step** — what goes in, what comes out, what it costs, and whether it actually helps.

This prototype runs **3 experiments** (with memory, without memory, partial memory) across **5 scripted sessions** and produces a **comparison report + interactive dashboard** proving whether memory is useful, what kinds matter, and what it costs.

---

## Domain: Investment Research Analyst

### Why This Domain

- **Multi-session by nature**: Day 1 research company A, Day 2 research company B, Day 3 compare using both sessions' knowledge
- **Multiple memory types naturally appear**: facts (semantic), experiences (episodic), strategies (procedural), lessons (reflective)
- **Errors are measurable**: wrong number = clearly wrong, not subjective
- **Memory benefit is provable and quantifiable**: cost savings + quality improvement

---

## Project Structure

```
memory-observatory/
│
├── README.md
│
├── config/
│   ├── scenarios.json           # The 5 session scripts
│   ├── mock_data.json           # Simulated financial data
│   └── settings.py              # Model config, cost rates
│
├── core/
│   ├── orchestrator.py          # Main agent loop (ReAct)
│   ├── llm_client.py            # Claude API wrapper + full logging
│   ├── tool_registry.py         # Tool definitions + execution
│   └── prompt_builder.py        # Assembles context, tracks token counts
│
├── memory/
│   ├── memory_manager.py        # Central memory coordinator
│   ├── working_memory.py        # Scratchpad (within-task)
│   ├── episodic_store.py        # "What happened" store
│   ├── semantic_store.py        # "What I know" store
│   ├── procedural_store.py      # "How to do things" store
│   ├── reflective_store.py      # "What I learned" store
│   ├── retriever.py             # Multi-signal retrieval logic
│   └── consolidator.py          # Post-session reflection + compression
│
├── tools/
│   ├── financial_lookup.py      # Mock: returns financial data
│   ├── sec_filing.py            # Mock: returns filing excerpts
│   ├── news_search.py           # Mock: returns recent news
│   └── calculator.py            # Actual: computes ratios etc
│
├── tracking/
│   ├── token_tracker.py         # Counts tokens per call
│   ├── cost_calculator.py       # Computes $ cost per call
│   ├── latency_tracker.py       # Measures time per step
│   ├── quality_scorer.py        # Scores output against ground truth
│   └── trace_logger.py          # Full trace of every LLM call
│
├── experiments/
│   ├── run_with_memory.py       # Run all 5 sessions WITH full memory
│   ├── run_without_memory.py    # Run all 5 sessions WITHOUT memory
│   ├── run_partial_memory.py    # Run with ONLY episodic memory
│   └── compare_results.py       # Generate comparison report
│
├── dashboard/
│   └── observatory.html         # Single-file React dashboard
│
└── output/
    ├── traces/                  # Full LLM call traces (JSON)
    ├── memories/                # Memory store snapshots per session
    ├── costs/                   # Cost breakdowns
    └── report.md               # Final comparison report
```

---

## The 5-Session Scenario Script

### Session 1: "Research TechCorp Inc"

- Agent researches a company from scratch
- Discovers: Revenue $4.2B, Debt-to-equity 1.8 (high), CEO recently changed, missed earnings last quarter
- **Memory created**: Episodic (full trajectory), Semantic (key financial facts)
- **No procedural or reflective yet** — this is the first task

### Session 2: "Research HealthCo Ltd"

- Agent researches a second company
- **KEY MOMENT**: Should the agent recall from Session 1 that checking debt covenants was important? With procedural memory it checks debt FIRST. Without it, generic order.
- **Memory created**: Episodic (trajectory), Semantic (facts), Procedural ("Check debt metrics early for companies with recent leadership changes"), Reflective ("Leadership changes correlate with financial risk signals")

### Session 3: "Compare TechCorp vs HealthCo for investment"

- **THIS IS THE MEMORY TEST**
- **With memory**: Agent retrieves facts from sessions 1 and 2, immediately builds comparison, minimal new research needed
- **Without memory**: Agent must RE-RESEARCH both companies from scratch — double the work, double the cost, possibly inconsistent numbers
- **Memory created**: Procedural ("For comparisons, standardize metrics to same fiscal period before comparing"), Reflective ("Comparison was stronger because of consistent prior data")

### Session 4: "Client asks: What about the debt risk?"

- Follow-up question requiring DEEP cross-session recall
- **With memory**: Instantly retrieves debt metrics for both companies plus the reflection about debt-leadership correlation. Gives nuanced answer.
- **Without memory**: "What companies? What debt? Please provide context." — essentially fails.
- **Memory created**: Reflective ("Clients care about risk narrative, not just numbers")

### Session 5: "New company: RetailMax. Same analysis."

- **THE IMPROVEMENT TEST**
- Agent now has procedural memory from 4 sessions
- Does it research RetailMax BETTER and FASTER than it researched TechCorp in Session 1?
- Measurable: Fewer steps? Checks debt early? Asks about leadership? More structured output?

---

## Mock Data Design

### config/mock_data.json

Create realistic financial data for 3 fictional companies. Each company should have:

- Full financial profile: revenue, expenses, net income, total debt, total equity, cash, operating margin, shares outstanding
- Quarterly data for last 4 quarters
- Some intentional RED FLAGS buried in the data:
  - **TechCorp**: High debt-to-equity (1.8), recent CEO change, missed earnings Q3, a debt covenant violation footnote in the 10-K
  - **HealthCo**: Revenue declining 3 consecutive quarters, large R&D spend, recent FDA approval pending, related-party transaction buried in filings
  - **RetailMax**: Inventory buildup (60 days → 95 days over 4 quarters), margin compression, new store openings funded by debt
- Pre-written SEC filing excerpts (2-3 paragraphs each) with the red flags embedded
- Pre-written news headlines and summaries (3-5 per company)
- **Ground truth answers**: For each session, define what a PERFECT analysis would include, so we can score the agent's output automatically

### config/scenarios.json

```json
{
  "sessions": [
    {
      "id": 1,
      "task": "Conduct a thorough financial analysis of TechCorp Inc. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
      "expected_entities": ["revenue", "debt_to_equity", "ceo_change", "missed_earnings", "debt_covenant"],
      "ground_truth_score_criteria": {
        "identified_revenue": true,
        "identified_high_debt": true,
        "identified_ceo_change": true,
        "identified_missed_earnings": true,
        "found_debt_covenant_footnote": true,
        "provided_recommendation": true
      }
    },
    // ... sessions 2-5 with similar structure
  ]
}
```

### config/settings.py

```python
# Model configuration
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

# Cost rates (per 1K tokens, approximate)
INPUT_COST_PER_1K = 0.003
OUTPUT_COST_PER_1K = 0.015

# Memory settings
MAX_MEMORIES_PER_RETRIEVAL = 8
MAX_MEMORY_TOKENS = 2000
RETRIEVAL_WEIGHTS = {
    "relevance": 0.4,
    "importance": 0.3,
    "recency": 0.2,
    "type_match": 0.1
}

# Agent settings
MAX_ITERATIONS_PER_TASK = 15
```

---

## Detailed File Specifications

### core/llm_client.py

Wrapper around the Claude API that LOGS EVERYTHING. This is the most important file for the observatory.

**Responsibilities:**
- Accept assembled prompt from prompt_builder
- Count input tokens (use `anthropic` library's token counting or estimate at 4 chars/token)
- Call Claude API
- Count output tokens
- Record latency
- Record the FULL prompt sent (for transparency)
- Record which memories were included (passed as metadata)
- Record the FULL response
- Save trace JSON to `output/traces/`

**Trace format (one JSON object per LLM call):**

```json
{
  "call_id": "uuid",
  "experiment": "with_memory",
  "session": 3,
  "step": 5,
  "timestamp": "2026-02-28T10:15:30Z",
  "prompt": {
    "system_tokens": 1200,
    "memory_tokens": 850,
    "memory_items": [
      {
        "type": "semantic",
        "content": "TechCorp revenue: $4.2B",
        "source_session": 1,
        "retrieval_score": 0.92
      },
      {
        "type": "procedural",
        "content": "Check debt metrics early for companies with recent leadership changes",
        "source_session": 2,
        "retrieval_score": 0.85
      }
    ],
    "conversation_history_tokens": 2400,
    "tool_definitions_tokens": 600,
    "task_context_tokens": 300,
    "total_input_tokens": 5350
  },
  "response": {
    "content": "full response text...",
    "output_tokens": 450,
    "action": {
      "tool": "financial_lookup",
      "args": {"company": "HealthCo", "metric": "debt_to_equity"}
    },
    "is_final_answer": false,
    "latency_ms": 2340
  },
  "cost": {
    "input_cost_usd": 0.016,
    "output_cost_usd": 0.007,
    "total_cost_usd": 0.023,
    "cumulative_session_cost_usd": 0.187,
    "cumulative_experiment_cost_usd": 0.542
  }
}
```

### core/prompt_builder.py

Assembles the prompt for each LLM call. Returns both the prompt AND metadata about token allocation.

**Key design principle**: Each section is assembled and measured separately so we can see exactly how many tokens MEMORY consumes vs HISTORY vs TOOLS vs IDENTITY.

**Method signature:**

```python
def build_prompt(
    identity: str,                    # Static agent identity
    retrieved_memories: list[dict],   # From memory_manager.retrieve()
    working_memory: dict,             # Current scratchpad state
    conversation_history: list[dict], # Previous exchanges (may be compressed)
    current_observation: str,         # Latest tool result or user message
    tool_definitions: list[dict],     # Available tools
    task: str                         # Original task description
) -> tuple[list[dict], dict]:
    """
    Returns:
      - messages: list of message dicts for Claude API
      - metadata: {
          "system_tokens": int,
          "memory_tokens": int,
          "memory_items_included": list,
          "history_tokens": int,
          "tool_tokens": int,
          "task_tokens": int,
          "total_tokens": int
        }
    """
```

**System prompt template:**

```
You are a senior investment research analyst. You value accuracy and thoroughness.

{identity_and_values}

{retrieved_memories_section}

{working_memory_scratchpad}

You have access to these tools:
{tool_definitions}

Instructions:
- Think step by step about what information you need
- Use tools to gather data — do not make up numbers
- When you have sufficient information, provide your analysis as final_answer
- Format your response as:
  Thought: [your reasoning]
  Action: [tool_name]
  Action Input: [arguments as JSON]
  
  OR
  
  Thought: [your reasoning]
  Action: final_answer
  Action Input: [your complete analysis]
```

### core/orchestrator.py

The main ReAct loop with memory hooks at every stage.

**The loop:**

```python
def run_session(task: str, session_id: int, memory_enabled: bool = True):
    """
    1. Load task from scenario
    2. If memory_enabled: memory_manager.retrieve(task, phase="planning")
    3. prompt_builder.build_prompt(...)
    4. llm_client.call(prompt) — logged with full trace
    5. Parse response: extract Thought/Action/Action Input
    6. If action is a tool: execute via tool_registry, get observation
    7. Update working_memory scratchpad with observation
    8. Loop back to step 2 (re-retrieve memories each iteration —
       context may have changed, different memories may be relevant)
    9. If action is final_answer: exit loop

    POST-TASK (if memory_enabled):
    10. consolidator.process(trajectory, task, session_id)
    11. Save memory store snapshot to output/memories/
    12. Save complete trace to output/traces/
    
    ALWAYS:
    13. quality_scorer.score(final_answer, ground_truth)
    14. Save session summary
    """
```

**Important**: The orchestrator must handle the case where `memory_enabled=False` by simply skipping steps 2 and 10, passing empty memories to the prompt builder. Everything else stays identical — same tools, same prompts, same loop structure. This ensures a fair comparison.

### core/tool_registry.py

Maps tool names to executable functions. Also provides tool definitions for the prompt.

```python
TOOLS = {
    "financial_lookup": {
        "function": tools.financial_lookup.lookup,
        "description": "Look up financial metrics for a company. Returns specific financial data points.",
        "parameters": {
            "company": "string — Company name (e.g., 'TechCorp')",
            "metric": "string — One of: revenue, net_income, total_debt, total_equity, operating_margin, cash, shares_outstanding, debt_to_equity, quarterly_revenue"
        }
    },
    "sec_filing": {
        "function": tools.sec_filing.get_filing,
        "description": "Retrieve excerpts from SEC filings (10-K, 10-Q) for a company.",
        "parameters": {
            "company": "string — Company name",
            "filing_type": "string — One of: 10-K, 10-Q"
        }
    },
    "news_search": {
        "function": tools.news_search.search,
        "description": "Search recent news articles about a company.",
        "parameters": {
            "company": "string — Company name"
        }
    },
    "calculate": {
        "function": tools.calculator.evaluate,
        "description": "Evaluate a mathematical expression. Use for computing ratios, percentages, comparisons.",
        "parameters": {
            "expression": "string — Math expression (e.g., '4.2 / 2.3')"
        }
    }
}
```

### memory/memory_manager.py

Central coordinator for all memory operations.

**Key methods:**

```python
class MemoryManager:
    def __init__(self, db_path: str, enabled_stores: list[str] = None):
        """
        enabled_stores controls which memory types are active.
        - Full memory: ["episodic", "semantic", "procedural", "reflective"]
        - Partial (episodic only): ["episodic"]
        - No memory: [] or None
        """

    def retrieve(self, task_context: str, phase: str = "planning") -> list[dict]:
        """
        Returns ranked memories relevant to current context.

        Phase affects type weighting:
          planning   → prioritize procedural (0.4) + reflective (0.3)
          execution  → prioritize semantic (0.4) + episodic (0.3)
          review     → prioritize reflective (0.5)

        Scoring per memory:
          score = (relevance * 0.4) + (importance * 0.3)
                  + (recency * 0.2) + (type_match * 0.1)

        Returns list of dicts:
        [
          {
            "type": "procedural",
            "content": "Check debt metrics early...",
            "source_session": 2,
            "score": 0.85,
            "score_breakdown": {
              "relevance": 0.9, "importance": 0.8,
              "recency": 0.7, "type_match": 1.0
            }
          },
          ...
        ]

        Respects MAX_MEMORIES_PER_RETRIEVAL and MAX_MEMORY_TOKENS.
        """

    def store_episode(self, session_id, trajectory, task, outcome):
        """Store compressed episode in episodic store."""

    def store_semantic(self, facts: list[dict]):
        """Store extracted facts. Check for conflicts with existing facts."""

    def store_procedural(self, strategies: list[dict]):
        """Store strategies. If similar exists, increment success_count."""

    def store_reflective(self, lessons: list[dict]):
        """Store lessons learned."""

    def get_stats(self) -> dict:
        """
        Returns stats for dashboard:
        {
          "episodic_count": int,
          "semantic_count": int,
          "procedural_count": int,
          "reflective_count": int,
          "total_memories": int,
          "estimated_total_tokens": int
        }
        """
```

### memory/ — Individual Stores

All 4 stores use SQLite. Each store is a separate table in the same DB file.

**Schemas:**

```sql
-- Episodic: What happened
CREATE TABLE episodic (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    timestamp TEXT,
    task_summary TEXT,
    trajectory_summary TEXT,
    outcome TEXT,           -- success/partial/failure
    key_findings TEXT,      -- JSON list of important findings
    importance_score REAL,
    embedding BLOB,
    access_count INTEGER DEFAULT 0,
    last_accessed TEXT
);

-- Semantic: What I know (facts)
CREATE TABLE semantic (
    id INTEGER PRIMARY KEY,
    entity TEXT,            -- e.g., "TechCorp"
    attribute TEXT,         -- e.g., "revenue"
    value TEXT,             -- e.g., "$4.2B"
    context TEXT,           -- e.g., "FY2025 annual"
    source_session INTEGER,
    confidence REAL,
    embedding BLOB,
    last_verified TEXT,
    access_count INTEGER DEFAULT 0
);

-- Procedural: How to do things
CREATE TABLE procedural (
    id INTEGER PRIMARY KEY,
    trigger_condition TEXT,  -- WHEN this situation...
    strategy TEXT,           -- DO this...
    success_count INTEGER DEFAULT 1,
    failure_count INTEGER DEFAULT 0,
    source_sessions TEXT,    -- JSON list of session IDs
    embedding BLOB,
    access_count INTEGER DEFAULT 0
);

-- Reflective: What I learned
CREATE TABLE reflective (
    id INTEGER PRIMARY KEY,
    lesson TEXT,
    context TEXT,            -- What situation triggered this lesson
    derived_from TEXT,       -- JSON: which episodes/sessions
    importance_score REAL,
    embedding BLOB,
    access_count INTEGER DEFAULT 0,
    created_at TEXT
);
```

### memory/retriever.py

Implements multi-signal scoring for memory retrieval.

**Relevance**: Use cosine similarity between the task context embedding and memory embeddings. For the prototype, use `sentence-transformers` (`all-MiniLM-L6-v2`) or fall back to simple TF-IDF cosine similarity if we want zero dependencies.

**Importance**: Stored on each memory at creation time. Reflective memories and procedural memories with high success rates get higher scores.

**Recency**: Exponential decay based on session distance. `recency = exp(-0.3 * sessions_ago)`

**Type match**: Based on current phase (planning/execution/review), each memory type gets a weight (0.0 to 1.0).

### memory/consolidator.py

Runs AFTER each session completes. This is where learning happens.

```python
class Consolidator:
    def process(self, trajectory: list[dict], task: str, session_id: int):
        """
        1. REFLECT: Send trajectory to LLM with prompt:
           "Review this research trajectory. Answer:
            - What strategies worked well?
            - What mistakes were made or what was missed?
            - What would you do differently next time?
            - Any patterns you notice?
            Format each insight as a separate lesson."

           Parse response into structured lessons.
           Store in reflective_store.
           LOG THIS LLM CALL with full trace (consolidation has cost too).

        2. EXTRACT PROCEDURES: Send trajectory to LLM with prompt:
           "Based on this experience, extract any reusable strategies.
            Format as: WHEN [situation] THEN [strategy]"

           Store in procedural_store.
           If similar procedure exists (cosine similarity > 0.85),
           update existing one's success_count instead of creating new.

        3. EXTRACT FACTS: Send trajectory to LLM with prompt:
           "Extract all factual knowledge discovered.
            Format as JSON: [{entity, attribute, value, context}]"

           Store in semantic_store.
           If conflicting fact exists, keep newer one but log the conflict.

        4. COMPRESS EPISODE:
           Summarize the full trajectory into a compact episodic memory
           (< 500 tokens). Store in episodic_store.

        5. RETURN consolidation cost (tokens + $) for tracking.
        """
```

### tools/ — Mock Implementations

Each tool reads from `config/mock_data.json` and returns realistic responses.

**financial_lookup.py**: Takes company + metric, returns the value from mock data with some realistic formatting. Example return: `"TechCorp revenue (FY2025): $4.2 billion. Note: This represents a 3.1% YoY increase."`

**sec_filing.py**: Takes company + filing type, returns 2-3 paragraphs of pre-written text that includes red flags. The red flags should be subtle — buried in the middle of boring text, just like real filings.

**news_search.py**: Takes company, returns 3-5 mock news items with headline, date, source, and 2-sentence summary.

**calculator.py**: Actually evaluates math expressions using Python's `eval()` with a restricted namespace (only math operations, no imports). Returns the computed result.

### tracking/ — Instrumentation

**token_tracker.py**: Counts tokens per section of the prompt. Uses a simple estimation (split by whitespace, multiply by 1.3) or the anthropic tokenizer if available.

**cost_calculator.py**: Takes token counts, applies rates from settings.py, returns cost breakdown.

**latency_tracker.py**: Wraps function calls with timing. Records per-call and cumulative latency.

**quality_scorer.py**: Compares agent's final answer against ground truth criteria from scenarios.json. For each criterion (e.g., "identified_high_debt"), checks if the agent's output contains relevant information. Returns a score out of 10.

**trace_logger.py**: Writes the trace JSON files. One file per LLM call, organized by experiment/session. Also writes session summaries and experiment summaries.

---

## Experiment Runners

### experiments/run_with_memory.py

```python
"""
Run all 5 sessions with FULL memory system enabled.
All 4 memory types active: episodic, semantic, procedural, reflective.
"""

def run():
    memory_manager = MemoryManager(
        db_path="output/memories/full_memory.db",
        enabled_stores=["episodic", "semantic", "procedural", "reflective"]
    )
    orchestrator = Orchestrator(
        memory_manager=memory_manager,
        experiment_name="with_memory"
    )

    for session in load_scenarios():
        result = orchestrator.run_session(
            task=session["task"],
            session_id=session["id"]
        )
        # Consolidation happens inside run_session
        # Snapshot memory DB after each session
        snapshot_memory_db(session["id"], "with_memory")

    generate_experiment_summary("with_memory")
```

### experiments/run_without_memory.py

```python
"""
Run all 5 sessions with NO memory.
Each session starts completely fresh.
"""

def run():
    orchestrator = Orchestrator(
        memory_manager=None,  # No memory
        experiment_name="without_memory"
    )

    for session in load_scenarios():
        result = orchestrator.run_session(
            task=session["task"],
            session_id=session["id"]
        )
        # No consolidation, no memory storage

    generate_experiment_summary("without_memory")
```

### experiments/run_partial_memory.py

```python
"""
Run with ONLY episodic memory.
Tests whether raw recall is enough vs higher-level memory types.
"""

def run():
    memory_manager = MemoryManager(
        db_path="output/memories/partial_memory.db",
        enabled_stores=["episodic"]  # Only episodic
    )
    orchestrator = Orchestrator(
        memory_manager=memory_manager,
        experiment_name="partial_memory"
    )

    for session in load_scenarios():
        result = orchestrator.run_session(
            task=session["task"],
            session_id=session["id"]
        )
        # Only episodic storage, no procedural/reflective extraction
        snapshot_memory_db(session["id"], "partial_memory")

    generate_experiment_summary("partial_memory")
```

### experiments/compare_results.py

Reads all three experiment outputs and generates:

1. **output/report.md** — Markdown comparison report with tables
2. **output/costs/comparison.json** — Structured cost data for dashboard
3. **output/traces/comparison_summary.json** — Aggregated metrics

**Report should include these tables:**

Cost Comparison:
| Metric | No Memory | Episodic Only | Full Memory |
|---|---|---|---|
| Total LLM calls | ? | ? | ? |
| Total input tokens | ? | ? | ? |
| Total output tokens | ? | ? | ? |
| Memory retrieval tokens | 0 | ? | ? |
| Consolidation tokens | 0 | 0 | ? |
| Total cost ($) | ? | ? | ? |
| Memory overhead cost ($) | $0.00 | ? | ? |
| Net effective cost ($) | ? | ? | ? |

Quality Comparison:
| Session | No Memory | Episodic Only | Full Memory |
|---|---|---|---|
| 1: Research TechCorp | ?/10 | ?/10 | ?/10 |
| 2: Research HealthCo | ?/10 | ?/10 | ?/10 |
| 3: Compare Both | ?/10 | ?/10 | ?/10 |
| 4: Client Follow-up | ?/10 | ?/10 | ?/10 |
| 5: New Company | ?/10 | ?/10 | ?/10 |
| **Average** | ? | ? | ? |

Improvement Over Time (Full Memory only):
| Metric | Session 1 | Session 5 | Improvement |
|---|---|---|---|
| Steps to complete | ? | ? | ? |
| Time to complete | ? | ? | ? |
| Quality score | ? | ? | ? |
| Red flags caught | ? | ? | ? |

---

## Dashboard Specification

### dashboard/observatory.html

Single-file React artifact (HTML with inline JS/CSS). Reads from JSON files in `output/`.

**For the prototype**: Since the dashboard can't directly read files, have `compare_results.py` generate a single `dashboard_data.json` file that embeds all the data the dashboard needs. The dashboard includes this data inline or loads it.

**Alternative approach**: Generate the dashboard HTML with the data embedded directly in a `<script>` tag during the comparison step. This makes the dashboard fully self-contained.

**Panels to include:**

#### Panel 1: Prompt X-Ray

For any selected LLM call (dropdown: experiment → session → step), show a stacked bar:

```
System Prompt          ████████░░░░  1,200 tokens
Retrieved Memories     █████░░░░░░░    850 tokens
  ├ semantic (3)       ███░░░░░░░░░    400 tokens
  ├ procedural (1)     ██░░░░░░░░░░    200 tokens
  └ reflective (1)     ██░░░░░░░░░░    250 tokens
Conversation History   ████████████  2,400 tokens
Tool Definitions       ███░░░░░░░░░    600 tokens
Task Context           █░░░░░░░░░░░    300 tokens
───────────────────────────────────
TOTAL                              5,350 tokens
Cost: $0.023
```

Below the bar: expandable sections showing the actual text of each memory item that was retrieved.

#### Panel 2: Memory Growth Timeline

Visual timeline showing memories accumulate across sessions. Use colored dots/icons:
- 🔵 Episodic
- 🟢 Semantic
- 🟠 Procedural
- 🔴 Reflective

Show count per type at each session boundary.

#### Panel 3: Cost Comparison Chart

Grouped bar chart with 3 groups (No Memory, Episodic Only, Full Memory). Each bar stacked: LLM cost (blue) + memory overhead (orange).

#### Panel 4: Quality Over Time

Line chart with 3 lines (one per experiment). X-axis: sessions 1-5. Y-axis: quality score 0-10. The lines should diverge, especially at sessions 3 and 4.

#### Panel 5: A/B Diff View

Side-by-side text comparison of Session 3 or Session 4 output. Left: without memory. Right: with memory. Highlight the differences — the with-memory version should reference prior research specifically.

**Tech stack for dashboard:**
- React with hooks
- Recharts for charts
- Tailwind for styling
- All in a single .html file (inline everything)

---

## Execution Steps for Claude Code

### Step 1: Project Setup + Mock Data

```
Create the memory-observatory project structure as defined above.

Create config/mock_data.json with realistic financial data for 3 companies:

TechCorp Inc:
- Revenue: $4.2B (FY2025), up 3.1% YoY
- Net Income: $380M
- Total Debt: $2.8B
- Total Equity: $1.55B (debt-to-equity: 1.8)
- Cash: $900M
- Operating Margin: 18.2%
- Quarterly revenue: Q1 $980M, Q2 $1.05B, Q3 $1.02B (miss), Q4 $1.15B
- Red flags: CEO changed 6 months ago, missed Q3 earnings by 8%, debt covenant violation footnote in 10-K stating max leverage ratio of 1.5x was breached
- SEC filing text: 3 paragraphs including the buried covenant violation
- News: 5 headlines covering CEO change, earnings miss, new product launch, analyst downgrade, partnership announcement

HealthCo Ltd:
- Revenue: $2.1B (FY2025), down 5.2% YoY
- Net Income: $95M
- Total Debt: $800M
- Total Equity: $1.2B (debt-to-equity: 0.67)
- Cash: $450M
- Operating Margin: 11.8%
- Quarterly revenue: Q1 $560M, Q2 $540M, Q3 $520M, Q4 $480M (declining)
- Red flags: 3 consecutive quarters of revenue decline, $340M R&D spend (16% of revenue), FDA approval pending for key drug, related-party transaction with board member's company
- SEC filing text: 3 paragraphs including the related-party transaction
- News: 5 headlines

RetailMax Corp:
- Revenue: $6.8B, up 8% YoY
- Net Income: $210M
- Total Debt: $3.2B
- Total Equity: $2.1B (debt-to-equity: 1.52)
- Cash: $380M
- Operating Margin: 5.1% (compressed from 7.2% prior year)
- Red flags: Inventory days increasing (60→75→85→95), margin compression, 40 new stores opened funded by debt
- SEC filing text: 3 paragraphs
- News: 5 headlines

Create config/scenarios.json with the 5 sessions as described above, each with task description, expected entities, and ground truth scoring criteria.

Create config/settings.py with model configuration and cost rates.
```

### Step 2: Memory System

```
Build the memory system:

1. memory/episodic_store.py, semantic_store.py, procedural_store.py, reflective_store.py
   - Each uses SQLite with the schemas defined above
   - Each has: add(), search(query_embedding, top_k), get_all(), get_stats()
   - For embeddings: use a simple approach — TF-IDF vectors with sklearn
     (or if sentence-transformers is available, use all-MiniLM-L6-v2)
   - If neither available, fall back to bag-of-words cosine similarity
     (this is a prototype — perfect embeddings aren't critical)

2. memory/retriever.py
   - Implements multi-signal scoring: relevance × importance × recency × type_match
   - Phase-aware type weighting
   - Returns scored and ranked memories with full score breakdown

3. memory/memory_manager.py
   - Central coordinator
   - retrieve() and store() methods as specified
   - Configurable enabled_stores list
   - get_stats() for dashboard

4. memory/working_memory.py
   - Simple dict-based scratchpad
   - Tracks: current_objective, plan_status, key_facts_discovered, open_questions
   - update() method called after each agent step
   - to_string() method for prompt injection

5. memory/consolidator.py
   - Post-session processing as specified
   - Makes 2-3 LLM calls (reflection, fact extraction, procedure extraction)
   - Each call fully traced and costed
   - Returns consolidation cost metrics
```

### Step 3: Core Agent Engine

```
Build the core agent:

1. core/llm_client.py
   - Wraps anthropic Python SDK
   - Every call produces a trace JSON as specified
   - Tracks cumulative costs per session and per experiment
   - Handles retries gracefully

2. core/prompt_builder.py
   - Assembles prompt from components
   - Returns messages + metadata with per-section token counts
   - System prompt includes the agent identity as specified

3. core/tool_registry.py
   - Maps tool names to mock functions
   - Provides tool definitions in the format Claude expects
   - Validates tool arguments before execution

4. core/orchestrator.py
   - ReAct loop as specified
   - Memory retrieval before each LLM call (if enabled)
   - Working memory update after each step
   - Consolidation after task completion (if memory enabled)
   - Max iteration limit (15) as safety valve
   - Handles both memory-enabled and memory-disabled modes

5. tools/financial_lookup.py, sec_filing.py, news_search.py, calculator.py
   - Read from mock_data.json
   - Return formatted strings that look like real tool outputs
   - calculator.py actually computes expressions
```

### Step 4: Tracking + Quality Scoring

```
Build the tracking system:

1. tracking/token_tracker.py
   - Estimates token counts per text section
   - Simple approach: len(text.split()) * 1.3 (rough but sufficient)

2. tracking/cost_calculator.py
   - Takes token counts + rates from settings
   - Returns per-call and cumulative costs

3. tracking/latency_tracker.py
   - Context manager or decorator for timing
   - Records per-call latency

4. tracking/quality_scorer.py
   - Takes agent's final answer + ground truth criteria
   - For each criterion, checks if the answer addresses it
   - Simple keyword/phrase matching for prototype
   - Returns score out of 10 with per-criterion breakdown

5. tracking/trace_logger.py
   - Writes trace JSONs to output/traces/{experiment}/{session}/
   - Writes session summaries
   - Writes experiment summaries
```

### Step 5: Experiment Runners

```
Build the three experiment runners:

1. experiments/run_with_memory.py
   - Full memory system, all 4 types
   - Runs 5 sessions sequentially
   - Snapshots memory DB after each session

2. experiments/run_without_memory.py
   - No memory at all
   - Each session is independent

3. experiments/run_partial_memory.py
   - Episodic memory only
   - No procedural, reflective, or semantic extraction

4. experiments/compare_results.py
   - Reads traces from all 3 experiments
   - Generates output/report.md with comparison tables
   - Generates output/dashboard_data.json for the dashboard

All runners should:
- Print progress to console as they run
- Handle errors gracefully (if one session fails, continue to next)
- Generate clean output even if some sessions are incomplete

Add a main.py at project root that runs all 3 experiments sequentially:
  python main.py --experiment all|with_memory|without_memory|partial_memory
```

### Step 6: Dashboard

```
Build dashboard/observatory.html as a single-file React artifact.

It should load data from a JSON object embedded in the HTML
(generated by compare_results.py and injected into the HTML,
or kept as a separate file loaded via fetch).

Panels:
1. Prompt X-Ray — token breakdown visualization per LLM call
2. Memory Growth Timeline — colored dots showing accumulation
3. Cost Comparison — grouped stacked bar chart (Recharts)
4. Quality Over Time — multi-line chart (Recharts)
5. A/B Diff View — side-by-side text output comparison

Design: Clean, dark theme, data-dense but readable.
Use Tailwind for layout, Recharts for charts.
All in one .html file.
```

---

## Key Design Principles

1. **Transparency over magic**: Every aspect must be visible and inspectable. Don't hide what goes into the prompt — show it. Don't hide costs — show every penny.

2. **Fair comparison**: The only difference between the 3 experiments should be the memory configuration. Same model, same tools, same prompts, same scenarios, same evaluation.

3. **Real costs**: Track actual API costs (or realistic estimates). Memory has overhead — consolidation LLM calls cost money. Show this honestly.

4. **Measurable quality**: Ground truth criteria make quality scoring objective, not subjective.

5. **Self-contained**: Mock data means zero external dependencies beyond the Claude API. Anyone can clone and run this.

6. **If memory hurts, show it**: If memory makes Session 1 slower (overhead with no benefit), that's a valid and important finding. Don't hide negative results.

---

## Expected Outcomes

After running all experiments, the report should demonstrate:

1. **Sessions 1-2**: Memory has minimal benefit (slight overhead, similar quality). Both approaches do fresh research.

2. **Session 3 (comparison)**: Memory dramatically reduces cost (no re-research) and improves quality (consistent data from prior sessions). This is the inflection point.

3. **Session 4 (follow-up)**: Memory is ESSENTIAL. Without it, the task is nearly impossible. With it, the agent gives a rich, contextualized answer instantly.

4. **Session 5 (new company)**: Full memory agent performs measurably better than Session 1 — fewer steps, catches red flags earlier (procedural memory), more structured output.

5. **Episodic-only vs full memory**: Episodic helps with recall but doesn't show the improvement in Session 5. Procedural + reflective memory drive the learning curve.

6. **Cost break-even**: Memory overhead costs are recovered by Session 3 through reduced re-research. By Session 5, full memory is both cheaper AND better.
