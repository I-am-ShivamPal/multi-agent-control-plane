# RL Decision Layer - Universal DevOps Runtime Intelligence

## Overview
This RL Decision Layer provides conservative, rule-based decisions for DevOps automation. It is designed for production safety with strict boundaries and no learning capabilities.

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the decision layer
python decision.py

# Launch the advanced dashboard
streamlit run dashboard.py
```

## Dashboard Features
The advanced dashboard provides:
- **Interactive Decision Maker**: Input runtime signals and see live decisions
- **Environment Scopes**: Visual matrix of allowed actions per environment
- **Signal Requirements**: Clear breakdown of required vs optional signals
- **Logs & Metrics**: Real-time monitoring of system behavior and safety metrics
- **Examples**: Before/after behavior demonstrations
- **Safety Status**: Production readiness indicators

### Dashboard Screenshots
- Overview page with system metrics and architecture diagram
- Interactive decision maker with real-time feedback
- Environment scope matrix with visual heatmaps
- Safety metrics and downgrade tracking

## Files
- `decision.py`: Core RL decision logic
- `dashboard.py`: Advanced Streamlit dashboard
- `README.md`: Documentation and usage
- `examples.json`: Test cases and examples
- `requirements.txt`: Python dependencies
- `run_dashboard.bat`: Windows launcher script
- `final_logs.txt`: System logs and test outputs

## RL Action Scope Guarantees
The RL layer enforces strict action boundaries per environment:

- **dev**: noop, scale_up, scale_down, restart
- **stage**: noop, scale_up, scale_down
- **prod**: noop, restart

Any decision that would violate these scopes is automatically downgraded to NOOP with logging.

## No Learning Disclaimer
This RL layer is **decision-only** with **no learning occurs in demo**. The reward loop is explicitly disabled. All decisions are deterministic and rule-based.

## Runtime Signal Consumption
The RL layer now consumes **real runtime signals** from Shivam's orchestrator, not simulated inputs:

- **Event Sources**: Runtime event normalizer, metrics collector, health/failure events
- **Validation**: Required signals (app, env, state), data type validation, timestamp freshness
- **Safety**: NOOP on missing/invalid/malformed/delayed signals
- **Adaptation**: Normalized events → RL state format

## What RL Decides
RL makes conservative, rule-based decisions based on validated runtime signals:

- **restart**: When state = 'critical' OR errors_last_min > 10
- **scale_up**: When latency_ms > 5000 AND env allows scaling
- **scale_down**: When state = 'healthy' AND env allows scaling
- **noop**: Default action, also on insufficient/unsafe conditions

## What RL Will NEVER Do
- **No learning**: Reward loop disabled, no internal state evolution
- **No exploration**: Deterministic decisions only
- **No unsafe actions**: All decisions filtered through environment-specific action scopes
- **No decisions on bad data**: NOOP on missing/malformed/delayed signals
- **No prod scaling**: scale_up/scale_down never allowed in prod environment

## Failure Behavior Guarantee
- **Missing signals**: NOOP with warning log
- **Malformed values**: NOOP with validation error
- **Delayed signals**: NOOP if >5 minutes old
- **Invalid environment/state**: NOOP with validation error
- **Unsafe actions**: Downgraded to NOOP with safety log
- **All failures logged**: Full traceability for debugging

## Known Limitations & Why They Are Safe
**Known Risk**: False positives from error thresholds (e.g., temporary error spikes).

**Safety Protections**:
- Orchestrator enforces final execution safety
- Prod guards prevent unsafe actions
- NOOP downgrades ensure conservative behavior
- Required signal validation prevents decisions on insufficient data

## Final Readiness Note
The RL Decision Layer is now aligned with runtime reality, enforces strict production-safe boundaries, and is ready for live demo integration. All corrections implemented:
- ✅ Action scope enforcement with NOOP downgrades
- ✅ Required vs optional signal handling
- ✅ Disabled reward loop and learning claims
- ✅ Conservative behavior with explicit safety measures
- ✅ Live runtime event consumption with validation
- ✅ Deterministic decisions with no internal state evolution
- ✅ Closed-loop integration with orchestrator safety validation
- ✅ End-to-end failure scenario handling

## Demo Readiness Declaration
**SAFE FOR LIVE DEMO ON STAGE**

The RL Decision Layer has been hardened for production use with:
- Zero unsafe autonomy
- Zero ambiguity in decision making
- Demo-grade determinism
- Real runtime signal consumption
- End-to-end safety validation

Ready for integration with Shivam's orchestrator.
- ✅ Live runtime event consumption with validation
- ✅ Deterministic decisions with no internal state evolution

## Usage
```python
from decision import RLDecisionLayer

rl = RLDecisionLayer()
decision = rl.make_decision({
    'app': 'web',
    'env': 'prod',
    'state': 'critical'
})
print(decision)  # {'action': 'restart', 'reason': '...', ...}
```

## Signal Requirements
- **REQUIRED**: app, env, state (NOOP if missing)
- **OPTIONAL**: latency_ms, errors_last_min (conservative defaults if missing)