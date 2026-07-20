# Alsager — Research and Analysis

> Research is updated in waves. This file records verified findings, candidate approaches, and open assumptions to validate later.

---

## 1. Feasibility of Training on Home Hardware

### Hardware Landscape
Typical Home Assistant hosts:
- Raspberry Pi 4 (4GB) / Pi 5 (8GB): ARM Cortex-A76/A72, no GPU, CPU-bound training, limited RAM.
- Intel NUC / N100 mini PC: x86_64 with AVX2, 8–32GB RAM, much more viable for moderate training.
- Virtual machines (Proxmox, ESXi): variable, depends on allocated cores/RAM.
- HA Blue / Yellow: similar to Pi 4/5 constraints.

### Real-World Estimates
For a HAR dataset of ~30 days of phone sensors:
- ~43,200 windows if sampled every minute (window length TBD).
- After labeling maybe 5–20 classes with 50–200 examples each = small dataset.
- A 1D CNN or small MLP with <50k parameters can converge in minutes to an hour on CPU.
- A tiny GRU may take 2–5x longer but still feasible for small sequences.

### Verdict
Training on home hardware **is feasible** if we keep the model small (<100k parameters) and dataset moderate (<200k windows). For weaker hosts, we can offload training to occasional scheduled runs (e.g. weekly retrain at night).

### Actual Reference Hardware (2026-07-20)
- **Host: Intel i5 + 12 GB RAM.** This is the user's real HA host.
- Implication: local training of a small 1D CNN / MLP is comfortably feasible (minutes to ~1 hour). No need for scheduled-night fallback on this host.
- **Hard constraint**: neural network must remain small (<100k params, <5 MB model file). Rules out large transformers / deep RNNs.

---

## 2. Neural Network Architectures for Lightweight HAR

### Baseline Candidates
1. **MLP on engineered features**
   - Input: statistical features per sensor per window (mean, std, min, max, energy, zero-crossings).
   - Architecture: 2–3 hidden layers, 50–200 neurons each, ReLU, dropout.
   - Pros: fastest to train, smallest file, trivial to quantize.
   - Cons: loses fine-grained temporal structure.

2. **1D CNN**
   - Input: raw or lightly preprocessed window of shape (timesteps, features).
   - Architecture: 2–3 conv layers (kernel 3–7), max pooling, 1–2 dense layers.
   - Pros: captures local temporal patterns, trains fast on CPU, good HAR track record.
   - Cons: fixed receptive field, needs reasonable window length.

3. **Tiny GRU / LSTM**
   - Input: same as CNN.
   - Architecture: 1 layer, 32–64 hidden units, return_sequences=False.
   - Pros: models sequence order, good for variable-length dependency.
   - Cons: slower on CPU than CNN due to sequential computation.

4. **Temporal Convolutional Network (TCN)**
   - Dilated causal convolutions, residual blocks.
   - Pros: parallelizable, large receptive field, competitive with RNN.
   - Cons: slightly more complex to implement.

### Recommended Starting Point
- **1D CNN** as primary candidate: good balance of speed, size, accuracy.
- **MLP on features** as lightweight fallback for very constrained devices.
- **GRU** optionally if sequence ordering proves critical.

### Inference
- Runtime inference should use ONNX Runtime or TFLite for smallest footprint.
- Model file size target: <5MB.

---

## 3. Data Pipeline and Database

### Ingestion Strategy
- Event-driven via HA WebSocket API / event bus.
- Fallback polling every 60s for missed events.
- Each state change → append to local store with timestamp and entity_id.

### Database Candidates
1. **SQLite**
   - Pros: built into Python, zero external dependency, ACID, small footprint.
   - Cons: single writer, can grow large; no built-in compression.
   - Suitable for <10M rows.

2. **DuckDB**
   - Pros: fast analytical queries, built-in Parquet/compression, columnar.
   - Cons: slightly heavier than SQLite, but still single binary / Python lib.
   - Excellent for ML export pipelines.

3. **Parquet/JSONL files**
   - Append-only log files, one per day or per entity.
   - Pros: trivial, no DB process, excellent compression with ZSTD/Parquet.
   - Cons: querying requires reading whole files; window extraction must build indexes.

### Recommended Approach
- **Primary store**: SQLite for reliable, simple ingestion.
- **Export format**: Parquet (one file per training dataset) for downstream ML.
- **Schema**: Tall format — one row per state change.
  - Columns: `entity_id`, `state`, `last_updated`, `attributes_json`, `domain`.
- Window extraction happens at export/training time by pivoting and resampling.

### Storage Size Estimate
- 30 days, 50 sensors, 1 event/min each ≈ 2.16M rows.
- SQLite file ~200–500MB depending on attributes size. Acceptable.

---

## 4. Home Assistant Add-on Constraints

### What We Know
- Add-ons run in Docker containers.
- Can expose web UI via ingress (panel_iframe or dedicated add-on page).
- Can run background services inside the container.
- Can access HA API via internal URL (supervisor API) or HTTP.
- Persistent storage via `/config` or `/data` mapped volumes.

### Implication for Architecture
- Ingestion daemon = background process in add-on container.
- Database stored in `/data` (persistent volume).
- Web UI exposed via HA ingress or panel_iframe.
- Training script can be invoked from UI or scheduled cron inside add-on.
- Model files stored in `/data/models`.

### Open Questions
- Does HA supervisor limit CPU/memory for add-ons? Yes, but defaults are generous enough for modest training.
- Can add-ons access Supervisor API for entity listing? Yes, via internal endpoints.
- Can add-ons modify HA automations? Yes, via HA REST API (requires long-lived access token).

---

## 5. Technology Stack Recommendations

### Backend
- Python 3.11
- FastAPI (web server, easy async, OpenAPI)
- SQLite/SQLAlchemy (ingestion DB)
- Home Assistant Python API (hass-client or aiohttp)
- ONNX Runtime (inference)
- PyTorch (training, research flexibility)

### Frontend
- React or Vue via Vite.
- HA-lovelace card or standalone panel_iframe.
- Simple charting: Chart.js, Recharts, or ECharts.

### ML Pipeline
- NumPy, Pandas for preprocessing.
- PyTorch Lightning or pure PyTorch for model training.
- ONNX export for runtime.

### DevOps
- Docker / Docker Compose for add-on.
- GitHub Actions for CI/CD.
- Python tooling: ruff, mypy, pytest.

---

## 6. Key Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Training too slow on Pi | Default to light 1D CNN; enable weekly retrain schedule; skip training on weak HW and notify user. |
| Database grows too large | Partition by month; compress old partitions; limit retention via config. |
| Overfitting on small labeled dataset | Use data augmentation (jittering, scaling); enforce early stopping; ask user for more labels. |
| Privacy concerns | All data stays local; no telemetry; clear data retention policy. |
| HA API rate limits | Batch queries; cache entity list; respect HA's request limits. |

---

## 7. Next Research Steps

1. **Verify exact sensor entities created by HA Mobile app** on both Android and iOS.
   - Accelerometer: `sensor.accelerometer_x`, etc.
   - Gyroscope, magnetometer, activity sensors.
   - Network type, SSID, battery, location, etc.
   - Frequency of updates.

2. **Prototype small HAR CNN** on public smartphone HAR dataset (e.g. WISDM, UCI HAR) to measure training time on low-end CPU.

3. **Benchmark SQLite insert rate** for ~1k inserts/sec sustained with Python asyncio.

4. **Prototype HA Add-on minimal UI** to validate ingress and API access.

5. **Review legal/terms** for using HA name and packaging as add-on.

---

## Notes

- This document should be treated as a research backlog, not a final architecture decision.
- Assumptions must be validated with real data and hardware tests before implementation.
