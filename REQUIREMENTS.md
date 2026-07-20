# Requirements

## Hard Constraints

- **Home Assistant only**: the solution must operate inside Home Assistant.
  - Possible delivery forms: official Add-on, custom integration, AppDaemon app, HACS component.
  - Final delivery model will be chosen once architecture and requirements are solid.
- Language: all code, docs, and configs must be in English. **Web UI text is also English** (resolved 2026-07-20).
- Clean, well-documented, reproducible project.
- All data stays local; nothing is sent to external services unless explicitly configured.
- **Neural network must be small**: target <100k parameters, model file <5 MB (resolved 2026-07-20 — hard constraint).

## Functional Requirements

### Module 1: Ingestion Daemon

- Background service running 24/7 inside Home Assistant.
- Monitors user-selected entities for state changes.
- Stores every state change in a lightweight, optimized local database.
- Database must be fast, compact, and suitable for later ML training.
- Supports adding/removing monitored entities without data loss.
- Survives Home Assistant restarts without duplicate entries or gaps.

### Module 2: Dataset Export (UI: "Download and Create Dataset")

- UI section to select entities and date range (default: last 30 days).
- Reads from the local ingestion database (not HA history API).
- Exports data in ML-ready format compatible with TensorFlow / PyTorch / ONNX.
- Supports incremental/append exports.
- Stores exported datasets in a defined directory structure.
- User can trigger export on-demand from the UI.

### Module 3: Pattern Detection Engine

- Receives exported datasets as input.
- Trains a neural network on historical sensor data.
- Detects patterns / anomalies / correlations across sensors.
- Pushes learned patterns back into Home Assistant as automations.
- Supports model versioning and retraining.

### Module 4: Manage Monitored Entities

- UI to add/remove entities from the monitored set.
- UI to view ingestion status, database size, last update per entity.
- UI to pause/resume ingestion per entity or globally.

### Module 5: Dashboard / Insights

- UI showing learned patterns, automation impact, model performance.
- Manual override for automatic actions.

### Module 6: Interactive Training and Labeling (primary use case)

- UI timeline view of sensor history with visualization.
- User can select time window and provide label (e.g. "going to work", "at home").
- System can suggest candidate patterns from history and ask user to confirm or name them.
- Labels are stored with dataset and used for supervised training.
- Supports multi-class classification of repeating activities.
- Training loop: extract → label → train → evaluate → iterate.

### Module 7: Runtime Inference and Automation (post-training)

- Runs trained model continuously against live sensor stream.
- Converts real-time sensor data into model input windows on the fly.
- Performs inference when a full window is available.
- Evaluates probabilities/confidence and matches against learned patterns.
- Triggers Home Assistant automation actions when pattern confidence exceeds threshold.
- Supports periodical retraining / online learning from new labeled data.
- Logs all decisions and exposes confidence for transparency.

## Non-Functional Requirements

- User interface must be accessible from Home Assistant sidebar or Add-on panel.
- Ingestion daemon must have minimal CPU and memory footprint.
- Database must be robust to crashes and HA restarts.
- All components must be observable (logs, metrics).
- Dataset export must be reproducible (deterministic ordering, stable schema).

## Open Questions

- What database engine fits best for append-only time-series on limited hardware? (SQLite, DuckDB, Parquet log, InfluxDB, TinyDB, custom binary?)
- What is the optimal record schema for later ML training? (wide per-timestamp rows, long tall rows, hybrid?)
- Compression strategy for the local database? (none, LZ4, ZSTD, SQLite built-in)
- Should ingestion be event-driven (via HA websocket/events) or polled (periodic REST calls)?
- What is the target HA host hardware? (Pi 4/5, NUC, VM, HA Blue, etc.)
- Expected number of monitored entities and events per day?
- Should the system support multiple independent monitoring profiles?
- Export format: single file per entity, one wide matrix, or TFRecord shards?
- How should model versioning be stored and managed?
- Should inferred automations act immediately, or queue for user review?
