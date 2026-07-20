"""Ingestion background daemon (MVA-3).

MVA-3: an asyncio loop that, for each monitored entity, produces state
changes and appends them to the SQLite ingestion log. With no HA connection
configured it uses a **mock event source** (random-walk state per sensor)
so the full ingestion pipeline is exercisable locally.

Real HA wiring (WebSocket/REST subscription) slots in later by replacing
``_mock_event_source`` with a live subscription; the loop and DB writes
stay identical.
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import AsyncIterator, Optional

from src.core.db import IngestionDB
from src.core.store import monitored_store


class IngestionDaemon:
    def __init__(self, db: IngestionDB, store: MonitoredStore, interval: float = 2.0) -> None:
        self.db = db
        self.store = store
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.last_error: Optional[str] = None
        # simulated state per entity for the mock source
        self._mock_state: dict[str, float] = {}

    @property
    def running(self) -> bool:
        return self._running

    async def _mock_event_source(self) -> AsyncIterator[dict]:
        """Yield synthetic state changes for monitored entities."""
        while True:
            for entity_id in self.store.list():
                base = self._mock_state.get(entity_id, 0.0)
                # random walk; keep values in a plausible range
                value = max(-20.0, min(20.0, base + random.uniform(-1.5, 1.5)))
                self._mock_state[entity_id] = value
                domain = entity_id.split(".", 1)[0]
                yield {
                    "entity_id": entity_id,
                    "state": f"{value:.2f}",
                    "attributes_json": json.dumps({"mock": True, "simulated": True}),
                    "domain": domain,
                    "last_updated": None,
                }
            await asyncio.sleep(self.interval)

    async def _run(self) -> None:
        self._running = True
        self.last_error = None
        try:
            async for event in self._mock_event_source():
                if not self._running:
                    break
                try:
                    self.db.insert(
                        entity_id=event["entity_id"],
                        state=event.get("state"),
                        attributes_json=event.get("attributes_json"),
                        domain=event.get("domain"),
                        last_updated=event.get("last_updated"),
                    )
                except Exception as exc:  # noqa: BLE001
                    self.last_error = str(exc)
        finally:
            self._running = False

    def start(self) -> bool:
        if self._running:
            return False
        self._running = True
        self._task = asyncio.ensure_future(self._run())
        return True

    def stop(self) -> bool:
        if not self._running:
            return False
        self._running = False
        if self._task:
            self._task.cancel()
        return True

    def snapshot(self) -> dict:
        return {
            "running": self._running,
            "monitored": len(self.store.list()),
            "rows_total": self.db.count_total(),
            "rows_today": self.db.count_today(),
            "last_error": self.last_error,
        }


# Module-level singleton used by the API and UI.
# Shares the same MonitoredStore instance as the entities API.
daemon = IngestionDaemon(IngestionDB(), monitored_store)