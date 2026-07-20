# Alsager — Installation and Distribution

## Distribution Model (2026-07-20)

The add-on image is **built by GitHub Actions** and published to GHCR
(`ghcr.io/MrJelly17/alsager-<arch>`). Home Assistant **pulls** the prebuilt
image — it does NOT build the Dockerfile locally. This avoids needing Docker
on the HA host or on the dev machine.

Benefits:
- Reproducible, versioned builds (per arch: amd64 / armv7 / arm64).
- `config.json` references a fixed GHCR image, so installation is just
  "add repository → install".
- No local `docker build` step, no Samba copy of source.

## Prerequisites

1. The GitHub repo `MrJelly17/ALS` exists and contains `addons/alsager/`.
2. The Actions workflow (`.github/workflows/build.yml`) has run at least once
   and pushed images to GHCR.
   - On push to `main` → `ghcr.io/mrjelly17/alsager-<arch>:dev`
   - On a GitHub Release → `ghcr.io/mrjelly17/alsager-<arch>:<version>`
3. GHCR packages are visible to the HA host (public, or the HA host pulls
   with appropriate rights). For a private repo, the Supervisor needs
   registry credentials — keep the repo (and package) public for simplicity,
   or configure `config.json` auth.

## Install Steps (HA)

1. In HA UI: **Settings → Add-ons → Add-on Store → ⋮ (top-right) →
   Repositories → Add**.
2. Enter the repository URL: `https://github.com/MrJelly17/ALS`
3. Confirm. "Alsager" appears under the added repository in the store.
4. Click **Alsager → Install**. The Supervisor pulls
   `ghcr.io/mrjelly17/alsager-<arch>` for your machine's arch.
5. **Start** the add-on; open the UI from the HA sidebar (ingress panel).

> If install fails with a manifest/404 error, the GHCR image does not exist
> yet — run the Actions workflow (push `main` or cut a release) first.

## Repository Structure

```
alsager/                      # GitHub repo root
├─ .github/workflows/build.yml
├─ addons/alsager/
│  ├─ config.json            # image: ghcr.io/mrjelly17/alsager-{arch}
│  ├─ Dockerfile
│  ├─ run.sh
│  ├─ requirements.txt
│  ├─ src/
│  ├─ ui/
│  └─ tests/
└─ (project docs at root)
```

## config.json (image reference)

```json
{
  "name": "Alsager",
  "version": "0.3.0",
  "slug": "alsager",
  "image": "ghcr.io/mrjelly17/alsager-{arch}",
  "arch": ["amd64", "armv7", "arm64"],
  "startup": "services",
  "boot": "auto",
  "ingress": true,
  "ingress_port": 5000,
  "panel_icon": "mdi:brain",
  "panel_title": "Alsager",
  "options": { "ha_base_url": "", "ha_token": "", "poll_interval": 5 },
  "schema": { "ha_base_url": "url", "ha_token": "password", "poll_interval": "int(1,60)" },
  "map": ["config:rw", "data:rw"]
}
```

- `image` uses the `{arch}` placeholder — Supervisor substitutes the target
  architecture automatically.
- `ingress: true` serves the UI through HA (no exposed port needed).

## Local Development (without building/pushing)

For fast UI/API iteration on your machine (no Docker, no HA):

```bash
cd addons/alsager
python3 -m venv .venv
env -u PYTHONPATH .venv/bin/pip install -r requirements-dev.txt
env -u PYTHONPATH .venv/bin/python -m pytest -q
env -u PYTHONPATH ALSAGER_DATA_DIR=./data ALSAGER_CONFIG_DIR=./config \
  .venv/bin/python -m uvicorn src.main:app --port 5000
```

The app uses mock entities when no HA connection is configured, so the full
UI works end-to-end locally.

## Accessing the UI

With `ingress: true`, the UI is reachable from the HA sidebar panel.
FastAPI serves the UI at `/` and the API at `/api/`.
