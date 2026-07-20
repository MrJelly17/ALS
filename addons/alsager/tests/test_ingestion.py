"""Tests for the Alsager MVA-3 ingestion daemon + SQLite (no HTTP layer).

The daemon is an asyncio loop; we exercise it directly on a real event loop
rather than through TestClient (which is not thread-safe for background loops).
HTTP endpoints (start/stop/status) are covered by the live smoke test.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

import pytest

ADDON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ADDON_DIR))

from src.core import db as db_mod  # noqa: E402
from src.core import store as store_mod  # noqa: E402
from src.core import ingestion_daemon as daemon_mod  # noqa: E402


@pytest.fixture()
def isolated():
    tmp = Path(tempfile.mkdtemp(prefix="alsager-test-"))
    database = db_mod.IngestionDB(tmp / "ingestion.db")
    store = store_mod.MonitoredStore(tmp / "monitored.json")
    store.add(["sensor.battery_level", "sensor.steps"])
    daemon = daemon_mod.IngestionDaemon(database, store, interval=0.05)
    yield daemon, database
    database.close()


def test_db_insert_and_counts(tmp_path):
    database = db_mod.IngestionDB(tmp_path / "t.db")
    database.insert("sensor.x", "1.23", "{}", "sensor", None)
    database.insert("sensor.y", "4.56", "{}", "sensor", None)
    assert database.count_total() == 2
    rows = database.recent(10)
    assert len(rows) == 2
    assert rows[0]["entity_id"] in ("sensor.x", "sensor.y")
    database.close()


def test_daemon_start_stop_flags(isolated):
    daemon, _ = isolated
    assert daemon.start() is True
    assert daemon.running is True
    # idempotent: second start returns False (already running)
    assert daemon.start() is False
    assert daemon.running is True
    assert daemon.stop() is True
    assert daemon.running is False
    # stop when not running returns False
    assert daemon.stop() is False


def test_daemon_ingests_rows(isolated):
    daemon, database = isolated
    loop = asyncio.new_event_loop()
    try:
        async def _run_for(dur):
            task = asyncio.ensure_future(daemon._run())
            await asyncio.sleep(dur)
            daemon.stop()
            task.cancel()

        loop.run_until_complete(_run_for(0.6))
    finally:
        loop.close()
    # The mock source should have appended at least one row.
    assert database.count_total() >= 1


def test_status_includes_row_counts(isolated):
    daemon, _ = isolated
    snap = daemon.snapshot()
    assert "running" in snap
    assert "rows_total" in snap
    assert "rows_today" in snap
    assert snap["monitored"] == 2
