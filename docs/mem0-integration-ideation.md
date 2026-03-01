# Mem0 + Memory Observatory: Integration Ideation

> Analysis date: 2026-03-01
> Status: Ideation only — no code changes

## What Mem0 Brings vs What Observatory Already Has

| Capability | Observatory (current) | Mem0 |
|---|---|---|
| **Extraction** | 4 separate LLM calls post-session (lessons, procedures, facts, episodes) | Single pipeline: LLM extracts facts from conversation pairs on-the-fly |
| **Storage** | SQLite (4 typed tables) | Vector DB (Qdrant) + optional Graph DB (Neo4j) |
| **Retrieval** | Bag-of-words cosine + 4-signal scoring | Embedding similarity (text-embedding-3-small) + optional graph traversal |
| **Deduplication** | Semantic store checks (entity, attribute) pairs | LLM-guided: ADD / UPDATE / DELETE / NOOP per fact |
| **Conflict resolution** | Overwrites on match | LLM reasons about contradictions, marks old facts invalid |
| **Memory types** | Explicit 4 types (episodic, semantic, procedural, reflective) | Flat facts + optional graph entities/relationships |
| **Scoping** | Session-based (session_id) | User / agent / run_id based |

## Key Tension

The two systems have **fundamentally different philosophies**:

- **Observatory**: Typed memory with structured extraction. The agent knows *what kind* of memory it's storing (a fact vs a strategy vs a lesson). Retrieval is phase-aware (planning favors procedural, execution favors semantic).

- **Mem0**: Flat memory with intelligent retrieval. Everything is a "memory" (a text fact with an embedding). The intelligence is in extraction/deduplication, not in type-based routing. Graph memory adds relational structure but not cognitive categories.

## Three Integration Angles

### 1. Mem0 as a New Experiment Condition (Cleanest)

Add a 4th condition to the experiment: `mem0_memory`.

```
no_memory          → control (existing)
partial_memory     → episodic only (existing)
with_memory        → full 4-type system (existing)
mem0_memory        → Mem0 handles all memory (NEW)
```

**Why this is interesting**: Direct apples-to-apples comparison on the same 5 (or 100) sessions. Same agent, same tasks, same scoring — just swap the memory backend. This answers: *does a production memory system outperform a hand-crafted typed system?*

**What you'd measure**:
- Quality scores (does Mem0's embedding retrieval find better memories?)
- Token overhead (Mem0 extracts per-turn vs Observatory's batch consolidation)
- Memory growth (Mem0's dedup vs Observatory's 49 memories in 5 sessions)
- Cost (Mem0 needs OpenAI for embeddings + extraction LLM calls)

**Challenge**: Mem0 expects conversation-style `add()` calls, not post-session batch consolidation. You'd need to feed it the full trajectory as messages.

### 2. Hybrid — Mem0 for Retrieval, Keep Typed Storage (Most Interesting)

Keep the Observatory's 4-type consolidation pipeline (it works well — 34 semantic facts from Session 1). But **replace the bag-of-words retriever with Mem0's embedding search**.

Current retrieval is the weakest link — bag-of-words cosine similarity misses semantic relationships. The README already lists "Add embedding-based similarity" as a next step. Mem0 gives you that for free.

**How it would work**:
- After consolidation, `store` each extracted memory into Mem0 via `memory.add()` with metadata tags for type (episodic/semantic/procedural/reflective)
- At retrieval time, `memory.search(context)` returns embedding-ranked results
- Layer the Observatory's existing 4-signal scoring *on top* of Mem0's relevance scores (importance, recency, type_match still applied)

**What you'd gain**:
- Real embedding similarity instead of bag-of-words
- Mem0's built-in deduplication/conflict resolution for semantic facts
- Graph memory (Mem0g) could naturally represent company→metric relationships (TechCorp→debt_to_equity→1.81x becomes a graph triple)

**What you'd preserve**:
- Phase-aware type weighting (Mem0 has no concept of "planning needs procedural memories")
- The Observatory's consolidation quality (4 focused LLM calls > 1 generic extraction)
- Experiment framework, scoring, tracing

### 3. Mem0g for Entity Knowledge, Observatory for Everything Else (Most Targeted)

The Observatory's semantic store is entity-attribute-value triples. Mem0g is literally a graph of entities and relationships. This is a natural fit.

**Replace only the semantic store with Mem0g**:
- Consolidator still extracts facts, but stores them as graph triples via Mem0g
- Retrieval for semantic facts uses graph traversal ("give me all facts about TechCorp" = node lookup + edge traversal)
- Episodic, procedural, reflective stores stay SQLite-backed

**Why**: The Observatory already discovered that semantic facts were the most impactful memory type (Session 4 went from 2.0 → 10.0 with semantic facts). Graph memory could make entity retrieval even better — e.g., "compare TechCorp vs HealthCo debt" would traverse both entity subgraphs and return all connected metrics.

## Practical Considerations

**Cost**: Mem0 defaults to OpenAI for extraction + embeddings. The Observatory currently runs on StepFun at $0.01/experiment. Adding Mem0 adds:
- Embedding calls (text-embedding-3-small: $0.02/M tokens — cheap)
- Extraction LLM calls (gpt-4.1-nano — cheap)
- Graph DB if using Mem0g (Neo4j Aura free tier exists)

**Dependency weight**: Mem0 pulls in `openai`, vector store client, and optionally Neo4j. The Observatory is currently dependency-light (just `openai` for OpenRouter).

**The LLM question**: Mem0 uses its own LLM calls for extraction/dedup. The Observatory's consolidator also uses LLM calls. Running both means double the extraction overhead. Need to pick one or the other for extraction, not both.

**Scoping mismatch**: Mem0 scopes by `user_id` / `agent_id`. The Observatory scopes by `session_id` and needs cross-session retrieval. You'd map `user_id` → experiment run, and `session_id` → `run_id`.

## Recommended Order

1. **Start with Angle 1** (Mem0 as 4th experiment condition) — lowest effort, highest learning. Just wrap Mem0's API in a `MemoryManager`-compatible interface, run the same 5 sessions, compare scores. This tells you immediately whether Mem0's approach beats the handcrafted one.

2. **Then try Angle 3** (Mem0g for semantic store only) — if Angle 1 shows Mem0 is competitive, the graph representation for entity facts is the highest-value targeted integration.

3. **Angle 2** (hybrid retrieval) is the most architecturally interesting but the most work. Save it for after you have data from 1 and 3.

## Open Questions

- **Does typed memory matter?** Mem0 stores flat facts. The Observatory's phase-aware retrieval (planning→procedural, execution→semantic) is a differentiator. If Mem0 performs equally well without types, that's a finding. If it performs worse, types matter.
- **Batch vs streaming extraction?** Mem0 extracts per-turn. Observatory consolidates post-session. Which produces higher quality memories? Could measure this directly.
- **Graph vs flat for financial data?** Investment analysis is highly relational (company→metric→value→time_period). Mem0g might shine here specifically because the domain is entity-rich.
- **Who resolves conflicts better?** Mem0's LLM-guided ADD/UPDATE/DELETE vs Observatory's simple (entity, attribute) dedup. Especially relevant when a metric changes across sessions.

## References

- [Mem0 Paper (arXiv)](https://arxiv.org/abs/2504.19413)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)
- [Mem0 Python Quickstart](https://docs.mem0.ai/open-source/python-quickstart)
- [Mem0 Graph Memory Docs](https://docs.mem0.ai/open-source/features/graph-memory)
- [Mem0 Architecture Deep Dive (Medium)](https://medium.com/@zeng.m.c22381/mem0-overall-architecture-and-principles-8edab6bc6dc4)
- [AWS + Mem0 Integration Guide](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
