"""
Semantic Memory Store — "What I know"

Stores factual knowledge as entity-attribute-value triples.
Example: (TechCorp, revenue, $4.2B, FY2025 annual)
"""

import json
import sqlite3
from datetime import datetime


class SemanticStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT,
                    attribute TEXT,
                    value TEXT,
                    context TEXT,
                    source_session INTEGER,
                    confidence REAL,
                    embedding BLOB,
                    last_verified TEXT,
                    access_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def add(
        self,
        entity: str,
        attribute: str,
        value: str,
        context: str = "",
        source_session: int = 0,
        confidence: float = 1.0,
        embedding: list[float] | None = None,
    ) -> int:
        # Check for existing fact on same entity+attribute
        existing = self._find_existing(entity, attribute)
        if existing:
            # Update with newer information, log conflict
            self._update_fact(existing["id"], value, context, source_session, confidence)
            return existing["id"]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO semantic
                    (entity, attribute, value, context, source_session,
                     confidence, embedding, last_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity,
                    attribute,
                    value,
                    context,
                    source_session,
                    confidence,
                    json.dumps(embedding) if embedding else None,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def _find_existing(self, entity: str, attribute: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM semantic
                WHERE LOWER(entity) = LOWER(?) AND LOWER(attribute) = LOWER(?)
                """,
                (entity, attribute),
            ).fetchone()
            return dict(row) if row else None

    def _update_fact(
        self,
        fact_id: int,
        value: str,
        context: str,
        source_session: int,
        confidence: float,
    ):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE semantic
                SET value = ?, context = ?, source_session = ?,
                    confidence = ?, last_verified = ?
                WHERE id = ?
                """,
                (
                    value,
                    context,
                    source_session,
                    confidence,
                    datetime.utcnow().isoformat(),
                    fact_id,
                ),
            )
            conn.commit()

    def search(self, top_k: int = 10) -> list[dict]:
        """Return all facts (retriever handles scoring)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM semantic
                ORDER BY source_session DESC, confidence DESC
                LIMIT ?
                """,
                (top_k,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def search_by_entity(self, entity: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM semantic WHERE LOWER(entity) = LOWER(?)",
                (entity,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM semantic ORDER BY entity, attribute"
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def increment_access(self, memory_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE semantic SET access_count = access_count + 1 WHERE id = ?",
                (memory_id,),
            )
            conn.commit()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM semantic").fetchone()[0]
            entities = conn.execute(
                "SELECT COUNT(DISTINCT entity) FROM semantic"
            ).fetchone()[0]
            return {"count": count, "unique_entities": entities, "type": "semantic"}

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        d["embedding"] = json.loads(d["embedding"]) if d["embedding"] else None
        d["memory_type"] = "semantic"
        d["content"] = f"{d['entity']} — {d['attribute']}: {d['value']}"
        if d["context"]:
            d["content"] += f" ({d['context']})"
        return d
