"""Tests for the Alsager MVA-2 API (entity listing + monitored set)."""

import os
import sys
from pathlib import Path

import json
import pytest
from fastapi.testclient import TestClient

ADDON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ADDON_DIR))

from src.main import app  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app)


def test_health_ok(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["version"] == "0.3.0"


def test_status_ok(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    body = res.json()
    assert "ha_connected" in body
    assert "ingestion" in body
    assert "rows_total" in body


def test_list_entities_mock(client):
    res = client.get("/api/entities")
    assert res.status_code == 200
    body = res.json()
    assert body["source"] == "mock"
    assert body["count"] > 0
    assert any(e["entity_id"] == "sensor.battery_level" for e in body["entities"])


def test_list_entities_domain_filter(client):
    res = client.get("/api/entities?domain=binary_sensor")
    assert res.status_code == 200
    body = res.json()
    assert all(e["domain"] == "binary_sensor" for e in body["entities"])
    assert body["count"] >= 1


def test_monitored_roundtrip(client, tmp_path):
    import src.core.store as store_mod

    store_mod.monitored_store = store_mod.MonitoredStore(tmp_path / "monitored.json")
    store_mod.monitored_store.clear()
    assert client.get("/api/monitored").json()["monitored"] == []

    add = client.post(
        "/api/monitored",
        json={"entity_ids": ["sensor.battery_level", "sensor.steps"]},
    )
    assert add.status_code == 200
    added = add.json()["monitored"]
    assert "sensor.battery_level" in added
    assert "sensor.steps" in added

    add2 = client.post(
        "/api/monitored", json={"entity_ids": ["sensor.battery_level"]}
    )
    assert add2.json()["monitored"].count("sensor.battery_level") == 1

    rem = client.request(
        "DELETE",
        "/api/monitored",
        json={"entity_ids": ["sensor.steps"]},
    )
    remaining = rem.json()["monitored"]
    assert "sensor.steps" not in remaining
    assert "sensor.battery_level" in remaining


def test_monitored_requires_ids(client):
    res = client.post("/api/monitored", json={"entity_ids": []})
    assert res.status_code == 400


def test_monitored_invalid_ids_rejected(client):
    # Testing that invalid and potentially dangerous entity IDs are correctly rejected
    res = client.post("/api/monitored", json={"entity_ids": ["../../../malicious_id"]})
    assert res.status_code == 400
    assert "Invalid entity_id format" in res.json()["detail"]


def test_ingestion_recent_endpoint(client):
    # Testing that the new recent ingestion endpoint works and returns a list
    res = client.get("/api/ingestion/recent?limit=10")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_index_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Alsager" in res.text


def test_static_assets(client):
    js = client.get("/app.js")
    css = client.get("/styles.css")
    assert js.status_code == 200
    assert css.status_code == 200
    assert js.headers["content-type"].startswith("application/javascript")
    assert css.headers["content-type"].startswith("text/css")
