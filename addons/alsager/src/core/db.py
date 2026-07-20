"""SQLite ingestion store (MVA-3).

Schema is tall: one row per state change. Optimised for append-only
time-series and later ML window extraction (per RESEARCH.md).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS ingestion_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id     TEXT    NOT NULL,
    state         TEXT,
    attributes_json TEXT,
    domain        TEXT,
    last_updated  TEXT,
    received_at   TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ingestion_entity ON ingestion_log(entity_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_received ON ingestion_log(received_at);
"""


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class IngestionDB:
    """Thin SQLite wrapper for the ingestion log."""

    def __init__(self, path: Path | None = None) -> None:
        from src.core.config import DATA_DIR

        self.path = path or (DATA_DIR / "ingestion.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert(
        self,
        entity_id: str,
        state: Optional[str],
        attributes_json: Optional[str],
        domain: Optional[str],
        last_updated: Optional[str],
    ) -> None:
        self.conn.execute(
            """INSERT INTO ingestion_log
               (entity_id, state, attributes_json, domain, last_updated, received_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (entity_id, state, attributes_json, domain, last_updated, _now_iso()),
        )
        self.conn.commit()

    def count_total(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS c FROM ingestion_log").fetchone()
        return int(row["c"])

    def count_today(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM ingestion_log WHERE DATE(received_at) = DATE('now')"
        ).fetchone()
        return int(row["c"])

    def recent(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM ingestion_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
