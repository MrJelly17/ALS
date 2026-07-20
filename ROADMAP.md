# Roadmap

<!-- Work plan split into phases and milestones. Updated as information is gathered. -->

## Legend

- 🔴 Required (must-have)
- 🟡 Important (should-have)
- 🟢 Optimal (could-have)
- ⚫ Deferred (won't-have in this phase)

## Phase 1 — Requirements and Discovery

- Finalize all functional and non-functional requirements.
- Decide delivery model (Add-on vs custom integration vs AppDaemon).
- Choose ML-ready dataset format.
- Define Home Assistant entity selection mechanism.
<!-- TODO: add detailed phase content -->

## Phase 2 — Module 1: Dataset Creation

- Build Home Assistant Add-on web UI entry point.
- Implement entity picker in UI.
- Implement historical data extraction from HA statistics/recorder.
- Implement ML-ready file export in chosen format.
- Implement configurable lookback period.
- Store dataset in defined directory structure.
- Write unit and integration tests.
- Add documentation for setup and usage.

## Phase 3 — Pattern Detection Engine

- Design neural network architecture for time-series pattern detection.
- Implement data preprocessing and feature engineering.
- Train model on extracted dataset.
- Implement pattern detection / anomaly detection.
- Evaluate model performance.

## Phase 4 — Automation Integration

- Bridge detected patterns into Home Assistant automations.
- Implement safety controls: review before apply.
- Implement feedback loop for model improvement.

## Phase 5 — Polish and Launch

- Full Add-on packaging.
- HACS publication.
- Monitoring dashboard.
- Documentation and onboarding.

## Milestones

<!-- Item: description, target date, status (not started / in progress / done) -->
- M1: Requirements and architecture decision — status: in progress
- M2: Dataset creation module working — status: not started
- M3: Pattern detection prototype — status: not started
- M4: Home Assistant automation bridge — status: not started
- M5: Production-ready Add-on — status: not started
