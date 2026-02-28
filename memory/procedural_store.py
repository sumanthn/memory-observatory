"""
Procedural Memory Store — "How to do things"

Stores reusable strategies as WHEN-THEN rules.
Example: WHEN "company with recent leadership change" THEN "check debt metrics early"

Tracks success/failure counts to learn which strategies work.
"""

import json
import sqlite3
from datetime import datetime


class ProceduralStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procedural (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_condition TEXT,
                    strategy TEXT,
                    success_count INTEGER DEFAULT 1,
                    failure_count INTEGER DEFAULT 0,
                    source_sessions TEXT,
                    embedding BLOB,
                    access_count INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            conn.commit()

    def add(
        self,
        trigger_condition: str,
        strategy: str,
        source_session: int,
        embedding: list[float] | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO procedural
                    (trigger_condition, strategy, source_sessions,
                     embedding, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    trigger_condition,
                    strategy,
                    json.dumps([source_session]),
                    json.dumps(embedding) if embedding else None,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def increment_success(self, memory_id: int, session_id: int):
        """Mark a strategy as successfully used in a new session."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT source_sessions FROM procedural WHERE id = ?",
                (memory_id,),
            ).fetchone()
            if row:
                sessions = json.loads(row[0]) if row[0] else []
                if session_id not in sessions:
                    sessions.append(session_id)
                conn.execute(
                    """
                    UPDATE procedural
                    SET success_count = success_count + 1,
                        source_sessions = ?
                    WHERE id = ?
                    """,
                    (json.dumps(sessions), memory_id),
                )
                conn.commit()

    def search(self, top_k: int = 10) -> list[dict]:
        """Return procedures ranked by success rate (retriever handles full scoring)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM procedural
                ORDER BY
                    CAST(success_count AS REAL) / MAX(success_count + failure_count, 1) DESC,
                    success_count DESC
                LIMIT ?
                """,
                (top_k,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM procedural ORDER BY success_count DESC"
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def increment_access(self, memory_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE procedural SET access_count = access_count + 1 WHERE id = ?",
                (memory_id,),
            )
            conn.commit()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM procedural").fetchone()[0]
            total_successes = conn.execute(
                "SELECT COALESCE(SUM(success_count), 0) FROM procedural"
            ).fetchone()[0]
            return {
                "count": count,
                "total_successes": total_successes,
                "type": "procedural",
            }

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        d["source_sessions"] = (
            json.loads(d["source_sessions"]) if d["source_sessions"] else []
        )
        d["embedding"] = json.loads(d["embedding"]) if d["embedding"] else None
        d["memory_type"] = "procedural"
        d["importance_score"] = d["success_count"] / max(
            d["success_count"] + d["failure_count"], 1
        )
        d["content"] = f"WHEN: {d['trigger_condition']}\nTHEN: {d['strategy']}"
        return d
