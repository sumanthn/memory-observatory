"""
Memory Retriever — Multi-signal scoring for memory retrieval

Scores each candidate memory on 4 signals:
  1. Relevance  — cosine similarity to current context
  2. Importance — stored importance score
  3. Recency    — exponential decay by session distance
  4. Type match — phase-aware type weighting

Uses bag-of-words cosine similarity as the default embedding approach.
Falls back gracefully if no embedding libraries are available.
"""

import math
import re
from collections import Counter

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import (
    MAX_MEMORIES_PER_RETRIEVAL,
    MAX_MEMORY_TOKENS,
    PHASE_TYPE_WEIGHTS,
    RECENCY_DECAY_FACTOR,
    RETRIEVAL_WEIGHTS,
)


def _tokenize(text: str) -> list[str]:
    """Simple word tokenization: lowercase, split on non-alpha, remove short words."""
    words = re.findall(r"[a-zA-Z]{2,}", text.lower())
    return words


def _bow_vector(text: str) -> Counter:
    """Bag-of-words vector as a Counter."""
    return Counter(_tokenize(text))


def cosine_similarity(text_a: str, text_b: str) -> float:
    """Bag-of-words cosine similarity between two texts."""
    vec_a = _bow_vector(text_a)
    vec_b = _bow_vector(text_b)

    if not vec_a or not vec_b:
        return 0.0

    # Intersection of words
    common = set(vec_a.keys()) & set(vec_b.keys())
    dot_product = sum(vec_a[w] * vec_b[w] for w in common)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


class Retriever:
    def __init__(self, current_session_id: int = 1):
        self.current_session_id = current_session_id

    def score_memories(
        self,
        memories: list[dict],
        query: str,
        phase: str = "planning",
    ) -> list[dict]:
        """
        Score and rank a list of candidate memories against the query.

        Args:
            memories: List of memory dicts (each must have 'content',
                      'memory_type', and optionally 'importance_score',
                      'session_id' or 'source_session')
            query: The current task context
            phase: One of 'planning', 'execution', 'review'

        Returns:
            Scored and sorted list of memory dicts with score_breakdown added.
        """
        type_weights = PHASE_TYPE_WEIGHTS.get(phase, PHASE_TYPE_WEIGHTS["planning"])
        scored = []

        for memory in memories:
            content = memory.get("content", "")
            mem_type = memory.get("memory_type", "episodic")

            # 1. Relevance: cosine similarity to query
            #    For semantic facts, boost if entity name appears in query
            #    (bag-of-words penalizes short facts vs long procedural memories)
            relevance = cosine_similarity(query, content)
            if mem_type == "semantic":
                entity = memory.get("entity", "")
                attribute = memory.get("attribute", "")
                query_words_set = set(_tokenize(query))
                # Boost if the entity (company name) appears in query as whole words
                entity_words = set(_tokenize(entity))
                entity_match = entity_words & query_words_set
                if entity_match and any(len(w) > 3 for w in entity_match):
                    relevance = max(relevance, 0.3) + 0.15
                # Boost if the attribute matches query keywords
                attr_words = set(_tokenize(attribute))
                if attr_words & query_words_set:
                    relevance += 0.1

            # 2. Importance: stored on the memory (default 0.5)
            importance = memory.get("importance_score", 0.5)
            # For procedural memories, use success rate
            if mem_type == "procedural":
                success = memory.get("success_count", 1)
                failure = memory.get("failure_count", 0)
                importance = success / max(success + failure, 1)
            # For semantic memories, use confidence score
            elif mem_type == "semantic":
                importance = memory.get("confidence", 1.0)

            # 3. Recency: exponential decay based on session distance
            #    Uses absolute distance so future sessions (from backfill)
            #    don't get artificially high recency
            source_session = memory.get("source_session") or memory.get(
                "session_id", 1
            )
            sessions_ago = abs(self.current_session_id - source_session)
            recency = math.exp(-RECENCY_DECAY_FACTOR * sessions_ago)

            # 4. Type match: phase-aware weighting
            type_match = type_weights.get(mem_type, 0.1)

            # Weighted composite score
            score = (
                RETRIEVAL_WEIGHTS["relevance"] * relevance
                + RETRIEVAL_WEIGHTS["importance"] * importance
                + RETRIEVAL_WEIGHTS["recency"] * recency
                + RETRIEVAL_WEIGHTS["type_match"] * type_match
            )

            scored_memory = memory.copy()
            scored_memory["score"] = round(score, 4)
            scored_memory["score_breakdown"] = {
                "relevance": round(relevance, 4),
                "importance": round(importance, 4),
                "recency": round(recency, 4),
                "type_match": round(type_match, 4),
            }
            scored.append(scored_memory)

        # Sort by score descending
        scored.sort(key=lambda m: m["score"], reverse=True)

        # Diversified selection: ensure a mix of memory types
        # Take top memories but guarantee at least 1-2 from each available type
        # This prevents one dominant type from crowding out others
        result = []
        total_tokens = 0
        types_included = {}
        min_per_type = 2  # Guarantee at least 2 slots for each type present

        # First pass: take the top-scoring memory from each type
        for memory in scored:
            mem_type = memory.get("memory_type", "")
            if mem_type not in types_included:
                content = memory.get("content", "")
                token_estimate = int(len(content.split()) * 1.3)
                if total_tokens + token_estimate <= MAX_MEMORY_TOKENS:
                    result.append(memory)
                    total_tokens += token_estimate
                    types_included[mem_type] = 1

        # Second pass: fill remaining slots by score
        for memory in scored:
            if len(result) >= MAX_MEMORIES_PER_RETRIEVAL:
                break
            if memory in result:
                continue
            content = memory.get("content", "")
            token_estimate = int(len(content.split()) * 1.3)
            if total_tokens + token_estimate > MAX_MEMORY_TOKENS:
                break
            result.append(memory)
            total_tokens += token_estimate

        # Re-sort final result by score
        result.sort(key=lambda m: m["score"], reverse=True)
        return result
