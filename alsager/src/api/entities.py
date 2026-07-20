"""Entity listing + monitored-set management (MVA-2)."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core import ha_client
from src.core import store

router = APIRouter(prefix="/api", tags=["entities"])

class MonitoredPayload(BaseModel):
    entity_ids: List[str] = Field(default_factory=list, description="List of entity IDs to monitor/unmonitor")


@router.get("/entities")
async def list_entities(domain: str | None = None) -> Dict[str, Any]:
    result = ha_client.client.list_entities()
    entities = result["entities"]
    if domain:
        entities = [e for e in entities if e["domain"] == domain]
    return {
        "source": result["source"],
        "count": len(entities),
        "entities": entities,
    }


@router.get("/monitored")
async def get_monitored() -> Dict[str, Any]:
    return {"monitored": store.monitored_store.list()}


@router.post("/monitored")
async def set_monitored(payload: MonitoredPayload) -> Dict[str, Any]:
    ids = payload.entity_ids
    if not ids:
        raise HTTPException(status_code=400, detail="entity_ids required")
    for eid in ids:
        if not store.is_valid_entity_id(eid):
            raise HTTPException(status_code=400, detail=f"Invalid entity_id format: {eid}")
    store.monitored_store.add(ids)
    return {"monitored": store.monitored_store.list()}


@router.delete("/monitored")
async def remove_monitored(payload: MonitoredPayload) -> Dict[str, Any]:
    ids = payload.entity_ids
    store.monitored_store.remove(ids)
    return {"monitored": store.monitored_store.list()}
