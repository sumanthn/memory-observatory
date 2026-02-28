# Agentic Memory Systems: Open-Source Landscape Survey

**Project**: Memory Observatory
**Date**: February 28, 2026
**Purpose**: Survey of open-source projects dedicated to persistent memory for AI agents — what exists, how they work, and where our project fits.

---

## Tier 1: Major Purpose-Built Agent Memory Frameworks

### 1. Mem0 — 48.3k stars, $24M Series A (YC-backed)
- **GitHub**: [github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)
- **Memory Types**: User memory, Session memory, Agent memory (multi-level). Semantic via vector store, relational via graph store, key-value memory.
- **Storage Backends**: 20+ vector stores (Qdrant, ChromaDB, Pinecone, pgvector, Redis, Milvus, Azure AI Search), graph backends (Neo4j, MemGraph, Kuzu, Neptune), key-value stores.
- **Retrieval**: Hybrid search across vector, key-value, and graph stores. Vector similarity with optional MMR-based reranking. Scores on relevance, importance, and recency.
- **Consolidation**: Yes. Claims 80% prompt token reduction. Deduplication and merging.
- **Architecture**: Modular, API-first. Managed cloud and self-hosted open-source (Apache 2.0). Python and TypeScript SDKs.
- **Scale**: Production-ready. 186M API calls/quarter in Q3 2025. AWS chose Mem0 as exclusive memory provider for their Agent SDK. 80K+ developers on cloud.
- **Key Differentiator**: Most widely adopted standalone memory layer. Started vector-only, added graph memory as field matured — validates that vector alone isn't enough.

### 2. Letta (formerly MemGPT) — 21.3k stars
- **GitHub**: [github.com/letta-ai/letta](https://github.com/letta-ai/letta)
- **Memory Types**: Four tiers inspired by OS virtual memory:
  - Core Memory — editable in-context memory (mutable system prompt, ~2K chars)
  - Recall Memory — full conversation log
  - Archival Memory — vector DB for long-term overflow
  - External Data Sources attached to archival
- **Storage Backends**: PostgreSQL (production), SQLite (default).
- **Retrieval**: Agent self-manages retrieval. The agent decides when to read/write to archival or recall memory using tool calls (`core_memory_append`, `core_memory_replace`, `archival_memory_insert`).
- **Consolidation**: Agents actively self-edit memory blocks. When context fills up, agents decide what to persist vs. keep.
- **Architecture**: Full agent runtime platform, not just a memory library. REST API with Python/TypeScript SDKs.
- **Scale**: Production-ready. Commercial offering for enterprise.
- **Key Differentiator**: The seminal MemGPT paper (2023) defined the field. Only system where the agent itself manages its own memory using tool calls. The agent autonomously decides what to remember, forget, and archive.

### 3. Graphiti (by Zep) — 23.2k stars
- **GitHub**: [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- **Memory Types**: Temporal knowledge graph with entities, episodes, communities, sagas, and relationships. Bi-temporal model tracking both event-occurrence time and ingestion time.
- **Storage Backends**: Neo4j 5.26+, FalkorDB 1.1.2+, Kuzu 0.11.2+, Amazon Neptune. Full-text search via OpenSearch or native DB.
- **Retrieval**: Hybrid — semantic embeddings + keyword search (BM25) + graph traversal. Sub-200ms latency. Point-in-time historical queries.
- **Consolidation**: Continuous incremental updates without full graph recomputation. Community detection and saga formation.
- **Architecture**: Modular driver abstraction. Apache 2.0. Powers commercial Zep platform.
- **Scale**: Production-ready. 25K+ weekly PyPI downloads.
- **Key Differentiator**: Leading temporal knowledge graph for agents. Preserves relationships AND time — enables queries like "what did the user believe about X before date Y?" Zep Community Edition deprecated in favor of Graphiti as open-source core.

### 4. Cognee — 12.6k stars, $7.5M seed
- **GitHub**: [github.com/topoteretes/cognee](https://github.com/topoteretes/cognee)
- **Memory Types**: Combines vector search (semantic) and knowledge graph (relational). Multi-modal: conversations, documents, images, audio.
- **Storage Backends**: LanceDB (default vector), PGVector, Redis, FalkorDB. KuzuDB (default graph), Neo4j, Neptune. PostgreSQL/SQLite (relational). 30+ data source connectors.
- **Retrieval**: GraphRAG — retrieval augmented by knowledge graph relationships. Combines semantic similarity with graph traversal.
- **Consolidation**: ECL pipeline (Extract, Cognify, Load) transforms raw data into structured knowledge graphs.
- **Architecture**: Modular pipeline design. Apache 2.0.
- **Key Differentiator**: Knowledge engine, not just storage. Multi-modal support (text, images, audio). "Memory in 6 lines of code."

### 5. MemOS — 6k stars
- **GitHub**: [github.com/MemTensor/MemOS](https://github.com/MemTensor/MemOS)
- **Memory Types**: Text memory, multi-modal memory (images/charts), tool memory (for agent planning), skill memory (cross-task reuse), persona memory.
- **Storage Backends**: Neo4j (graph), Qdrant (vector), Redis Streams (scheduling/queuing), PostgreSQL.
- **Retrieval**: Unified Memory API with inspectable graph. Combined vector and graph search.
- **Consolidation**: Memory feedback mechanism for natural-language refinement.
- **Architecture**: "Memory Operating System" metaphor. MemScheduler for async ingestion.
- **Scale**: v2.0 "Stardust" released Dec 2025. Claims to outperform Mem0, Zep, and Memobase on benchmarks.
- **Key Differentiator**: First to propose memory as an OS-level primitive. Skill memory for cross-task reuse is unique. Multi-modal memory support.

### 6. OpenMemory — 3.5k stars
- **GitHub**: [github.com/CaviraOSS/OpenMemory](https://github.com/CaviraOSS/OpenMemory)
- **Memory Types**: Five cognitive sectors: Episodic (events), Semantic (facts), Procedural (skills), Emotional (feelings), Reflective (insights).
- **Storage Backends**: SQLite (default, local-first), PostgreSQL.
- **Retrieval**: Composite scoring based on salience, recency, and coactivation. Adaptive decay engine. Explainable recall traces.
- **Consolidation**: Hierarchical Memory Decomposition with temporal graph overlay. Sector classification routes memories automatically.
- **Architecture**: Local-first, privacy-focused. Native MCP server. MIT License.
- **Scale**: Growing rapidly. Ships migration tools from Mem0, Zep, Supermemory.
- **Key Differentiator**: Most cognitively-inspired architecture. Five memory sectors mirror human cognitive science. **Closest peer to our Memory Observatory** — same 4 of 5 types, SQLite storage, composite scoring.

### 7. LangMem — 1.3k stars
- **GitHub**: [github.com/langchain-ai/langmem](https://github.com/langchain-ai/langmem)
- **Memory Types**: "Hot path" (agent manages during conversation) and "Background" (automatic extraction/consolidation).
- **Storage Backends**: InMemoryStore (dev), AsyncPostgresStore (production), any LangGraph BaseStore.
- **Retrieval**: Semantic similarity via embeddings. Vector search with namespace scoping.
- **Consolidation**: Background manager extracts, updates, removes, and consolidates memories. Includes prompt optimizers that refine agent behavior.
- **Architecture**: Library for LangGraph ecosystem. Python only.
- **Key Differentiator**: Dual hot-path/background approach. Unique prompt optimization — actively refines agent prompts based on learned patterns.

---

## Tier 2: Memory Within Larger Agent Frameworks

### 8. CrewAI — 44.8k stars (whole framework)
- **GitHub**: [github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
- **Memory Types**: Short-term (Chroma/RAG), Long-term (SQLite3), Entity (RAG), Contextual, User memory.
- **Storage**: ChromaDB via EmbedChain + SQLite3 + Mem0 integration.
- **Key Differentiator**: Multi-agent shared memory. Memory auto-shared across crew members.

### 9. AutoGPT — 182k stars (whole framework)
- **GitHub**: [github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
- **Memory Types**: Short-term (recent messages), Long-term (vector embeddings).
- **Storage**: Deliberately dropped all vector DBs in favor of JSON file storage. "Less is more."
- **Key Differentiator**: Historical significance — first autonomous agent with memory. Simplified memory by removing vector DBs.

### 10. Mastra — 21.5k stars (whole framework)
- **GitHub**: [github.com/mastra-ai/mastra](https://github.com/mastra-ai/mastra)
- **Memory Types**: Observational Memory — novel text-based type. Two background agents (Observer + Reflector) watch conversations and maintain dense observation log.
- **Storage**: **No vector DB. No graph DB. No embeddings.** Pure text compression. Compatible with prompt caching.
- **Consolidation**: Core mechanism. Raw history continuously compressed into observation log. 5-40x compression on tool outputs.
- **Scale**: v1.2.0 Feb 2026. 94.87% on LongMemEval (state-of-the-art).
- **Key Differentiator**: Challenges the entire structured memory premise. Proves pure text compression by observer/reflector agents can outperform traditional approaches. Simpler and cheaper.

---

## Tier 3: Smaller / Research / Deprecated

### 11. A-Mem — 802 stars (NeurIPS 2025)
- **GitHub**: [github.com/WujiangXu/A-mem](https://github.com/WujiangXu/A-mem)
- Zettelkasten-inspired structured notes with cross-links. Agent decides how to organize and refine.

### 12. Motorhead — 909 stars (DEPRECATED)
- **GitHub**: [github.com/getmetal/motorhead](https://github.com/getmetal/motorhead)
- Standalone Rust memory server. Redis + RediSearch. Incremental summarization. No longer maintained.

### 13. Memobase — 2.6k stars
- **GitHub**: [github.com/memodb-io/memobase](https://github.com/memodb-io/memobase)
- User-profile-centric. PostgreSQL + Redis. Top-tier on LOCOMO benchmark.

### 14. Memary — 2.6k stars
- **GitHub**: [github.com/kingjulio8238/Memary](https://github.com/kingjulio8238/Memary)
- Knowledge-graph-first. Neo4j. Recursive subgraph retrieval with multi-hop reasoning.

### 15. Microsoft Kernel Memory — 2.1k stars
- **GitHub**: [github.com/microsoft/kernel-memory](https://github.com/microsoft/kernel-memory)
- C# / .NET ecosystem. Plugin for Semantic Kernel and Microsoft Copilot. No production support.

---

## Key Trends (Late 2025 / Early 2026)

### 1. Graph memory is ascendant
The field is moving from pure vector search toward knowledge graphs. Mem0 added graph memory. Graphiti is built on it. Cognee, MemOS, Memary all use graph backends. Vector alone isn't enough — you need relational structure.

### 2. Consolidation is table stakes
Every serious project does it. Mem0 claims 80% compression. Letta has self-editing. Mastra does observational compression. Graphiti does incremental graph updates.

### 3. Storage is hybrid
Nobody uses just one backend anymore. The pattern:
```
Vector DB     → fuzzy semantic search ("find relevant memories")
Graph DB      → relational queries ("how are these entities connected?")
Relational DB → structured lookups ("get TechCorp's debt_to_equity")
```

### 4. MCP is the integration layer
OpenMemory, MemOS, Graphiti ship native MCP servers. Memory is becoming plug-and-play for any AI tool.

### 5. Two schools of thought
- **Structured extraction** (our approach, Mem0, OpenMemory): Parse memories into typed schemas
- **Observational compression** (Mastra, Letta): Let agents self-manage what to remember via natural language

### 6. Benchmarking is maturing
LOCOMO and LongMemEval are standard benchmarks. Mastra achieved 94.87% on LongMemEval. Mem0 published peer-reviewed LOCOMO results.

---

## Where Memory Observatory Fits

Our closest peer is **OpenMemory** — same cognitive memory types, SQLite storage, composite scoring. But we have something none of them have: **a controlled experiment platform that measures whether memory actually works**.

Everyone builds memory systems. Nobody proves they help with controlled experiments.

We showed:
- Session 4 goes from **2/10 to 10/10** with memory
- Semantic extraction reduces tool calls by **36%** (11 steps → 7)
- Full memory eliminates **catastrophic failures** (20% failure rate → 0%)
- Consolidation costs **$0.0005/session** — negligible

The Memory Observatory isn't trying to be a memory framework. It answers: **does any of this actually matter?**

---

## Ideas to Steal

| From | Idea | Relevance to Us |
|------|------|----------------|
| **Letta** | Agent self-manages memory via tool calls | Could add `store_fact` and `recall` as agent tools instead of post-hoc extraction |
| **Graphiti** | Bi-temporal model (event time + ingestion time) | We track `source_session` but not when facts were *discovered* vs *stored* |
| **Mastra** | Observational compression (no embeddings) | Could add as a 4th experiment condition — text-only memory vs structured types |
| **OpenMemory** | Adaptive decay engine | Better than our fixed recency weight — decay rate could adapt based on access patterns |
| **Mem0** | Graph memory alongside vector memory | Validates our Redis + MemGraph architecture proposal |
| **Cognee** | ECL pipeline (Extract, Cognify, Load) | Structured pipeline vs our monolithic consolidator — more testable |
| **MemOS** | Skill memory for cross-task reuse | Our procedural memory is close but doesn't explicitly model reusable skills |
| **A-Mem** | Zettelkasten cross-linking | Memories that reference other memories — provenance tracking |

---

## Further Reading

- [Mem0 Research Paper (arXiv)](https://arxiv.org/abs/2504.19413)
- [MemGPT Paper — Operating System for LLMs (2023)](https://arxiv.org/abs/2310.08560)
- [Zep/Graphiti Architecture Paper (arXiv)](https://arxiv.org/html/2501.13956v1)
- [A-Mem: Zettelkasten Agent Memory (NeurIPS 2025)](https://arxiv.org/abs/2502.12110)
- [Mastra Observational Memory Research](https://mastra.ai/research/observational-memory)
- [Survey of AI Agent Memory Frameworks — Graphlit](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)
- [Why AutoGPT Ditched Vector Databases](https://dariuszsemba.com/blog/why-autogpt-engineers-ditched-vector-databases/)
