# Rityadani's RL Decision Layer Integration

This directory contains Rityadani's RL Decision Layer for Universal DevOps Runtime Intelligence.

## Location
`core/rl/rityadani_decision_layer/`

## Contents

### Core Files
- **`decision.py`** - Rule-based RL decision logic with strict safety boundaries
- **`dashboard.py`** - Advanced Streamlit dashboard for interactive decision making
- **`examples.json`** - Test cases and example scenarios
- **`requirements.txt`** - Python dependencies
- **`run_dashboard.bat`** - Windows launcher script
- **`final_logs.txt`** - System logs and test outputs

## What This Provides

### Conservative Rule-Based Decisions
- No learning or exploration (deterministic only)
- Strict action scope per environment:
  - **dev**: noop, scale_up, scale_down, restart
  - **stage**: noop, scale_up, scale_down
  - **prod**: noop, restart

### Runtime Signal Consumption
- Validates required signals: app, env, state
- Optional signals: latency_ms, errors_last_min
- NOOP on missing/invalid/delayed signals

### Safety Guarantees
- Action scope enforcement with automatic downgrades to NOOP
- No unsafe actions in production
- All failures logged with full traceability

## Quick Start

### Run Decision Layer
```bash
cd core/rl/rityadani_decision_layer
python decision.py
```

### Launch Dashboard
```bash
cd core/rl/rityadani_decision_layer
streamlit run dashboard.py
```

## Integration with Main System

This RL decision layer complements the existing RL API in `core/rl/external_api/`:

- **`external_api/`** (Ritesh) - Demo-frozen RL API for website integration
- **`rityadani_decision_layer/`** (Rityadani) - Rule-based decision layer with dashboard

Both can coexist and serve different purposes:
- External API: Production demo with frozen decisions
- Decision Layer: Development/testing with interactive dashboard

## Key Features

1. **Deterministic Behavior** - Same input always produces same output
2. **Environment-Aware** - Different action scopes per environment
3. **Signal Validation** - Comprehensive input validation
4. **Safety First** - Conservative defaults, NOOP on uncertainty
5. **Interactive Dashboard** - Visual decision making and monitoring

## Original Repository
Source: https://github.com/rityadani/devops-layer.py

Integrated on: 2026-02-11
