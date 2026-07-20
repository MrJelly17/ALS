"""Ingestion control endpoints (MVA-3)."""

from __future__ import annotations

from fastapi import APIRouter

import src.core.ingestion_daemon as ingestion_daemon

router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post("/ingestion/start")
async def start_ingestion() -> dict:
    started = ingestion_daemon.daemon.start()
    return {
        "running": ingestion_daemon.daemon.running,
        "started": started,
        **ingestion_daemon.daemon.snapshot(),
    }


@router.post("/ingestion/stop")
async def stop_ingestion() -> dict:
    stopped = ingestion_daemon.daemon.stop()
    return {
        "running": ingestion_daemon.daemon.running,
        "stopped": stopped,
        **ingestion_daemon.daemon.snapshot(),
    }


@router.get("/ingestion/status")
async def ingestion_status() -> dict:
    return ingestion_daemon.daemon.snapshot()
