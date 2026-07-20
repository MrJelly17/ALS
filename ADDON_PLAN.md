# Alsager — Add-on Build Plan

Goal: build a working Home Assistant Add-on that can:
- list HA entities,
- let user select entities to monitor,
- ingest state changes 24/7 into SQLite,
- expose a minimal web UI to control ingestion.

This is the foundation for all later modules.

## Add-on Structure (actual)

```
alsager/                      # repo root = GitHub repo (MrJelly17/ALS)
├─ .github/workflows/build.yml  # GH Actions: build per-arch → GHCR
├─ addons/alsager/            # HA add-on directory (added as HA repository)
│  ├─ config.json            # manifest (image: ghcr.io/mrjelly17/alsager-{arch})
│  ├─ Dockerfile             # HA base image (amd64/armv7/arm64)
│  ├─ run.sh                 # entrypoint (s6 + bashio)
│  ├─ requirements.txt
│  ├─ src/
│  │  ├─ main.py             # FastAPI app + health/status/UI routes
│  │  ├─ api/entities.py     # /api/entities, /api/monitored
│  │  ├─ api/ingestion.py    # /api/ingestion/*
│  │  └─ core/
│  │     ├─ config.py        # path resolution (HA /data,/config → local)
│  │     ├─ ha_client.py     # HA REST wrapper + mock entities + `client` singleton
│  │     ├─ db.py            # SQLite ingestion_log
│  │     ├─ ingestion_daemon.py  # background asyncio ingestion loop + `daemon` singleton
│  │     ├─ store.py         # JSON-backed MonitoredStore + `monitored_store` singleton
│  │     └─ state.py         # status bridge → daemon.snapshot()
│  ├─ ui/{index.html,app.js,styles.css}
│  └─ tests/{test_api.py,test_ingestion.py}
├─ README.md, CHANGELOG.md, TASK.md, REQUIREMENTS.md, RESEARCH.md,
│  ROADMAP.md, STRUKTURA.md, STACK.md, INSTRUCTIONS.md, SECURITY.md,
│  IDEAS.md, MOCKUPS.md, OPEN_QUESTIONS.md, ADDON_PLAN.md, ADDON_INSTALL.md
```

## Build & Distribution Model (2026-07-20)

Image is **built by a GitHub Actions worker**, NOT locally:

1. Push/merge to `main` (or a release) triggers `.github/workflows/build.yml`.
2. The workflow builds `addons/alsager/Dockerfile` for `amd64`, `armv7`,
   `arm64` (QEMU + Buildx) and pushes to GHCR:
   `ghcr.io/mrjelly17/alsager-<arch>:dev` (push to main) or `:<version>`
   (release tag).
3. `config.json` references the prebuilt image:
   `"image": "ghcr.io/mrjelly17/alsager-{arch}"` — the Supervisor substitutes
   `{arch}` with the target arch at install time and **pulls** the image
   (no local Docker build on HA).
4. In HA: Settings → Add-ons → Store → ⋮ → Repositories → add
   `https://github.com/MrJelly17/ALS`. Install "Alsager".

This resolves the earlier `404` (`Failed to fetch manifest for
ghcr.io/...:0.0.6`) — the image now exists in GHCR once the workflow runs,
and `config.json` uses the correct `{arch}` template.

## UI Wireframe

### Page 1: Entities
- Search/filter entities by device or domain
- Multi-select checkboxes
- "Start monitoring" button
- List of currently monitored entities

### Page 2: Status
- Ingestion status: running/stopped
- Database size, row count (today / total)
- Last ingestion error (if any)
- Start/Stop ingestion buttons

### Page 3: Data preview
- Table of recent rows (entity_id, state, timestamp)

## Minimal Viable Add-on (MVA)

Phase MVA-1: Static scaffold  ✅ DONE
- Dockerfile (HA base) + FastAPI `/health` + UI served at `/`.

Phase MVA-2: Entity listing  ✅ DONE (2026-07-20)
- `/api/entities` (mock fallback), `?domain=` filter.
- `/api/monitored` GET/POST/DELETE, persisted via `MonitoredStore`.
- UI Entities tab.

Phase MVA-3: Ingestion  ✅ DONE (2026-07-20) — verified
- `src/core/db.py` SQLite `ingestion_log`.
- `src/core/ingestion_daemon.py` asyncio loop (mock source) + `daemon` singleton.
- `POST /api/ingestion/start|stop`, `GET /api/ingestion/status`.
- UI Status (counters + controls) + Data preview.
- 12/12 pytest + live smoke (start→rows→stop) PASS.

Phase MVA-4: Polish
- Error handling, restart resilience, logging, labels, dataset export,
  pattern engine (small NN <100k params), runtime inference, HA automations.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend | FastAPI | async, auto-OpenAPI |
| DB | SQLite | zero-dep, enough for <10M rows |
| Frontend | SPA HTML/JS | no build step, served by FastAPI |
| Image build | GH Actions → GHCR | no local Docker on HA/dev; reproducible |
| Base image | HA `{arch}-base` | s6 + bashio for `run.sh` |
| Ingestion | asyncio loop (mock now, HA later) | event-driven, real HA wiring TBD |
