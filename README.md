# Alsager

Alsager is an AI-powered pattern detection system for Home Assistant.
It continuously monitors selected sensors, stores state history in a lightweight local database, exports ML-ready datasets, trains neural networks on the data, and feeds learned patterns back into Home Assistant automation.
Delivered as a **Home Assistant Add-on** with a web UI.

## Key Constraint

Alsager must run inside Home Assistant as an Add-on (the chosen delivery model).

## Working Mode

- High-level vision first, detailed decisions later.
- Requirements/architecture evolve as context grows.
- This document is the single source of truth and is updated continuously.

## Language & Communication

- All code, docs, and configs are **English**.
- User–assistant discussion is in **Polish**; Polish is never committed.

## Documentation

`TASK.md` · `REQUIREMENTS.md` · `RESEARCH.md` · `IDEAS.md` · `MOCKUPS.md` ·
`STRUKTURA.md` · `STACK.md` · `CHANGELOG.md` · `INSTRUCTIONS.md` ·
`SECURITY.md` · `ROADMAP.md` · `OPEN_QUESTIONS.md` · `ADDON_PLAN.md` ·
`ADDON_INSTALL.md`

## Current Status (2026-07-20)

Following the MVA plan in `ADDON_PLAN.md`.

| Phase | Status |
|-------|--------|
| MVA-1: Static scaffold | ✅ Done |
| MVA-2: Entity listing & selection | ✅ Done |
| MVA-3: Ingestion (SQLite + daemon + real HA REST) | ✅ Done & verified |
| MVA-4: Polish / dataset export / pattern engine | ⚫ Pending |

**Verified:** 12/12 pytest + live uvicorn smoke (health, status, entities
mock, monitored roundtrip, ingestion start→rows→stop).

The add-on runs locally without HA (mock entities); inside HA it connects
automatically via `SUPERVISOR_TOKEN` / `SUPERVISOR_URL`.

## Build & Distribution Model

The add-on **image is built by a GitHub Actions worker** and pushed to GHCR
(`ghcr.io/MrJelly17/alsager-<arch>`). HA pulls the prebuilt image — it does
not build locally.

- Workflow: `.github/workflows/build.yml` (builds amd64/armv7/arm64 on push
  to `main` → `:dev`, on release → `:<version>`).
- `config.json` references the image: `"image": "ghcr.io/mrjelly17/alsager-{arch}"`.

## Install on Home Assistant

1. Ensure the image exists: push `main` (or a release) so the Actions
   workflow builds & publishes to GHCR. (Needs `GITHUB_TOKEN` — automatic in
   Actions; package visibility must allow the HA host to pull.)
2. In HA: **Settings → Add-ons → Add-on Store → ⋮ → Repositories → Add**.
3. Enter `https://github.com/MrJelly17/ALS` and click Add.
4. "Alsager" appears in the store → **Install** → **Start** → open the panel.

> Earlier error `Failed to fetch manifest for ghcr.io/...:0.0.6 - 404` meant
> the image did not exist / `config.json` pointed at a wrong tag. With the
> Actions build + `{arch}` template in `config.json`, the manifest resolves.

## Run Locally (dev)

```bash
cd addons/alsager
python3 -m venv .venv
# Strip any inherited PYTHONPATH so the new .venv stays isolated:
env -u PYTHONPATH .venv/bin/pip install -r requirements-dev.txt
env -u PYTHONPATH .venv/bin/python -m pytest -q
env -u PYTHONPATH ALSAGER_DATA_DIR=./data ALSAGER_CONFIG_DIR=./config \
  .venv/bin/python -m uvicorn src.main:app --port 5000
# open http://127.0.0.1:5000
```

## Project Layout

```
addons/alsager/
├─ config.json          # manifest (image: ghcr.io/mrjelly17/alsager-{arch})
├─ Dockerfile           # HA base image
├─ run.sh
├─ requirements.txt     # runtime
├─ requirements-dev.txt # dev/test (pytest, httpx)
├─ src/{main.py, api/, core/}
├─ ui/{index.html,app.js,styles.css}
└─ tests/{test_api.py,test_ingestion.py}
```

## License

<!-- TODO -->
