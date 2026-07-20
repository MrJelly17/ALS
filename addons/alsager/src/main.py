"""FastAPI app — Alsager add-on entrypoint (MVA-3)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from src.api.entities import router as entities_router
from src.api.ingestion import router as ingestion_router
from src.core import state
from src.core.config import DATA_DIR, UI_DIR
from src.core import ingestion_daemon
from src.core.ha_client import client as ha_client

# Shared singletons. The daemon instance lives in ingestion_daemon module
# so both main.py and api/ingestion.py reference the SAME object.
_db = ingestion_daemon.daemon.db

app = FastAPI(title="Alsager", version="0.3.0")
app.include_router(entities_router)
app.include_router(ingestion_router)


@app.get("/api/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "version": "0.3.0",
            "ha_connected": ha_client.is_available(),
        }
    )


@app.get("/api/status")
async def status() -> JSONResponse:
    snap = ingestion_daemon.daemon.snapshot()
    return JSONResponse(
        {
            "version": "0.3.0",
            "ha_connected": ha_client.is_available(),
            "monitored_entities": snap["monitored"],
            "ingestion": "running" if snap["running"] else "stopped",
            "rows_total": snap["rows_total"],
            "rows_today": snap["rows_today"],
            "data_dir": str(DATA_DIR),
        }
    )


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/app.js")
async def app_js() -> FileResponse:
    return FileResponse(UI_DIR / "app.js", media_type="application/javascript")


@app.get("/styles.css")
async def styles_css() -> FileResponse:
    return FileResponse(UI_DIR / "styles.css", media_type="text/css")
