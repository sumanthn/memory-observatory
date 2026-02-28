# Memory Types Wiki

This document covers the 4 persistent memory types used in the Memory Observatory, how each is implemented, the exact prompts that extract them, and how they surface in the agent's context.

---

## Overview

The memory system is inspired by human cognitive architecture. Each type captures a different kind of knowledge, is stored differently, and is useful in different situations.

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  EPISODIC   │  │  SEMANTIC   │  │ PROCEDURAL  │  │ REFLECTIVE  │
│ "What       │  │ "What I     │  │ "How to do  │  │ "What I     │
│  happened"  │  │  know"      │  │  things"    │  │  learned"   │
│             │  │             │  │             │  │             │
│ Session     │  │ Entity-     │  │ WHEN-THEN   │  │ Meta-       │
│ summaries   │  │ attribute-  │  │ rules       │  │ cognitive   │
│ with        │  │ value       │  │ with        │  │ lessons     │
│ outcomes    │  │ triples     │  │ success     │  │ with        │
│             │  │             │  │ tracking    │  │ importance  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

### When Each Type Helps

| Situation | Most Useful Memory |
|-----------|-------------------|
| "What was TechCorp's debt ratio?" | **Semantic** — has the exact number |
| "I analyzed this company before" | **Episodic** — has the session summary |
| "How should I approach this analysis?" | **Procedural** — has the strategy |
| "What mistakes should I avoid?" | **Reflective** — has the lesson |

---

## 1. Episodic Memory — "What Happened"

### Concept

Episodic memory stores compressed summaries of past research sessions. Think of it as a diary entry — what the agent did, what it found, and how it turned out. It provides narrative context about prior experiences.

### Schema

```sql
CREATE TABLE episodic (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id        INTEGER,        -- which session produced this
    timestamp         TEXT,            -- when it was created
    task_summary      TEXT,            -- what the task was
    trajectory_summary TEXT,           -- what the agent did
    outcome           TEXT,            -- success / partial / failure
    key_findings      TEXT,            -- JSON array of finding strings
    importance_score  REAL,            -- 0.0 to 1.0
    embedding         BLOB,            -- for future vector search
    access_count      INTEGER DEFAULT 0,
    last_accessed     TEXT
);
```

### Extraction Prompt

After each session, the consolidator compresses the full trajectory into an episode:

```
Summarize this research session into a compact episode summary (under 200 words).

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
{
  "task_summary": "Brief task description",
  "trajectory_summary": "What the agent did and found",
  "outcome": "success/partial/failure",
  "key_findings": ["finding 1", "finding 2", ...]
}
```

### How It Appears in the Agent's Prompt

```
[Past Experiences]
  (from session 1) Session 1: Conduct a thorough financial analysis of
  TechCorp Inc., identifying key strengths, risks, and red flags for an
  investment committee summary.
  Outcome: success
  Key findings: High leverage: Debt-to-equity 1.81x, covenant breach
  (leverage ratio 1.83x vs 1.5x requirement) with temporary waiver until
  March 2026., Leadership transition: New CEO Sarah Chen appointed...
```

### Real Example (from Session 1)

```json
{
  "session_id": 1,
  "task_summary": "Conduct a thorough financial analysis of TechCorp Inc.",
  "trajectory_summary": "Gathered financials, read SEC filings, searched news",
  "outcome": "success",
  "key_findings": [
    "High leverage: Debt-to-equity 1.81x, covenant breach",
    "Leadership transition: New CEO Sarah Chen appointed",
    "Q3 2025 revenue missed estimates by 8.1%",
    "Nova AI partnership securing $200M minimum revenue"
  ],
  "importance_score": 0.7
}
```

### Retrieval Scoring

- **Relevance**: bag-of-words cosine similarity between query and the episode content string
- **Importance**: stored `importance_score` (default 0.7)
- **Recency**: `exp(-0.3 × |current_session - source_session|)`

---

## 2. Semantic Memory — "What I Know"

### Concept

Semantic memory stores factual knowledge as structured entity-attribute-value triples. These are the raw data points — numbers, names, dates, statuses. It's the agent's knowledge base of verified facts.

The key feature is **deduplication**: if the agent discovers the same fact again (same entity + attribute), the store updates the existing record rather than creating a duplicate. This keeps the knowledge base clean.

### Schema

```sql
CREATE TABLE semantic (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity          TEXT,            -- "TechCorp Inc."
    attribute       TEXT,            -- "debt_to_equity"
    value           TEXT,            -- "1.81x"
    context         TEXT,            -- "Significantly exceeds tech sector median ~0.9x"
    source_session  INTEGER,         -- which session discovered this
    confidence      REAL,            -- 0.0 to 1.0 (used as importance in scoring)
    embedding       BLOB,
    last_verified   TEXT,            -- timestamp of last update
    access_count    INTEGER DEFAULT 0
);
```

### Extraction Prompt

After each session, the consolidator extracts all factual knowledge from the trajectory:

```
Extract all factual knowledge discovered during this research session.

TASK: {task}

TRAJECTORY:
{trajectory}

Format as entity-attribute-value triples.
Return as JSON:
{
  "facts": [
    {
      "entity": "Company or subject name",
      "attribute": "The specific metric or property",
      "value": "The value discovered",
      "context": "Additional context (time period, source, etc.)"
    }
  ]
}
```

**Important**: This call uses `max_tokens=8192` (vs 4096 for agent calls). A single session can produce 30+ facts, and the structured JSON easily exceeds 4096 tokens. The original 4096 limit caused the model to hit the ceiling and return empty responses — this was the root cause of zero semantic facts being stored.

### How It Appears in the Agent's Prompt

```
[Known Facts]
  (from session 1) TechCorp Inc. — Revenue (FY2025): $4.2B (Year-over-year increase of 3.1%)
  (from session 1) TechCorp Inc. — Debt-to-Equity (FY2025): 1.81
  (from session 1) TechCorp Inc. — Covenant Status: Technical breach
  (from session 2) HealthCo Ltd. — total_debt: $800M (FY2025)
```

### Real Examples (extracted by LLM from Session 1)

```
TechCorp Inc. — Revenue (FY2025): $4.2B (Year-over-year increase of 3.1%)
TechCorp Inc. — Net Income (FY2025): $380M
TechCorp Inc. — Debt-to-Equity (FY2025): 1.81
TechCorp Inc. — Covenant Status: Technical breach
TechCorp Inc. — CEO Appointment: Sarah Chen (Effective July 1, 2025)
TechCorp Inc. — Q3 2025 Revenue: $1.02B (Missed estimates by 8.1%)
TechCorp Inc. — Strategic Partnership: Partnership with major cloud provider ($200M committed)
TechCorp Inc. — Analyst Downgrade: Morgan Stanley downgraded to 'Equal Weight'
... (34 facts total from one session)
```

### Retrieval Scoring

Semantic facts get special treatment in scoring because they're short (a single fact like "debt_to_equity: 1.81x" has very few words), which penalizes them in bag-of-words cosine similarity compared to longer procedural or episodic memories.

To compensate:
- **Entity boost**: If the entity name (e.g., "TechCorp") appears in the query as whole words (length > 3 chars to avoid false matches like "the"), relevance is boosted: `max(relevance, 0.3) + 0.15`
- **Attribute boost**: If the attribute keywords match query words, `relevance += 0.1`
- **Importance**: Uses the `confidence` field (default 1.0) instead of `importance_score`

### Deduplication

When adding a fact, the store checks if the same `(entity, attribute)` pair already exists (case-insensitive). If so, it updates the value, context, session, and confidence rather than inserting a duplicate. This means facts from later sessions automatically supersede earlier ones.

---

## 3. Procedural Memory — "How To Do Things"

### Concept

Procedural memory stores reusable strategies as WHEN-THEN rules. These are action patterns the agent has learned work well — like heuristics or standard operating procedures. Each rule has a trigger condition (when to apply it) and a strategy (what to do).

The store tracks **success and failure counts**, so strategies that consistently lead to good outcomes score higher during retrieval.

### Schema

```sql
CREATE TABLE procedural (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_condition TEXT,            -- "WHEN a company has a covenant breach..."
    strategy          TEXT,            -- "THEN check waiver terms in SEC filing..."
    success_count     INTEGER DEFAULT 1,
    failure_count     INTEGER DEFAULT 0,
    source_sessions   TEXT,            -- JSON array of session IDs
    embedding         BLOB,
    access_count      INTEGER DEFAULT 0,
    created_at        TEXT
);
```

### Extraction Prompt

After each session, the consolidator derives strategies from what the agent did:

```
Based on this research experience, extract any reusable strategies.

TASK: {task}

TRAJECTORY:
{trajectory}

Format as WHEN-THEN rules. These should be specific enough to be actionable.
Return as JSON:
{
  "procedures": [
    {
      "trigger_condition": "WHEN this situation arises...",
      "strategy": "THEN do this..."
    }
  ]
}
```

### How It Appears in the Agent's Prompt

```
[Learned Strategies]
  (from session 1) WHEN: WHEN conducting a financial analysis of a company
  THEN: THEN collect both annual/quarterly financial metrics and review
  recent SEC filings (10-K, 10-Q) for management discussion, debt covenants,
  and risk factors

  (from session 3) WHEN: WHEN comparing debt risk between multiple companies
  THEN: THEN create a side-by-side table of key debt metrics (total debt,
  debt-to-equity, net debt, cash) and qualitative risk factors for direct
  comparison
```

### Real Examples (extracted from Session 1)

```
WHEN: WHEN initiating a comprehensive financial analysis of a company
THEN: THEN gather key financial metrics for the latest fiscal year
      (revenue, net income, margins, debt ratios, EPS, P/E, R&D spend)

WHEN: WHEN investigating financial health and compliance risks
THEN: THEN review recent SEC filings (10-K and 10-Q) for management
      discussion, debt covenants, and risk factors

WHEN: WHEN a company has a covenant breach or waiver
THEN: THEN treat as a high-priority red flag and quantify the gap
      between actual ratio and covenant limit

WHEN: WHEN forming an investment committee summary
THEN: THEN structure output with executive summary, key metrics,
      red flags, strengths, clear recommendation (with rationale),
      and specific monitoring points for follow-up
```

### Retrieval Scoring

- **Relevance**: bag-of-words cosine similarity (procedural content tends to be long, so it matches well)
- **Importance**: Calculated as `success_count / (success_count + failure_count)` — a success rate
- **Recency**: Same exponential decay as other types

### Success Tracking

When a procedural memory is retrieved and the session ends successfully, `increment_success()` can be called to update the success count and add the session to `source_sessions`. Over time, strategies that consistently help will score higher. Strategies that lead to failures can have their `failure_count` incremented to reduce their score.

---

## 4. Reflective Memory — "What I Learned"

### Concept

Reflective memory stores meta-cognitive lessons — higher-order insights about the agent's own reasoning process. These aren't facts about the world or strategies for action; they're observations about what works, what doesn't, and how to think better.

This is the most "human" memory type. Where procedural memory says "do X when Y", reflective memory says "I noticed that doing X leads to better outcomes because Z."

### Schema

```sql
CREATE TABLE reflective (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson           TEXT,            -- the insight itself
    context          TEXT,            -- what led to this insight
    derived_from     TEXT,            -- JSON array of session IDs
    importance_score REAL,            -- 0.0 to 1.0
    embedding        BLOB,
    access_count     INTEGER DEFAULT 0,
    created_at       TEXT
);
```

### Extraction Prompt

After each session, the consolidator reflects on the entire experience:

```
Review this research trajectory from a financial analysis session.

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
{
  "lessons": [
    {
      "lesson": "The key insight or lesson",
      "context": "What situation or observation led to this lesson",
      "importance_score": 0.0 to 1.0
    }
  ]
}
```

### How It Appears in the Agent's Prompt

```
[Lessons & Insights]
  (from session 1) Lesson: Debt analysis should include maturity schedule:
  Mentioning 'upcoming debt maturities' without specifying amounts and
  timing from SEC filings leaves refinancing risk unquantified.
  Context: The analysis noted high leverage and a Morgan Stanley downgrade
  citing debt concerns, but did not extract the debt maturity breakdown
  from the 10-K, which is essential for assessing liquidity risk.
```

### Real Examples (extracted from Session 1)

```
Lesson: Systematic multi-source data collection ensures comprehensive coverage
Context: The researcher gathered data from financial_lookup, sec_filing,
and news_search, each revealing different aspects of TechCorp's situation.

Lesson: SEC filings are indispensable for uncovering material risks
Context: The 10-K filing revealed the covenant breach and waiver details
that were not visible in the basic financial metrics.

Lesson: Cash flow analysis must be included to assess liquidity
Context: While debt ratios were analyzed, the operating cash flow and
free cash flow were not explicitly examined.

Lesson: Balance strengths and risks to avoid bias
Context: The analysis separately listed strengths and risks, leading to
a nuanced view rather than a one-sided conclusion.
```

### Retrieval Scoring

- **Relevance**: bag-of-words cosine similarity
- **Importance**: The LLM assigns an `importance_score` (0.0-1.0) during extraction, reflecting how significant the lesson is
- **Recency**: Same exponential decay

---

## How Memories Flow Through the System

### Phase 1: Research (Agent Loop)

```
Task arrives → Retrieve memories → Build prompt → Call LLM → Tool/Answer → Repeat
```

At each step, the orchestrator retrieves up to 8 memories (max 2000 tokens) from all enabled stores. The retrieval is **phase-aware**:

| Phase | When | Favors |
|-------|------|--------|
| **Planning** | Steps 1-2 | Procedural (0.4) > Reflective (0.3) > Semantic (0.2) > Episodic (0.1) |
| **Execution** | Steps 3+ | Semantic (0.4) > Episodic (0.3) > Procedural (0.2) > Reflective (0.1) |
| **Review** | Post-task | Reflective (0.5) > Semantic (0.2) = Episodic (0.2) > Procedural (0.1) |

This means early in a session, the agent gets strategies and lessons ("how to approach this"). Later, it gets facts and experiences ("what do I know about this company").

### Phase 2: Consolidation (Post-Session)

After the agent finishes, the consolidator makes 4 LLM calls:

```
1. REFLECT    → Extract lessons        → reflective store
2. PROCEDURES → Extract WHEN-THEN rules → procedural store
3. FACTS      → Extract EAV triples    → semantic store
4. COMPRESS   → Summarize episode      → episodic store
```

All 4 calls use `max_tokens=8192` and receive the full trajectory as input. The system prompt for each call includes "Return valid JSON only" to keep responses parseable.

### Phase 3: Prompt Injection

Retrieved memories are formatted into the system prompt, grouped by type with human-readable labels:

```
=== Relevant Memories from Prior Sessions ===

[Known Facts]
  (from session 1) TechCorp Inc. — Revenue: $4.2B (FY2025)
  (from session 2) HealthCo Ltd. — total_debt: $800M (FY2025)

[Past Experiences]
  (from session 3) Session 3: Compare TechCorp and HealthCo...

[Learned Strategies]
  (from session 1) WHEN: ... THEN: ...

[Lessons & Insights]
  (from session 1) Lesson: ... Context: ...
```

---

## Retrieval Scoring Deep Dive

All memories go through the same 4-signal scoring formula:

```
score = 0.4 × relevance + 0.3 × importance + 0.2 × recency + 0.1 × type_match
```

### Signal 1: Relevance (weight: 0.4)

Bag-of-words cosine similarity between the query text and the memory's `content` string.

**Problem**: Short semantic facts ("debt_to_equity: 1.81x") get low cosine similarity compared to long procedural memories with many matching words.

**Fix**: Semantic facts get boosted if:
- Entity name appears in query (e.g., "TechCorp" in query matches "TechCorp Inc." entity): `+0.15` plus a floor of `0.3`
- Attribute keywords match query words (e.g., "debt" in both): `+0.1`

### Signal 2: Importance (weight: 0.3)

Source depends on memory type:
- **Episodic**: stored `importance_score` (default 0.7)
- **Semantic**: `confidence` field (default 1.0)
- **Procedural**: `success_count / (success_count + failure_count)` — a success rate
- **Reflective**: LLM-assigned `importance_score` (0.0-1.0)

### Signal 3: Recency (weight: 0.2)

Exponential decay by session distance:

```python
sessions_ago = abs(current_session_id - source_session)
recency = exp(-0.3 × sessions_ago)
```

| Sessions ago | Recency score |
|-------------|--------------|
| 0 (same session) | 1.000 |
| 1 | 0.741 |
| 2 | 0.549 |
| 3 | 0.407 |
| 5 | 0.223 |
| 10 | 0.050 |

### Signal 4: Type Match (weight: 0.1)

Phase-aware bonus for the "right" memory type at the right time. During planning, procedural memories get 0.4; during execution, semantic facts get 0.4.

### Diversified Selection

After scoring, a two-pass selection ensures type diversity:

1. **First pass**: Take the top-scoring memory from each available type (guarantees at least 1 per type)
2. **Second pass**: Fill remaining slots (up to 8 total, 2000 token budget) by score regardless of type

This prevents scenarios where one dominant type crowds out all others.

---

## Memory Counts: What a Session Produces

From a single Session 1 run (TechCorp research):

| Type | Count | Examples |
|------|-------|---------|
| Episodic | 1 | Session summary with 6 key findings |
| Semantic | 34 | Revenue, debt, CEO, covenant, quarterly results, guidance, partnerships... |
| Procedural | 10 | Strategies for financial analysis, SEC filing review, report structure... |
| Reflective | 6 | Lessons about multi-source data, SEC importance, cash flow analysis... |
| **Total** | **51** | |

Over multiple sessions, the semantic store grows fastest (30+ facts per company researched), while procedural and reflective memories plateau as the agent learns the same general strategies.

---

## Implementation Files

| File | Role |
|------|------|
| `memory/episodic_store.py` | SQLite CRUD for episodes |
| `memory/semantic_store.py` | SQLite CRUD for facts + deduplication |
| `memory/procedural_store.py` | SQLite CRUD for strategies + success tracking |
| `memory/reflective_store.py` | SQLite CRUD for lessons |
| `memory/memory_manager.py` | Central coordinator — routes storage and retrieval |
| `memory/retriever.py` | 4-signal scoring + diversified selection |
| `memory/consolidator.py` | Post-session LLM calls to extract all 4 types |
| `core/prompt_builder.py` | Formats memories into the agent's system prompt |
| `config/settings.py` | Retrieval weights, phase weights, limits |
