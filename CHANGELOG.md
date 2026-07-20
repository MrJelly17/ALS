# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning based on [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Build pipeline: GitHub Actions workflow (`.github/workflows/build.yml`)
  builds the add-on image per-arch (amd64/armv7/arm64) via Buildx + QEMU and
  pushes to **GHCR** (`ghcr.io/<owner>/alsager-<arch>:dev` on push to `main`,
  `:<version>` on release). HA no longer builds locally — it pulls the
  prebuilt image referenced in `config.json` `image` field.

## [0.3.0] - 2026-07-20

### Added (MVA-3: Ingestion)
- `src/core/db.py` — SQLite `ingestion_log` store (one row per state change,
  indexed by entity + received_at).
- `src/core/ingestion_daemon.py` — `IngestionDaemon`, an asyncio background
  loop that ingests mock state changes for monitored entities (real HA
  wiring slots in later by replacing `_mock_event_source`).
- `src/core/ha_client.py` — real Home Assistant REST access. Resolves
  credentials from `SUPERVISOR_TOKEN` + `SUPERVISOR_URL` (auto-injected in
  the add-on container) or manual `HA_BASE_URL` + `HA_LONG_LIVED_TOKEN`.
  Falls back to mock entities when no HA connection is available.
- Endpoints: `POST /api/ingestion/start|stop`, `GET /api/ingestion/status`.
- Web UI: Status tab "Start/Stop ingestion" + counters (rows total/today,
  last error); Data preview tab.
- `config.json` v0.3.0 with `options`/`schema` (`ha_base_url`, `ha_token`,
  `poll_interval`); `run.sh` wires Supervisor token/url + options.
- Shared singletons `monitored_store` and `ingestion_daemon.daemon` so the
  entities API and ingestion daemon reference the SAME monitored set.

### Changed
- App version bumped to `0.3.0`; `/api/health` and `/api/status` report `0.3.0`.
- `Dockerfile` now builds on `ghcr.io/home-assistant/{arch}-base` (required
  for s6 + bashio used by `run.sh`).

### Verification
- 12/12 pytest tests pass in an isolated `.venv` (PYTHONPATH stripped).
- Live uvicorn smoke test: health, status, entities (mock), monitored
  roundtrip, ingestion start → rows accumulated → stop — all PASS.

### Notes
- **Local dev pitfall:** if the shell exports `PYTHONPATH` to another venv,
  the new `.venv` will inherit it and import the wrong packages. Always run
  with `env -u PYTHONPATH …` (documented in README).

## [0.2.0] - 2026-07-20

### Added (MVA-2: Entity listing & selection)
- `GET /api/entities` — list HA entities, optional `?domain=` filter.
  - Returns **mock entities** when no HA connection is configured, so the
    UI is fully usable during early development.
- `GET/POST/DELETE /api/monitored` — manage the monitored entity set,
  persisted to `config/monitored.json` (no duplicates on re-add).
- Web UI "Entities" tab: filter box, domain dropdown, checkbox selection,
  "Start monitoring" / "Stop monitoring" buttons, live monitored summary.
- Web UI tab navigation (Status / Entities / Data preview).
- `src/core/config.py` — path resolution with HA-container → local fallback.
- `src/core/store.py` — JSON-backed `MonitoredStore`.
- `src/core/state.py` — in-memory ingestion status (bridged to daemon).
- `src/api/entities.py` — entities/monitored API router.
- `tests/test_api.py` — 8 tests covering health, status, entity listing,
  domain filter, and monitored roundtrip (isolated, no HA required).
- `.gitignore` for Python/venv/local data artifacts.

## [0.1.0] - 2026-01-01

- Added project documentation baseline.
