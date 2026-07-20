"""Monitored-entity persistence (MVA-2/3).

Stores the set of entity IDs the user wants Alsager to ingest.
Backed by a JSON file under the add-on config dir.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.core.config import CONFIG_DIR


class MonitoredStore:
    """Persists the monitored entity set to ``monitored.json`` (no dupes)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (CONFIG_DIR / "monitored.json")
        self._entities: List[str] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self._entities = list(data) if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                self._entities = []
        else:
            self._entities = []

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(sorted(self._entities), indent=2))

    def list(self) -> List[str]:
        return list(self._entities)

    def add(self, entity_ids: List[str]) -> None:
        added = False
        for eid in entity_ids:
            if eid and eid not in self._entities:
                self._entities.append(eid)
                added = True
        if added:
            self._save()

    def remove(self, entity_ids: List[str]) -> None:
        before = set(self._entities)
        self._entities = [e for e in self._entities if e not in set(entity_ids)]
        if set(self._entities) != before:
            self._save()

    def clear(self) -> None:
        if self._entities:
            self._entities = []
            self._save()


# Module-level singleton shared by the entities API and the ingestion daemon
# so both read/write the SAME monitored set (no drift between modules).
monitored_store = MonitoredStore()
