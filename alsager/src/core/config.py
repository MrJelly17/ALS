"""Project paths with container/dev fallback.

In the HA add-on container data lives under /data and /config.
On a developer machine those may not exist or be read-only, so we probe
writability and fall back to local directories.
"""

from __future__ import annotations

import os
from pathlib import Path


def _resolve_dir(env_var: str, container_path: str, local_fallback: str) -> Path:
    candidate = Path(os.environ.get(env_var, container_path))
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        probe = candidate / ".write_test"
        probe.touch()
        probe.unlink()
        return candidate
    except (OSError, PermissionError):
        fallback = Path(local_fallback)
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


DATA_DIR = _resolve_dir("ALSAGER_DATA_DIR", "/data", "data")
CONFIG_DIR = _resolve_dir("ALSAGER_CONFIG_DIR", "/config/alsager", "config")
UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui"
