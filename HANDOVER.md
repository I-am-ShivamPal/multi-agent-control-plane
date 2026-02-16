# HANDOVER DOCUMENT - Pravah (Multi-Agent CI/CD System)

## 🌐 Live Deployment

**Live URL**: https://multi-intelligent-agent.onrender.com/

**Status**: ✅ Active and operational

### Available Endpoints

- **Health Check**: `GET https://multi-intelligent-agent.onrender.com/health`
- **Process Runtime Event**: `POST https://multi-intelligent-agent.onrender.com/api/runtime/process`
- **Demo Cycle**: `POST https://multi-intelligent-agent.onrender.com/api/demo/cycle`
- **Validation**: `GET https://multi-intelligent-agent.onrender.com/api/demo/validate`

## 📦 Repository

**GitHub Repository**: https://github.com/username/Multi-Intelligent-agent-system-main

**Key Files**:
- `middleware.py` - Transport + validation layer
- `runtime_payload_schema.json` - Frozen contract
- `app.py` - Flask API server
- `ui/dashboards/dashboard.py` - Unified interface
- `ui/dashboards/unified_component.py` - Pipeline visualization
- `validate_demo_lock.py` - Demo lock validation
- `DEPLOYMENT.md` - Deployment guide

## 🔄 Middleware Layer

**File**: `middleware.py`

```python
"""Middleware: Transport + Validation Only. NO business logic."""

import json
import requests
from jsonschema import validate, ValidationError

# Load frozen contract
with open("runtime_payload_schema.json") as f:
    SCHEMA = json.load(f)

def validate_payload(payload):
    """Validate against frozen contract."""
    validate(instance=payload, schema=SCHEMA)

def send_to_rl(payload, rl_endpoint):
    """Send validated payload to RL endpoint."""
    response = requests.post(rl_endpoint, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()

def process_runtime_event(payload, rl_endpoint):
    """
    Bridge layer: validate → send → return.
    
    Args:
        payload: Runtime data dict
        rl_endpoint: RL system URL
        
    Returns:
        dict: {"decision": ..., "status": "success"/"error"}
    """
    try:
        validate_payload(payload)
        decision = send_to_rl(payload, rl_endpoint)
        return {"decision": decision, "status": "success"}
    except ValidationError as e:
        return {"decision": None, "status": "error", "error": f"Invalid payload: {e.message}"}
    except requests.RequestException as e:
        return {"decision": None, "status": "error", "error": f"RL endpoint failed: {str(e)}"}
```

**Responsibilities**:
1. Validate payload against frozen schema
2. Transport to RL endpoint via POST
3. Return structured response
4. NO business logic - pure bridge layer

## 🖥️ Unified Interface

**Access**: Run `streamlit run ui/dashboards/dashboard.py`

**Features**:
- **Runtime State Panel**: Shows app, state, latency, errors, workers
- **RL Decision Panel**: Displays action, confidence, timestamp
- **Action Executed Panel**: Shows orchestrator execution status
- **Environment Status Panel**: Displays env, health, uptime

**No dual dashboards** - All information in single view.

## 🎬 Demo Walkthrough Script

**One-Paragraph Demo**:

Access the Pravah system at https://multi-intelligent-agent.onrender.com/ and test the health endpoint to confirm the service is running. Send a POST request to `/api/demo/cycle` to trigger a complete demonstration: Pravah ingests a runtime event (crashed application in stage environment), validates the payload against the frozen contract, sends it to the RL decision layer which deterministically returns a `restart_service` action with full explanation, and the orchestrator executes the safe action while respecting environment gates. View the unified Pravah dashboard by running `streamlit run ui/dashboards/dashboard.py` to see all four pipeline stages (Runtime State → RL Decision → Action Executed → Environment Status) in a single interface, with real-time updates showing the complete flow from failure detection to automated recovery. Run `GET /api/demo/validate` to execute all four test scenarios (dev crash, stage overload, prod freeze, new app observation) and verify deterministic behavior, environment gate enforcement, and zero UI crashes as documented in `logs/DEMO_LOCK_PROOF.json`.

## ✅ Validation Results

**Proof File**: `logs/DEMO_LOCK_PROOF.json`

**Summary**:
- Total Scenarios: 4
- Passed: 4/4 (100%)
- UI Crashes: 0
- Q-Table Exposures: 0
- Determinism Confirmed: ✅
- Environment Gates Respected: ✅

**Test Scenarios**:
1. ✅ Crash in dev → restart
2. ✅ Overload in stage → scale_up (deterministic)
3. ✅ Overload in prod → noop (freeze mode)
4. ✅ New app ingestion → observation mode

## 🚀 Quick Start Commands

```bash
# Test live deployment
curl https://multi-intelligent-agent.onrender.com/health

# Run demo cycle
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/cycle

# Run validation
curl https://multi-intelligent-agent.onrender.com/api/demo/validate

# Local dashboard
streamlit run ui/dashboards/dashboard.py

# Local validation
python validate_demo_lock.py
```

## 📋 Contract Schema

**File**: `runtime_payload_schema.json`

**Required Fields** (no optionals):
- `app` (string): Application identifier
- `env` (enum): "dev", "stage", "prod"
- `state` (enum): "running", "crashed", "degraded", "starting", "stopped"
- `latency_ms` (number): Response latency ≥ 0
- `errors_last_min` (integer): Error count ≥ 0
- `workers` (integer): Worker count ≥ 0

**No additional properties allowed** - Strict validation enforced.

## 🔒 Environment Behavior

**Stage** (Demo Mode):
- Deterministic decisions (confidence: 1.0)
- Allowlist: restart, scale_up, scale_down, noop
- Predictable for demonstrations

**Prod** (Freeze Mode):
- Only `noop` allowed
- All other actions blocked
- Safety guards active
- Explanation: "Production freeze mode - no actions allowed"

## 📞 Support

**Documentation**:
- `DEPLOYMENT.md` - Deployment guide
- `README.md` - System overview
- `DEMO_LOCK_PROOF.json` - Validation proof

**Status**: Production-ready, fully validated, no placeholders.

---

**Handover Complete**: 2026-02-14
