# Live Demo Scenarios Guide

## Overview

This system provides **4 live-callable demo scenarios** that demonstrate autonomous agent decision-making. Each scenario follows the pattern: **Input → Decision → Reason → Safety**.

## Live Demo URL

Base URL: https://multi-intelligent-agent.onrender.com

## Scenario List

### Quick Access

```bash
# List all available scenarios
GET https://multi-intelligent-agent.onrender.com/api/demo/scenarios
```

---

## Scenario 1: Crash Recovery

**Endpoint**: `POST /api/demo/crash`

### Description
Demonstrates how the agent detects and recovers from application crashes.

### Flow

#### 1️⃣ Input
```json
{
  "event_type": "health_check_failed",
  "app_name": "payment-service",
  "state": "crashed",
  "health_status": "DOWN",
  "error_count": 5,
  "crash_reason": "Out of memory"
}
```

#### 2️⃣ Decision
- **Action**: `RESTART`
- **Action Index**: `1` (restart_service)
- **Source**: RL Decision Layer

#### 3️⃣ Reason
> "Application unhealthy (crashed state), restart required to restore service. Error count (5) exceeds threshold."

#### 4️⃣ Safety
```json
{
  "validation": "PASSED",
  "safe_to_execute": true,
  "reason": "Restart action allowed for crashed applications",
  "constraints": [
    "Max 3 restarts per hour",
    "Requires crash state"
  ]
}
```

### Try It

```bash
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/crash
```

**Expected Response**:
```json
{
  "scenario": "CRASH",
  "timestamp": "2026-02-07T...",
  "flow": {
    "1_input": {...},
    "2_decision": {"action": "restart", "action_index": 1},
    "3_reason": "Application unhealthy...",
    "4_safety": {"validation": "PASSED", ...}
  }
}
```

---

## Scenario 2: Overload Handling

**Endpoint**: `POST /api/demo/overload`

### Description
Demonstrates how the agent scales resources when detecting high CPU/memory usage.

### Flow

#### 1️⃣ Input
```json
{
  "event_type": "resource_alert",
  "app_name": "api-gateway",
  "cpu_usage": 95,
  "memory_usage": 92,
  "request_queue_depth": 1500,
  "current_instances": 2,
  "max_instances": 10
}
```

#### 2️⃣ Decision
- **Action**: `SCALE_UP`
- **Action Index**: `2` (scale_up)
- **Source**: RL Decision Layer

#### 3️⃣ Reason
> "Resource exhaustion detected (CPU: 95%, Memory: 92%). Scaling up to handle increased load. Request queue depth (1500) indicates demand exceeds capacity."

#### 4️⃣ Safety
```json
{
  "validation": "PASSED",
  "safe_to_execute": true,
  "reason": "Scale up allowed within instance limits",
  "constraints": [
    "Current: 2 instances",
    "Max: 10 instances",
    "CPU > 90%"
  ]
}
```

### Try It

```bash
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/overload
```

---

## Scenario 3: False Alarm (NOOP Safety)

**Endpoint**: `POST /api/demo/false-alarm`

### Description
Demonstrates how the agent avoids taking action on benign anomalies.

### Flow

#### 1️⃣ Input
```json
{
  "event_type": "metric_spike",
  "app_name": "analytics-service",
  "cpu_usage": 75,
  "memory_usage": 70,
  "error_rate": 0.02,
  "duration_seconds": 30,
  "pattern": "transient_spike",
  "previous_trend": "stable"
}
```

#### 2️⃣ Decision
- **Action**: `NOOP` (No Operation)
- **Action Index**: `0`
- **Source**: RL Decision Layer

#### 3️⃣ Reason
> "Metrics within acceptable threshold. Transient spike (30s duration) does not warrant intervention. Error rate (2%) is below 5% threshold. Pattern indicates temporary fluctuation, not sustained issue."

#### 4️⃣ Safety
```json
{
  "validation": "PASSED",
  "safe_to_execute": true,
  "reason": "NOOP prevents overreaction to transient spikes",
  "constraints": [
    "Error rate < 5%",
    "Duration < 60s",
    "Pattern: transient"
  ]
}
```

### Try It

```bash
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/false-alarm
```

**Key Learning**: This demonstrates the agent's **self-restraint** - knowing when NOT to act is as important as knowing when to act.

---

## Scenario 4: New App Onboarding (Text Input)

**Endpoint**: `POST /api/demo/onboarding`

### Description
Demonstrates how the agent onboards new applications from free-text descriptions.

### Flow

#### 1️⃣ Input
```json
{
  "text": "This is my backend payment service"
}
```

**Text is parsed into structured event**:
```json
{
  "event_type": "app_onboarded",
  "app_name": "payment-service",
  "runtime_type": "backend",
  "state": "newly_onboarded",
  "observation_period_hours": 24
}
```

#### 2️⃣ Decision
- **Action**: `NOOP`
- **Action Index**: `0`
- **Source**: Onboarding Policy

#### 3️⃣ Reason
> "New application requires observation period. No actions allowed for newly onboarded apps (policy). Observation period: 24 hours. Allows system to collect baseline metrics before automated intervention."

#### 4️⃣ Safety
```json
{
  "validation": "PASSED",
  "safe_to_execute": true,
  "reason": "NOOP enforced for newly onboarded applications",
  "constraints": [
    "State: newly_onboarded",
    "No actions allowed",
    "Observation period required"
  ]
}
```

### Try It

```bash
# Default text
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/onboarding

# Custom text
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/onboarding \
  -H "Content-Type: application/json" \
  -d '{"text": "This is my frontend web application"}'
```

---

## Run All Scenarios

**Endpoint**: `POST /api/demo/run-all`

Execute all 4 scenarios in sequence and get comprehensive results.

```bash
curl -X POST https://multi-intelligent-agent.onrender.com/api/demo/run-all
```

**Response Structure**:
```json
{
  "demo_run": "complete",
  "scenarios_executed": 4,
  "results": [
    { "scenario": "CRASH", ... },
    { "scenario": "OVERLOAD", ... },
    { "scenario": "FALSE_ALARM", ... },
    { "scenario": "ONBOARDING", ... }
  ]
}
```

---

## Key Takeaways

### 1. Transparent Decision Making
Every scenario shows:
- **What the system detected** (Input)
- **What it decided to do** (Decision)
- **Why it made that choice** (Reason)
- **How safety was ensured** (Safety validation)

### 2. Safety First
- All actions go through safety validation
- Constraints are explicit and verifiable
- No action executes without approval

### 3. Self-Restraint
- **Scenario 3 (False Alarm)**: Shows the agent refusing to act on benign anomalies
- **Scenario 4 (Onboarding)**: Shows the agent enforcing observation periods
- Both demonstrate knowing when NOT to act

### 4. Explainability
- Every decision includes detailed reasoning
- No black-box decisions
- Audit trail for compliance

---

## Testing on Live Demo

### Quick Test Script

```bash
#!/bin/bash
BASE_URL="https://multi-intelligent-agent.onrender.com"

echo "Testing Demo Scenarios..."
echo "========================="

echo "\n1. Crash Recovery"
curl -X POST $BASE_URL/api/demo/crash | jq '.flow'

echo "\n2. Overload Handling"
curl -X POST $BASE_URL/api/demo/overload | jq '.flow'

echo "\n3. False Alarm"
curl -X POST $BASE_URL/api/demo/false-alarm | jq '.flow'

echo "\n4. App Onboarding"
curl -X POST $BASE_URL/api/demo/onboarding \
  -H "Content-Type: application/json" \
  -d '{"text": "My new microservice"}' | jq '.flow'

echo "\nAll scenarios tested!"
```

---

## Response Format

All scenarios return responses in this format:

```json
{
  "scenario": "SCENARIO_NAME",
  "timestamp": "ISO-8601 timestamp",
  "flow": {
    "1_input": { /* Input data */ },
    "2_decision": {
      "action": "action_name",
      "action_index": 0,
      "source": "rl_decision_layer"
    },
    "3_reason": "Detailed explanation of why this decision was made",
    "4_safety": {
      "validation": "PASSED/FAILED",
      "safe_to_execute": true/false,
      "reason": "Safety validation explanation",
      "constraints": ["List", "of", "constraints"]
    }
  },
  "proof": {
    "state": { /* Agent state at decision time */ },
    "execution_result": { /* Result of action execution */ }
  }
}
```

---

## Demo Scenarios Summary

| Scenario | Endpoint | Action | Key Learning |
|----------|----------|--------|--------------|
| **Crash** | `/api/demo/crash` | RESTART | Auto-recovery from failures |
| **Overload** | `/api/demo/overload` | SCALE_UP | Resource-based scaling |
| **False Alarm** | `/api/demo/false-alarm` | NOOP | Self-restraint, avoiding overreaction |
| **Onboarding** | `/api/demo/onboarding` | NOOP | Safety policies for new apps |

---

## Next Steps

1. **Try the scenarios** using the curl commands above
2. **Review the responses** to understand the decision flow
3. **Check the README** for more system details: [README.md](README.md)
4. **Read the documentation**: [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md)

## Questions?

- Check [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md) for detailed usage
- Review [README.md](README.md) for system capabilities
- See [implementation_plan.md](implementation_plan.md) for technical details
