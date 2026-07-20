# Alsager

Alsager is an AI-powered pattern detection system for Home Assistant.
It continuously monitors selected sensors, stores state history in a lightweight local database, exports ML-ready datasets, trains neural networks on the data, and feeds learned patterns back into Home Assistant automation.
Delivered primarily as a Home Assistant Add-on with a web UI.

## System Architecture

Alsager has three core layers:

1. **Ingestion daemon** — background service that monitors selected HA entities 24/7 and stores state changes in a local optimized database.
2. **Dataset export** — UI-driven module that reads from the local database and produces ML-ready dataset files for training.
3. **Pattern engine** — trains neural networks on exported datasets and pushes detected patterns back into HA as automations.
4. **Runtime inference engine** — runs the trained model in the background against live sensor streams and triggers automations.

## Key Constraint

Alsager must run inside Home Assistant — either as an official Add-on or as a custom integration/component.
Current preferred direction: **Home Assistant Add-on with web UI**.
Final delivery model will be finalized once architecture is fully understood.

## Working Mode

- High-level vision first, detailed decisions later.
- Requirements and architecture are expected to evolve as more context is gathered.
- This document is the single source of truth and will be updated continuously.

## Primary Use Case

Phone-based activity recognition through Home Assistant mobile app sensors:
- Accelerometer, gyroscope, battery, network (WiFi/Cellular), location, steps, orientation
- Pattern extraction from temporal sensor history
- Labeled activity detection (e.g. "commuting to work", "working out", "at home")
- User-driven labeling during training sessions
- Learned patterns trigger automations in Home Assistant