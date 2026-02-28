"""
Memory Manager — Central coordinator for all memory operations

Controls which memory types are active and provides a unified interface
for retrieval and storage across all stores.
"""

from memory.episodic_store import EpisodicStore
from memory.semantic_store import SemanticStore
from memory.procedural_store import ProceduralStore
from memory.reflective_store import ReflectiveStore
from memory.retriever import Retriever


class MemoryManager:
    def __init__(
        self,
        db_path: str,
        enabled_stores: list[str] | None = None,
    ):
        """
        Initialize memory manager with configurable stores.

        Args:
            db_path: Path to the SQLite database file
            enabled_stores: Which memory types are active.
                - Full memory: ["episodic", "semantic", "procedural", "reflective"]
                - Partial (episodic only): ["episodic"]
                - No memory: [] or None
        """
        self.db_path = db_path
        self.enabled_stores = enabled_stores or []
        self.current_session_id = 1

        # Initialize only enabled stores
        self.stores = {}
        if "episodic" in self.enabled_stores:
            self.stores["episodic"] = EpisodicStore(db_path)
        if "semantic" in self.enabled_stores:
            self.stores["semantic"] = SemanticStore(db_path)
        if "procedural" in self.enabled_stores:
            self.stores["procedural"] = ProceduralStore(db_path)
        if "reflective" in self.enabled_stores:
            self.stores["reflective"] = ReflectiveStore(db_path)

        self.retriever = Retriever(current_session_id=self.current_session_id)

    def set_session(self, session_id: int):
        """Update current session for recency scoring."""
        self.current_session_id = session_id
        self.retriever.current_session_id = session_id

    def retrieve(self, task_context: str, phase: str = "planning") -> list[dict]:
        """
        Retrieve ranked memories relevant to current context.

        Args:
            task_context: The current task or query text
            phase: One of 'planning', 'execution', 'review'
                   Affects type weighting in scoring.

        Returns:
            List of scored memory dicts with content, type, score, and breakdown.
        """
        if not self.enabled_stores:
            return []

        # Gather candidates from all enabled stores
        candidates = []
        for store_name, store in self.stores.items():
            memories = store.get_all()
            candidates.extend(memories)

        if not candidates:
            return []

        # Score and rank via retriever
        ranked = self.retriever.score_memories(candidates, task_context, phase)

        # Increment access counts for retrieved memories
        for memory in ranked:
            mem_type = memory.get("memory_type")
            mem_id = memory.get("id")
            if mem_type in self.stores and mem_id:
                self.stores[mem_type].increment_access(mem_id)

        return ranked

    def store_episode(
        self,
        session_id: int,
        task_summary: str,
        trajectory_summary: str,
        outcome: str,
        key_findings: list[str],
        importance_score: float = 0.7,
    ) -> int | None:
        """Store a compressed episode."""
        if "episodic" not in self.stores:
            return None
        return self.stores["episodic"].add(
            session_id=session_id,
            task_summary=task_summary,
            trajectory_summary=trajectory_summary,
            outcome=outcome,
            key_findings=key_findings,
            importance_score=importance_score,
        )

    def store_semantic(self, facts: list[dict]) -> list[int]:
        """
        Store extracted facts.

        Each fact dict should have: entity, attribute, value, context, source_session
        """
        if "semantic" not in self.stores:
            return []
        ids = []
        for fact in facts:
            fact_id = self.stores["semantic"].add(
                entity=fact.get("entity", ""),
                attribute=fact.get("attribute", ""),
                value=fact.get("value", ""),
                context=fact.get("context", ""),
                source_session=fact.get("source_session", self.current_session_id),
                confidence=fact.get("confidence", 1.0),
            )
            ids.append(fact_id)
        return ids

    def store_procedural(self, strategies: list[dict]) -> list[int]:
        """
        Store extracted strategies.

        Each strategy dict should have: trigger_condition, strategy
        """
        if "procedural" not in self.stores:
            return []
        ids = []
        for strat in strategies:
            strat_id = self.stores["procedural"].add(
                trigger_condition=strat.get("trigger_condition", ""),
                strategy=strat.get("strategy", ""),
                source_session=self.current_session_id,
            )
            ids.append(strat_id)
        return ids

    def store_reflective(self, lessons: list[dict]) -> list[int]:
        """
        Store lessons learned.

        Each lesson dict should have: lesson, context, importance_score
        """
        if "reflective" not in self.stores:
            return []
        ids = []
        for lesson in lessons:
            lesson_id = self.stores["reflective"].add(
                lesson=lesson.get("lesson", ""),
                context=lesson.get("context", ""),
                derived_from=lesson.get("derived_from", [self.current_session_id]),
                importance_score=lesson.get("importance_score", 0.7),
            )
            ids.append(lesson_id)
        return ids

    def get_stats(self) -> dict:
        """
        Returns stats for dashboard visualization.
        """
        stats = {
            "episodic_count": 0,
            "semantic_count": 0,
            "procedural_count": 0,
            "reflective_count": 0,
            "total_memories": 0,
        }

        for store_name, store in self.stores.items():
            store_stats = store.get_stats()
            stats[f"{store_name}_count"] = store_stats["count"]
            stats["total_memories"] += store_stats["count"]

        return stats

    def get_all_memories_by_type(self) -> dict:
        """Returns all memories organized by type — for snapshots."""
        result = {}
        for store_name, store in self.stores.items():
            result[store_name] = store.get_all()
        return result
