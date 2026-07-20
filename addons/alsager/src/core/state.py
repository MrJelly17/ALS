"""Ingestion runtime status (MVA-3: bridged to the live daemon).

Kept for backwards compatibility with UI code that referenced
``state.status``. Now returns the daemon's live snapshot.
"""

from __future__ import annotations

from src.core import ingestion_daemon


def snapshot() -> dict:
    return ingestion_daemon.daemon.snapshot()
