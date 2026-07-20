# Alsager — Ideas and Brainstorming

## Core Concept

Continuous monitoring of Home Assistant entities (especially phone sensors) → ingestion into optimized local database → interactive labeling → neural network training → pattern-based automations.

## Phone Sensors Target (via HA mobile app)

- Accelerometer (x, y, z)
- Gyroscope
- Magnetometer / orientation
- Battery level / charging state
- Network type (WiFi / Cellular / SSID)
- Location (with user consent)
- Steps / movement activity
- Ambient noise (if available)
- Device motion / still detection

## Activity Recognition Use Cases

- **Commuting**: leaving home → driving/transit → arriving at work
- **Workout**: movement patterns, duration, intensity
- **Sleep**: phone still, charging, location bedtime
- **Presence**: home / away / work based on location + WiFi + sensor patterns
- **Recurring routines**: weekly patterns in movement and connectivity

## Interactive Labeling Flow

1. System shows timeline of sensor readings for selected window.
2. User labels window with activity name.
3. System suggests similar windows from history ("did you also go to work on Tuesday?").
4. Labels become training labels for neural network.
5. After training, system can detect repeating labeled patterns automatically.

## ML Approach Ideas

- Time-series classification on multi-sensor windows.
- Self-supervised pretraining on raw sensor history, then fine-tuning on user labels.
- Online / incremental learning to improve over time without full retrain.
- Explainability: which sensors contributed most to a detected pattern.

## UI Ideas

- "Label Session" mode: user actively teaches the model.
- Timeline scrubber with sensor intensity heatmap.
- Predicted activity feed with confidence score and manual correction buttons.
- Automation preview: "if Alsager detects you are commuting, turn on car heater at 7:15".

## Future Ideas

- Voice commands via HA to log activities ("I'm starting workout").
- Integration with HA energy dashboard.
- Anomaly detection (unusual activity at unusual time).
- Multi-user support (different phones, different profiles).
- Context-aware suggestions ("it's usually cold when you drive to work — enable seat heater?").
