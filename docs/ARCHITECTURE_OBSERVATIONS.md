# Architecture Observations: Models & Strategies for Memory Extraction

**Project**: Memory Observatory
**Date**: February 28, 2026
**Context**: After building and testing the 4-type memory system with live LLM calls, we explored the design space for how agents should extract, store, and retrieve persistent memory.

---

## The Core Question

The current system uses **one approach**: the same LLM (StepFun Step 3.5 Flash) performs both the research task AND the memory extraction. After finishing its task, it reviews its own trajectory in 4 separate calls and produces structured JSON for each memory type.

But this is just one point in a large design space. Below we analyze 6 fundamentally different approaches, argue for and against each, and propose a hybrid architecture.

---

## Approach 1: Same Model Extracts Its Own Memory (Current)

**How it works**: Agent finishes task → same LLM reviews its trajectory → extracts facts, strategies, lessons, episode summary via 4 prompted calls.

**The case for it:**
- The model understands its own reasoning. It knows *why* it made certain tool calls, what surprised it, what felt important. This is especially valuable for reflective memory — only the "thinker" truly knows what it learned.
- Consistency. The same model that produced the analysis extracts the memory, so there's no interpretation gap.
- Simple architecture. One model, one API, one set of credentials.

**The case against it:**
- **Self-reinforcement loop.** The model reviews its own work and says "I did great, here are my brilliant lessons." It may not recognize its own blind spots. If it missed a red flag during research, it won't extract a lesson about missing it — because it doesn't know it missed it.
- **Hallucination during extraction.** We saw this: the model can fabricate facts that weren't in the trajectory. When it's extracting 34 semantic facts, some could be confabulated from its training data rather than the actual tool outputs.
- **Cost multiplication.** 4 extra LLM calls per session. With a cheap model like Step Flash ($0.0005/session) this is fine. With Claude Opus or GPT-4, this becomes $0.05-0.50 per session — a 10-100x increase.

**Verdict**: Good for research prototypes. The self-reinforcement risk is real but manageable at small scale.

---

## Approach 2: Smaller/Cheaper Model for Consolidation

**How it works**: Use a capable model (Claude Sonnet, GPT-4o) for the agent loop, but a cheap model (Haiku, GPT-4o-mini, Step Flash) for memory extraction.

**The case for it:**
- Massive cost savings. The consolidation prompts are relatively straightforward — "extract facts from this text as JSON" doesn't require frontier reasoning.
- Speed. Smaller models are faster, so consolidation doesn't block the next session.
- The extraction task is simpler than the research task. You don't need a senior analyst to take notes — a junior can do it.

**The case against it:**
- Quality gap on nuanced extraction. A smaller model might miss the *significance* of a fact. It'll extract "debt-to-equity: 1.81x" but might not add the crucial context "significantly exceeds tech sector median ~0.9x."
- Procedural and reflective extraction genuinely benefit from reasoning ability. Extracting "WHEN you see a covenant breach, THEN check waiver terms" requires understanding causal relationships in the trajectory.
- Two models to manage, test, and handle failure modes for.

**Verdict**: Probably the best default for production. Use the big model where reasoning matters (agent loop), cheap model where pattern extraction matters (consolidation). The quality difference on fact extraction is minimal — the facts are literally in the tool output text.

---

## Approach 3: No LLM for Facts — Extract Directly from Tool Outputs

**How it works**: Instead of asking the LLM to extract facts post-hoc, intercept the tool outputs at execution time and parse them directly. The tools already return structured data.

For example, when `financial_lookup(TechCorp, all_financials)` returns:
```
Revenue: $4.2B (+3.1% YoY)
Net Income: $380M
Debt-to-Equity: 1.81x
```

...just regex-parse those into semantic memory immediately. No LLM call needed.

**The case for it:**
- **Zero hallucination.** The facts come directly from the source data. The LLM can't fabricate numbers it never saw.
- **Zero cost.** No API call, no tokens, instant.
- **Real-time.** Facts are stored as they're discovered, not after the session ends. This means Session 3 could benefit from Session 2's facts even before consolidation runs.
- **Deterministic.** Same input always produces same facts. No variance between runs.

**The case against it:**
- Brittle. Requires custom parsers for each tool's output format. If the format changes, parsers break.
- Misses derived insights. The LLM might observe "Q3 revenue missed by 8.1% — this is the largest miss in 5 years" — a derived fact that isn't in any single tool output.
- Only works for semantic memory. You can't regex-extract procedural strategies or reflective lessons from tool outputs.

**Verdict**: Should be done **in addition to** LLM extraction, not instead of. Capture structured facts at tool execution time (zero cost, zero hallucination), then use LLM extraction for higher-order memories (strategies, lessons, derived insights). This is a hybrid approach that gives the best of both worlds.

---

## Approach 4: Embedding-Based Memory (No Summarization)

**How it works**: Don't summarize at all. Take raw chunks of the trajectory (tool outputs, thoughts, answers) and store them with vector embeddings. At retrieval time, embed the query and find nearest neighbors.

Systems like MemGPT, LangChain Memory, and most RAG pipelines work this way.

**The case for it:**
- No information loss. The raw text is preserved exactly.
- No extraction errors. Nothing is misinterpreted or hallucinated.
- Simple pipeline. Embed → store → retrieve. No prompt engineering for extraction.
- Works immediately. No post-session processing needed.

**The case against it:**
- **Context window waste.** Raw chunks are verbose. A 2000-char tool output becomes a memory item that costs ~500 tokens. Our semantic fact `TechCorp — debt_to_equity: 1.81x` costs ~15 tokens and contains the same key information. That's a **33x efficiency difference**.
- **No structure.** You can't query "what is TechCorp's debt ratio?" — you can only find chunks that are semantically similar to that question. The chunk might contain the answer buried in paragraph 3 of a 2000-char SEC filing extract.
- **Retrieval noise.** Long chunks match many queries because they contain many topics. A chunk about TechCorp's revenue, debt, and CEO transition will match queries about any of those topics, diluting relevance.
- **No cross-session synthesis.** Embedding-based memory doesn't connect facts across sessions. It can't tell you "TechCorp's debt situation got worse between Session 1 and Session 4" because it treats each chunk independently.

**Verdict**: Wrong approach for multi-session agents. It works for single-session RAG (chatbots with long conversations), but for agents that need to *learn and improve* across sessions, you need structured memory that compresses, deduplicates, and connects knowledge.

---

## Approach 5: Knowledge Graph Memory

**How it works**: Instead of flat EAV triples, store facts as a graph with entities as nodes and relationships as edges. Use a graph database (Neo4j) or in-memory graph structure.

```
TechCorp --[has_metric]--> Revenue: $4.2B
TechCorp --[has_CEO]--> Sarah Chen --[replaced]--> Robert Martinez
TechCorp --[breached]--> Debt Covenant --[waiver_until]--> March 2026
HealthCo --[competitor_of]--> TechCorp (implicit from Session 3)
```

**The case for it:**
- **Relational reasoning.** "How are TechCorp and HealthCo related?" → they were compared in Session 3. "Who replaced whom at TechCorp?" → Sarah Chen replaced Robert Martinez.
- **Path queries.** "What risks connect TechCorp's debt to its CEO change?" → leadership transition → delayed renewals → Q3 miss → covenant breach.
- **Natural deduplication.** Entity resolution is built into graph structure.
- **Scales well.** As you add more companies and sessions, the graph captures cross-entity relationships that flat stores miss.

**The case against it:**
- **Complexity.** Building and maintaining a knowledge graph from LLM outputs is hard. Entity resolution ("TechCorp Inc." vs "TechCorp" vs "the company") requires NLP.
- **Extraction is harder.** Going from free text to graph triples is a harder task than extracting flat facts. The LLM needs to identify not just entities and attributes, but relationships between entities.
- **Overkill for small scale.** With 3 companies and 5 sessions, a flat SQLite table works fine. The graph advantage kicks in at 50+ entities.
- **Retrieval is different.** You need graph traversal algorithms, not just cosine similarity. This is a different skill set and infrastructure.

**Verdict**: The right long-term architecture for production agent memory, but premature for a research prototype. The 100-session expansion with 10 companies is the right inflection point to consider it. For now, the EAV triples in SQLite capture 90% of the value at 10% of the complexity.

---

## Approach 6: Hierarchical / Tiered Memory

**How it works**: Different storage tiers with different compression levels, like CPU cache hierarchy.

```
L1: Working Memory    — current session scratchpad (full detail, no persistence)
L2: Recent Memory     — last 3-5 sessions, lightly compressed (episodic summaries + all facts)
L3: Long-term Memory  — older sessions, heavily compressed (key facts only, strategies, lessons)
L4: Archival Memory   — everything ever stored, raw, for forensics/audit
```

As sessions age, memories get progressively compressed. Recent sessions keep full detail; old sessions keep only the most accessed/important items.

**The case for it:**
- Matches how humans work. You remember yesterday in detail, last month in broad strokes, last year in key events only.
- Scales to hundreds of sessions without unbounded growth.
- Naturally prioritizes recent, frequently-accessed knowledge.

**The case against it:**
- Compression is lossy. A fact that seemed unimportant in Session 5 might become critical in Session 50. If it was compressed away, it's gone.
- More complex memory management. Need policies for when/how to compress.
- Our current recency decay in retrieval scoring already achieves a similar effect — old memories score lower and are naturally deprioritized without being deleted.

**Verdict**: The recency signal in our retrieval scorer (`recency weight = 0.2`) already provides soft tiering without data loss. Hard tiering becomes worthwhile at 100+ sessions when storage and retrieval latency become real concerns.

---

## Recommended Hybrid Architecture

If redesigning this system for production:

```
EXTRACTION LAYER (per session):
├── Tool-output parsing (zero cost, zero hallucination)
│   → Semantic facts from structured tool returns
│
├── Cheap model (Haiku / GPT-4o-mini)
│   → Fact extraction from unstructured text (SEC filings, news)
│   → Episode compression
│
└── Same model or slightly better
    → Procedural strategy extraction
    → Reflective lesson extraction
    (these need reasoning ability)

STORAGE LAYER:
├── SQLite for structured data (facts, episodes, strategies, lessons)
├── Vector index (e.g., sqlite-vec or ChromaDB) for embedding-based retrieval
└── Access counters + timestamps for importance/recency signals

RETRIEVAL LAYER:
├── Hybrid scoring: vector similarity + keyword match + structured filters
├── Phase-aware weighting (current approach, works well)
└── Diversified selection (current approach, works well)
```

### Per-Memory-Type Extraction Strategy

The key insight: **different memory types have different extraction difficulty and different error tolerance**.

| Memory Type | Extraction Difficulty | Error Tolerance | Best Extractor |
|---|---|---|---|
| **Semantic** (facts) | Low — facts are in tool outputs | Low — wrong numbers are dangerous | **Tool output parsing** (no LLM) |
| **Episodic** (summaries) | Medium — needs compression | Medium — approximation is OK | **Cheap model** |
| **Procedural** (strategies) | High — needs causal reasoning | Medium — vague strategies still help | **Good model** |
| **Reflective** (lessons) | High — needs meta-cognition | High — wrong lessons are OK to try | **Same model as agent** |

---

## Observations from the Pilot

These architectural observations are grounded in what we actually saw during the 5-session pilot:

1. **The token limit bug was the most impactful finding.** `MAX_TOKENS=4096` caused silent zero-fact extraction. This is a class of bug that any memory system will face — the extraction call itself has resource constraints that can silently truncate output.

2. **Self-extraction works surprisingly well for a cheap model.** Step 3.5 Flash at $0.10/M input produced 34 high-quality semantic facts from a single session. The facts were accurate, well-structured, and useful for downstream retrieval.

3. **The consolidation cost is negligible.** 4 LLM calls for consolidation cost ~$0.0005 per session. Even with 100 sessions across 3 experiments, total consolidation cost is ~$0.15. This means the "same model extracts its own memory" approach has virtually no cost penalty at this model tier.

4. **Hallucination risk is real but bounded.** When extracting 34 facts, some may be confabulated. Mitigations: cross-reference against tool outputs (Approach 3), store confidence scores, and decay importance of unvalidated facts.

5. **The biggest quality improvement came from semantic memory, not from model choice.** Session 4 went from 2/10 to 10/10 not because we used a better model, but because we stored and retrieved the right facts. This suggests **what you store matters more than how you extract it**.

---

## What We'd Change for the 100-Session Run

1. **Add tool-output parsing** (Approach 3) alongside LLM extraction for semantic facts — zero-cost, zero-hallucination baseline.
2. **Add embedding-based retrieval** as a secondary signal alongside bag-of-words cosine similarity — better for fuzzy matching.
3. **Add a 4th experiment condition**: semantic-only memory — isolate the contribution of facts vs episodes vs strategies.
4. **Track extraction accuracy**: compare LLM-extracted facts against ground truth to measure hallucination rate.
5. **Test cross-model extraction**: use the agent's model for research, a cheaper model for consolidation, and compare memory quality.
