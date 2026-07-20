# Alsager — Open Questions

This file contains every question that still needs clarification before Alsager can move from planning to implementation.
Questions are grouped by area. Answer them in any order; add your responses directly under each question.
Update this file as questions are resolved.

---

## Resolved Decisions (2026-07-20)

- **Language**: All project code, docs, and configs are written in **English**. User–assistant conversation is in Polish. (Resolves REQ "English" rule + communication channel.)
- **HA host**: Intel **i5 + 12 GB RAM**. Viable for local training of small models.
- **Model size**: Neural network **must be small** (target <100k params, model file <5 MB per RESEARCH). Hard constraint — no large architectures.
- **Scope of first test**: i5/12 GB is the reference hardware; training runs locally but must respect the small-model constraint. (Weak-HW fallback in RESEARCH stays relevant only if porting to Pi later.)
- **UI language**: Add-on web UI is also in **English** (consistent with the project-wide English rule — covers code, docs, configs, and UI text).
- **Delivery / deployment (2026-07-20)**: Home Assistant Add-on distributed via a **GitHub repository** (`https://github.com/MrJelly17/ALS`) added in HA as a repository. The image is **built by GitHub Actions** (`.github/workflows/build.yml`) per-arch and pushed to **GHCR** (`ghcr.io/mrjelly17/alsager-{arch}`); HA pulls the prebuilt image (no local Docker build). `config.json` references it via `"image": "ghcr.io/mrjelly17/alsager-{arch}"`. This resolves the earlier local-folder / `repository` URL error and the `ghcr.io/...:0.0.6` 404 (the image now exists in GHCR after a workflow run). Resolves OPEN_QUESTIONS #28/#29 (GitHub-based distribution; auto-update handled by HA once the repo is added).

---

# Hardware and Environment

1. ~~On which device/architecture will you first test Alsager?~~ **RESOLVED: i5 + 12 GB RAM.**
2. Should the project be optimized from the start for the weakest supported hardware, or first for your own setup?
   - **Note**: small-model constraint applies regardless; weakest-HW path only matters if later porting to Pi.
3. Do you have a dedicated volume/partition in HA for Alsager data, or should it live under `/config`?

---

# Sensors and Input Data

4. ~~Which exact HA Mobile sensors do you see in your HA?~~ **RESOLVED (mock):** until real `entity_id`s are provided, the add-on uses a realistic **mock entity list** (accelerometer x/y/z, gyroscope x/y/z, battery_level, wifi_connection, mobile_data_connection_type, steps, activity, binary_sensor.phone_charging, device_tracker.phone). Real HA listing (REST/WebSocket) lands in MVA-3. Provide your real `entity_id`s from Developer Tools → States when ready.
5. Do you prefer entity selection by name, or by category/device? (e.g. "all sensors from iPhone" vs single entities) — **Default in UI MVA-2: filter by name + domain dropdown (per-entity selection).** Bulk-by-device can be added later.
6. Should there be a default preset list of entities to monitor, or start empty? — **Start empty; user selects via UI.** (Mock list is only for display, not auto-monitored.)
7. What should happen when entities disappear (e.g. after integration removal)? Skip, archive, or remove from monitoring? — **Open (default: keep in monitored set but skip ingestion errors; revisit in MVA-3).**

---

# Time Windowing and Structure

8. What is the intended analysis window length? (e.g. 30s, 1min, 5min, 10min?)
9. Should windows be non-overlapping or overlapping with a sliding step?
10. Do you need sliding windows with a configurable stride, or static fixed segments?

---

# Labeling and Training

11. What should the labeling flow look like? (manual only, system suggestions, batch labeling?)
12. Should labels be assigned to time windows, or to longer sessions?
13. Can one activity span multiple windows, or should it be one label per fragment?
14. What should happen when the model fails to recognize a pattern? Ask the user, ignore, or log silently?
15. Do you prefer offline training (every X days) or online/incremental learning?

---

# UI and User Experience

16. Should the UI appear in the HA sidebar as a panel, or open as a separate browser tab?
17. Do you prefer a simple functional UI, or a richer UI with charts and visualizations?
18. Do you want a timeline view plotting multiple sensors at once?
19. Should the UI show model decision history with manual correction options?

---

# Output Automations

20. What types of HA actions should Alsager generate? (turn on/off entities, trigger scenes, change states, send notifications)
21. Should actions fire immediately or with a configurable delay?
22. Should there be a rate limit or circuit breaker to prevent excessive automation?
23. What happens when a pattern disappears or changes? Should the automation expire, or remain pattern-bound?

---

# Security and Privacy

24. Must everything stay strictly local? Is optional external export ever desired?
25. Should the local database be encrypted on disk?
26. What is the backup strategy for models and database? Automatic backups, manual only?
27. How should the HA long-lived access token for modifying automations be stored and protected?

---

# Publication and Distribution

28. Do you plan to publish on HACS, GitHub Releases, or keep it private?
29. Is automatic add-on update required from the start?
30. Should the UI include model versioning display and management?

---

# Testing and Quality

31. Which test types are required? (unit, integration, E2E)
32. Do you want CI/CD from the beginning, or introduced later?
33. What level of documentation is expected? (user guide, developer guide, API docs)

---

# Model and Retraining

34. Should retraining use only new labels, or the full dataset each time?
35. Do you want model versioning with rollback capability?
36. Should automatic retraining be triggered when new data arrives?
37. How should model success be measured? (accuracy, precision, recall, F1, user satisfaction)

---

> Last updated: 2026-07-20
> Status: all questions open — awaiting user input
