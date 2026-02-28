# Memory Observatory

An experimental platform that transparently evaluates how persistent memory systems impact AI agent performance on multi-session tasks.

The agent plays the role of a senior investment research analyst, researching fictional companies across multiple sessions. We run three controlled experiments — no memory, episodic-only memory, and full 4-type memory — and measure quality, cost, and behavior differences.

## Why This Exists

LLM agents forget everything between sessions. This project measures what happens when you give them persistent memory, and whether the overhead is worth it. The key questions:

- Does memory actually improve output quality, or just add cost?
- Which memory types matter? (facts vs experiences vs strategies vs lessons)
- When does memory help vs hurt?
- Can an LLM extract its own memories reliably?

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                            │
│  ReAct agent loop with native OpenAI-format tool calling    │
│                                                             │
│  For each step:                                             │
│    1. Retrieve relevant memories (scored & ranked)          │
│    2. Build prompt (identity + memories + history + tools)  │
│    3. Call LLM → get tool call or final answer              │
│    4. Execute tool, feed result back                        │
│    5. Update working memory                                 │
│                                                             │
│  After session:                                             │
│    6. CONSOLIDATE — LLM reviews its own trajectory          │
│       → Extract lessons (reflective)                        │
│       → Extract strategies (procedural)                     │
│       → Extract facts (semantic)                            │
│       → Compress episode (episodic)                         │
│    7. Score quality against ground truth                    │
│    8. Save full trace                                       │
└─────────────────────────────────────────────────────────────┘
```

### Memory Types

| Type | What It Stores | Example | Store |
|------|---------------|---------|-------|
| **Episodic** | Compressed session summaries | "Session 1: Analyzed TechCorp, found covenant breach..." | SQLite |
| **Semantic** | Entity-attribute-value facts | `TechCorp → debt_to_equity → 1.81x` | SQLite |
| **Procedural** | WHEN-THEN strategies | "WHEN company has covenant breach THEN check waiver terms" | SQLite |
| **Reflective** | Meta-cognitive lessons | "Debt analysis should include maturity schedule" | SQLite |

### Retrieval Scoring

Each candidate memory is scored on 4 signals:

```
score = 0.4 × relevance        # bag-of-words cosine similarity to query
     + 0.3 × importance        # stored importance / confidence / success rate
     + 0.2 × recency           # exponential decay by session distance
     + 0.1 × type_match        # phase-aware weighting (planning vs execution)
```

A diversification pass ensures at least one memory from each available type is included, preventing any single type from crowding out others.

### Consolidation

After each session, the same LLM reviews its own work trajectory and extracts memories through 4 separate API calls. This is where learning happens — the agent literally reflects on what it did and produces reusable knowledge.

The consolidation calls use `max_tokens=8192` (vs 4096 for agent calls) because structured JSON output with many items requires more output budget. This was a critical fix — the original 4096 limit caused the model to hit the token ceiling, returning empty responses and silently producing zero semantic facts.

## Project Structure

```
memory-observatory/
├── main.py                    # CLI entry point
├── config/
│   ├── scenarios.json         # 100 session definitions with ground truth
│   ├── mock_data.json         # 3 fictional companies (10 planned)
│   └── settings.py            # Model config, retrieval weights, costs
├── core/
│   ├── orchestrator.py        # Main agent loop
│   ├── llm_client.py          # OpenRouter API wrapper + cost tracking
│   ├── prompt_builder.py      # Prompt assembly with memory injection
│   └── tool_registry.py       # Tool definitions + mock execution
├── memory/
│   ├── memory_manager.py      # Central coordinator for all stores
│   ├── consolidator.py        # Post-session LLM-based memory extraction
│   ├── retriever.py           # Multi-signal scoring and ranking
│   ├── episodic_store.py      # Session summaries
│   ├── semantic_store.py      # Entity-attribute-value facts
│   ├── procedural_store.py    # WHEN-THEN strategies
│   ├── reflective_store.py    # Lessons learned
│   └── working_memory.py      # Per-session scratchpad (not persistent)
├── tools/
│   ├── financial_lookup.py    # Mock financial data API
│   ├── sec_filing.py          # Mock SEC filing retrieval
│   ├── news_search.py         # Mock news search
│   └── calculator.py          # Basic math tool
├── experiments/
│   ├── run_without_memory.py  # Control: no memory
│   ├── run_partial_memory.py  # Episodic only
│   ├── run_with_memory.py     # Full 4-type memory
│   └── compare_results.py     # Cross-experiment comparison
├── tracking/
│   ├── token_tracker.py       # Per-section token counting
│   ├── cost_calculator.py     # Cost computation
│   ├── latency_tracker.py     # Timing
│   ├── quality_scorer.py      # Ground truth scoring
│   └── trace_logger.py        # Full LLM call traces
├── scripts/
│   ├── backfill_semantic.py   # Populate semantic store from known data
│   └── replay_with_semantic.py # Compare retrieval with/without semantic
├── dashboard/
│   └── observatory.html       # Interactive visualization
├── docs/
│   └── METHODOLOGY_AND_OBSERVATIONS.md  # Detailed methodology report
└── output/                    # Generated at runtime
    ├── traces/                # Full LLM call traces per step
    ├── memories/              # SQLite databases + snapshots
    └── costs/                 # Cost breakdowns
```

## Quick Start

### Prerequisites

- Python 3.12+
- An OpenRouter API key (for StepFun Step 3.5 Flash model)

### Setup

```bash
# Create virtual environment
uv venv .venv && source .venv/bin/activate
uv pip install openai

# Set API key
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Run Experiments

```bash
# Run all 3 experiments across all sessions
python main.py

# Run a single experiment
python main.py --experiment with_memory

# Run specific sessions
python main.py --experiment with_memory --sessions 1-5

# Regenerate comparison report from existing data
python main.py --compare-only
```

### Cost

The model (StepFun Step 3.5 Flash) is extremely cheap via OpenRouter:
- Input: $0.10/M tokens
- Output: $0.30/M tokens
- **A full 5-session experiment costs ~$0.01-0.02**
- Estimated 100-session full run: ~$5.10 across all 3 experiments

## The 5-Session Pilot

The pilot uses 3 fictional companies across 5 progressively challenging sessions:

| Session | Task | Tests |
|---------|------|-------|
| 1 | Research TechCorp Inc. | Fresh analysis from scratch |
| 2 | Research HealthCo Ltd. | Fresh analysis, different sector |
| 3 | Compare TechCorp vs HealthCo | Cross-session knowledge recall |
| 4 | Client debt risk follow-up | Targeted recall of specific facts |
| 5 | Research RetailMax Corp. | Transfer of learned strategies |

### Results

| Condition | Avg Quality | Session 4 | Cost |
|-----------|------------|-----------|------|
| **Full Memory** | **10.0/10** | **10.0/10** | $0.014 |
| No Memory | 8.4/10 | 2.0/10 | $0.011 |
| Episodic Only | 8.0/10 | 10.0/10 | $0.009 |

**Session 4 is the smoking gun.** The no-memory agent hits the 15-step maximum doing individual metric lookups without ever synthesizing an answer — it scores 2.0/10. The memory-equipped agent already has the debt figures and focuses on the actual question.

## Key Findings

### 1. Memory eliminates catastrophic failures

Without memory, the agent has a 20% failure rate (1 of 5 sessions). With full memory: 0%. The cost of consolidation (~$0.0005 per session for 4 LLM calls) prevents downstream failures worth 10-100x more.

### 2. Semantic memory enables efficiency

With the fixed semantic extraction pipeline, Session 4 (debt comparison) completes in **7 steps vs 11** — a 36% reduction. The agent skips 4 financial lookups because it already has the debt numbers in its prompt from prior sessions.

### 3. The right memory mix matters

The original run had 6 procedural + 2 reflective memories for Session 4 — lots of generic strategies but zero actual facts. After fixing semantic extraction, the retriever delivers 5 semantic facts + 1 episodic + 1 procedural + 1 reflective. This targeted mix uses **150 fewer tokens** while providing more useful context.

### 4. Consolidation token limits are critical

The original `MAX_TOKENS=4096` caused the model to hit the output ceiling during fact extraction, returning empty responses and silently producing zero semantic facts across all sessions. Increasing consolidation calls to 8192 tokens fixed this — Session 1 now extracts **34 semantic facts** in a single call.

### 5. Episodic-only memory is fragile

The episodic-only condition suffers a catastrophic 0.0/10 failure on Session 2. Compressed episode summaries can mislead without the granular semantic facts to ground them.

## Bugs Found & Fixed

During development, we identified and fixed several issues in the memory pipeline:

| Bug | Impact | Fix |
|-----|--------|-----|
| JSON parsing in consolidator | `_parse_json_field` failed on raw arrays `[{...}]` — silently returned 0 facts | Handle raw arrays, alternative keys, BOM prefixes |
| Consolidation token limit | `MAX_TOKENS=4096` too small for fact extraction JSON → empty response | Added `max_tokens=8192` for consolidation calls |
| Entity matching in retriever | Substring match: "corp" in "RetailMax Corp." matched "TechCorp" | Tokenized word matching with `len(w) > 3` filter |
| Recency calculation | `max(current - source, 0)` gave future sessions recency=1.0 | Changed to `abs(current - source)` |
| Semantic importance | Retriever used `importance_score` but semantic store has `confidence` | Added `elif mem_type == "semantic"` branch |
| Type diversity | After scoring fixes, semantic facts dominated all 8 slots | Diversified selection: guarantee 1 slot per type |

## How Memory Flows Through the System

```
Session N starts
    │
    ├─→ MemoryManager.retrieve(task, phase="planning")
    │       │
    │       ├─→ Gather candidates from all enabled stores
    │       ├─→ Retriever.score_memories() — 4-signal scoring
    │       ├─→ Diversified selection (1+ per type)
    │       └─→ Returns ranked list (max 8 items, max 2000 tokens)
    │
    ├─→ PromptBuilder assembles system prompt
    │       │
    │       └─→ [Known Facts]
    │           [Past Experiences]
    │           [Learned Strategies]
    │           [Lessons & Insights]
    │
    ├─→ Agent loop (tool calls + final answer)
    │
    └─→ Consolidator.process(trajectory)
            │
            ├─→ _extract_lessons()     → reflective store
            ├─→ _extract_procedures()  → procedural store
            ├─→ _extract_facts()       → semantic store (34 facts from Session 1!)
            └─→ _compress_episode()    → episodic store
```

## Configuration

Key settings in `config/settings.py`:

```python
MODEL = "stepfun/step-3.5-flash"      # 196B MoE, 256K context
MAX_TOKENS = 4096                       # Agent calls
TEMPERATURE = 0.3
MAX_MEMORIES_PER_RETRIEVAL = 8
MAX_MEMORY_TOKENS = 2000
RETRIEVAL_WEIGHTS = {
    "relevance": 0.4,
    "importance": 0.3,
    "recency": 0.2,
    "type_match": 0.1,
}
```

## Next Steps

- [ ] Run full 100-session experiment across all 3 conditions
- [ ] Add embedding-based similarity (sentence-transformers) to replace bag-of-words
- [ ] Implement memory decay / forgetting for long-running experiments
- [ ] Add a 4th experiment condition: semantic-only memory
- [ ] Test with different models (Claude, GPT-4o, Llama) to see if findings generalize
- [ ] Build the interactive dashboard visualization

## License

Experimental research project. Use freely for learning and research.
