# QUICK REFERENCE - 60 Minute Integration

## Live System
**URL**: https://multi-intelligent-agent.onrender.com/
**Health**: GET /health
**Demo**: POST /api/demo/cycle
**Validate**: GET /api/demo/validate

## Repository
**GitHub**: https://github.com/username/Multi-Intelligent-agent-system-main

## Key Files
- `middleware.py` - Bridge layer (validate → transport → return)
- `runtime_payload_schema.json` - Frozen contract
- `app.py` - Flask API
- `ui/dashboards/unified_component.py` - 4-panel interface
- `validate_demo_lock.py` - Demo validation
- `logs/DEMO_LOCK_PROOF.json` - Validation proof

## Middleware (middleware.py)
```python
def process_runtime_event(payload, rl_endpoint):
    validate_payload(payload)  # Check schema
    decision = send_to_rl(payload, rl_endpoint)  # POST to RL
    return {"decision": decision, "status": "success"}  # Return
```

## Contract (runtime_payload_schema.json)
Required: app, env, state, latency_ms, errors_last_min, workers
No optionals. No additional properties.

## Unified Interface
Run: `streamlit run ui/dashboards/dashboard.py`
Panels: Runtime State | RL Decision | Action Executed | Environment Status

## Demo Walkthrough
Access https://multi-intelligent-agent.onrender.com/ → POST /api/demo/cycle → Pravah ingests crashed app event → Validates payload → RL returns restart_service → Orchestrator executes → View unified Pravah dashboard for complete pipeline → GET /api/demo/validate for all 4 scenarios → Check logs/DEMO_LOCK_PROOF.json for proof.

## Validation Results
4/4 scenarios PASSED
- Dev crash → restart ✅
- Stage overload → scale_up (deterministic) ✅
- Prod overload → noop (freeze) ✅
- New app → observe ✅

## Environment Behavior
**Stage**: Deterministic, allowlist enforcement
**Prod**: Freeze mode, noop only

## Test Commands
```bash
curl https://multi-intelligent-agent.onrender.com/health
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/cycle
curl https://multi-intelligent-agent.onrender.com/api/demo/validate
streamlit run ui/dashboards/dashboard.py
python validate_demo_lock.py
```

**Status**: Production-ready. No placeholders. No local-only logic.
