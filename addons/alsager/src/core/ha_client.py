"""Home Assistant API client wrapper.

MVA-1: connection discovery / availability.
MVA-2: entity listing with a mock fallback.
MVA-3: real REST access to Home Assistant when the add-on runs inside HA
(Supervisor injects SUPERVISOR_TOKEN + SUPERVISOR_URL; the add-on reaches
HA at http://supervisor/core/api).

Token resolution order:
  1. Explicit token/base_url passed in.
  2. Env: SUPERVISOR_TOKEN + SUPERVISOR_URL (HA add-on container).
  3. Env: HA_LONG_LIVED_TOKEN + HA_BASE_URL (manual/dev).
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

# Mock entities used when no HA connection is configured. Mirrors typical
# Home Assistant mobile app sensor entity_ids so UI development is realistic.
MOCK_ENTITIES = [
    {"entity_id": "sensor.accelerometer_x", "domain": "sensor", "friendly_name": "Accelerometer X", "state": "0.02"},
    {"entity_id": "sensor.accelerometer_y", "domain": "sensor", "friendly_name": "Accelerometer Y", "state": "-0.01"},
    {"entity_id": "sensor.accelerometer_z", "domain": "sensor", "friendly_name": "Accelerometer Z", "state": "9.81"},
    {"entity_id": "sensor.gyroscope_x", "domain": "sensor", "friendly_name": "Gyroscope X", "state": "0.00"},
    {"entity_id": "sensor.gyroscope_y", "domain": "sensor", "friendly_name": "Gyroscope Y", "state": "0.00"},
    {"entity_id": "sensor.gyroscope_z", "domain": "sensor", "friendly_name": "Gyroscope Z", "state": "0.00"},
    {"entity_id": "sensor.battery_level", "domain": "sensor", "friendly_name": "Battery Level", "state": "87"},
    {"entity_id": "sensor.wifi_connection", "domain": "sensor", "friendly_name": "Wi-Fi Connection", "state": "home-ssid"},
    {"entity_id": "sensor.mobile_data_connection_type", "domain": "sensor", "friendly_name": "Mobile Data Type", "state": "LTE"},
    {"entity_id": "sensor.steps", "domain": "sensor", "friendly_name": "Steps", "state": "3120"},
    {"entity_id": "sensor.activity", "domain": "sensor", "friendly_name": "Activity", "state": "still"},
    {"entity_id": "binary_sensor.phone_charging", "domain": "binary_sensor", "friendly_name": "Phone Charging", "state": "off"},
    {"entity_id": "device_tracker.phone", "domain": "device_tracker", "friendly_name": "Phone", "state": "home"},
]


class HAClient:
    """Home Assistant API access with graceful mock fallback."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        use_mock: Optional[bool] = None,
        timeout: float = 10.0,
    ) -> None:
        # Supervisor-injected (HA add-on container)
        self.token = (
            token
            or os.environ.get("SUPERVISOR_TOKEN")
            or os.environ.get("HA_LONG_LIVED_TOKEN", "")
        )
        supervisor_url = os.environ.get("SUPERVISOR_URL", "").rstrip("/")
        if supervisor_url and token is None:
            # Token already pulled from SUPERVISOR_TOKEN above.
            token = token or os.environ.get("SUPERVISOR_TOKEN", "")
        base = base_url or supervisor_url
        if base:
            # Inside HA add-on container the Supervisor proxy exposes HA at
            # <supervisor_url>/core/api ; a manual base URL is used as-is.
            if supervisor_url and not base_url:
                base = f"{supervisor_url}/core/api"
        else:
            base = (os.environ.get("HA_BASE_URL", "")).rstrip("/")
        self.base_url = base
        self._timeout = timeout
        self._available: Optional[bool] = None
        self._use_mock = use_mock if use_mock is not None else None

    def is_available(self) -> bool:
        """True when HA base URL + token are present."""
        if self._available is None:
            self._available = bool(self.base_url) and bool(self.token)
        return self._available

    def _should_mock(self) -> bool:
        if self._use_mock is not None:
            return self._use_mock
        return not self.is_available()

    def list_entities(self, domain: Optional[str] = None) -> dict:
        """Return entities, optionally filtered by domain.

        Returns ``{"source": "ha"|"mock", "entities": [...]}``. Uses live HA
        states when available; otherwise the mock list so the UI is fully
        functional during early development / local testing.
        """
        if self._should_mock():
            source = "mock"
            entities = MOCK_ENTITIES
        else:
            try:
                states = self.get_states()
                entities = [
                    {
                        "entity_id": s["entity_id"],
                        "domain": s["entity_id"].split(".", 1)[0],
                        "friendly_name": (s.get("attributes") or {}).get(
                            "friendly_name", s["entity_id"]
                        ),
                        "state": s.get("state"),
                    }
                    for s in states
                ]
                source = "ha"
            except Exception:
                # Network/token failure -> fall back to mock so UI still works.
                entities = MOCK_ENTITIES
                source = "mock"
        if domain:
            entities = [e for e in entities if e["domain"] == domain]
        return {"source": source, "entities": entities}

    def get_states(self) -> list[dict]:
        """GET /api/states — all current entity states."""
        url = f"{self.base_url}/states"
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_entity_state(self, entity_id: str) -> dict | None:
        """GET /api/states/<entity_id>."""
        import re
        if not re.match(r"^[a-zA-Z0-9_]+\.[a-zA-Z0-9_.-]+$", entity_id):
            raise ValueError(f"Invalid entity_id: {entity_id}")
        url = f"{self.base_url}/states/{entity_id}"
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self._timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def get_monitored_states(self, entity_ids: list[str]) -> list[dict]:
        """Fetch current states for the given entity ids (polling fallback)."""
        out = []
        for eid in entity_ids:
            try:
                st = self.get_entity_state(eid)
                if st:
                    out.append(st)
            except Exception:
                continue
        return out


# Module-level singleton shared by the API and UI.
client = HAClient()
