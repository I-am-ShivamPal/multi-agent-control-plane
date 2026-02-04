# Demo Walkthrough - Terminal-Free Agent Demo

## Live Demo URL

**Dashboard**: https://multi-agent-dashboard.onrender.com
**API**: https://multi-agent-api.onrender.com

## Prerequisites

None! All demos run through the web interface or API calls. No terminal access required.

---

## Walkthrough Steps

### 1. View Agent Status

**Web Dashboard**:
1. Navigate to the live dashboard URL
2. View "Live Agent Status" section showing:
   - Current agent state
   - Demo mode indicator
   - Freeze mode status
   - Uptime
   - Last decision with explanation

**API**:
```bash
curl https://multi-agent-api.onrender.com/api/agent/status
```

**Expected Response**:
```json
{
  "agent_id": "agent-demo-001",
  "state": "idle",
  "uptime_seconds": 3600,
  "last_decision": {
    "action": "restart",
    "confidence": 0.95,
    "timestamp": "2026-02-04T18:20:00Z",
    "explanation": "Crash detected → restart recommended"
  },
  "demo_mode": true,
  "freeze_mode": true
}
```

---

### 2. App Onboarding (Text-Based)

**Web Dashboard**:
1. Click "📝 Onboard App" button
2. Fill in form:
   - App Name: `my-new-api`
   - Repository URL: `https://github.com/username/my-new-api`
   - Runtime: `nodejs`
3. Click Submit
4. Watch agent process onboarding
5. View confirmation and spec file path

**API**:
```bash
curl -X POST https://multi-agent-api.onrender.com/api/agent/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my-new-api",
    "repo_url": "https://github.com/username/my-new-api",
    "runtime": "nodejs"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "App my-new-api onboarded successfully",
  "spec_file": "apps/registry/my-new-api.json",
  "timestamp": "2026-02-04T18:21:00Z"
}
```

**Verification**:
- Check agent status - last decision shows onboarding
- Spec file created in `apps/registry/`
- Proof log contains `ONBOARDING_VALIDATION_PASSED`

---

### 3. Crash Recovery Demo

**Web Dashboard**:
1. Click "💥 Trigger Crash" button
2. Watch agent:
   - Detect crash scenario
   - Decide on restart action
   - Execute recovery
3. View decision explanation in real-time

**API**:
```bash
curl -X POST https://multi-agent-api.onrender.com/api/demo/crash
```

**Expected Response**:
```json
{
  "status": "success",
  "scenario": "crash_recovery",
  "decision": "restart",
  "confidence": 0.95,
  "explanation": "Crash detected in demo-api (exit code 1) → RL decided to restart service → Success",
  "result": {
    "action_executed": "restart",
    "success": true,
    "details": "Service demo-api restarted successfully"
  },
  "timestamp": "2026-02-04T18:22:00Z"
}
```

**What Happened**:
1. Simulated crash in `demo-api` (exit code 1)
2. RL decision layer analyzed failure type
3. Recommended `restart` action with 95% confidence
4. Orchestrator executed restart through governance gates
5. System stabilized

**Verification**:
- Proof log contains `RL_DECISION` with action=restart
- Proof log contains `ORCH_EXEC` confirming execution
- Proof log contains `SYSTEM_STABLE`

---

### 4. Overload Handling Demo

**Web Dashboard**:
1. Click "📈 Trigger Overload" button
2. Watch agent:
   - Detect high CPU/memory usage
   - Decide on scaling action
   - Execute horizontal scaling
3. View decision explanation

**API**:
```bash
curl -X POST https://multi-agent-api.onrender.com/api/demo/overload
```

**Expected Response**:
```json
{
  "status": "success",
  "scenario": "overload_handling",
  "decision": "scale_up",
  "confidence": 0.92,
  "explanation": "High CPU (85%) detected in demo-api → RL decided to scale up → Success",
  "result": {
    "action_executed": "scale_up",
    "success": true,
    "replicas_before": 1,
    "replicas_after": 2,
    "details": "Scaled demo-api from 1 to 2 replicas"
  },
  "timestamp": "2026-02-04T18:23:00Z"
}
```

**What Happened**:
1. Simulated high CPU (85%) and memory (75%)
2. RL decision layer detected resource pressure
3. Recommended `scale_up` action with 92% confidence
4. Orchestrator added replica
5. System load distributed

**Verification**:
- Proof log contains `RL_DECISION` with action=scale_up
- Proof log contains `ORCH_EXEC` with replica count
- Agent status shows updated decision

---

### 5. View Proof Logs

**API**:
```bash
# Get last 20 proof log entries
curl https://multi-agent-api.onrender.com/api/logs/proof?limit=20
```

**Expected Response**:
```json
{
  "logs": [
    {
      "event_name": "RL_DECISION",
      "timestamp": "2026-02-04T18:22:00Z",
      "action": "restart",
      "confidence": 0.95
    },
    {
      "event_name": "ORCH_EXEC",
      "timestamp": "2026-02-04T18:22:01Z",
      "action": "restart",
      "status": "executed"
    },
    {
      "event_name": "SYSTEM_STABLE",
      "timestamp": "2026-02-04T18:22:02Z",
      "recovery_action": "restart"
    }
  ],
  "count": 20,
  "total_available": 156
}
```

---

### 6. List Available Scenarios

**API**:
```bash
curl https://multi-agent-api.onrender.com/api/demo/scenarios
```

**Expected Response**:
```json
{
  "scenarios": [
    {
      "id": "crash",
      "name": "Crash Recovery",
      "description": "Demonstrates autonomous crash detection and service restart",
      "endpoint": "/api/demo/crash",
      "method": "POST"
    },
    {
      "id": "overload",
      "name": "Overload Handling",
      "description": "Demonstrates autonomous scaling based on resource usage",
      "endpoint": "/api/demo/overload",
      "method": "POST"
    },
    {
      "id": "onboard",
      "name": "App Onboarding",
      "description": "Demonstrates text-based application onboarding",
      "endpoint": "/api/agent/onboard",
      "method": "POST",
      "required_fields": ["app_name", "repo_url", "runtime"]
    }
  ]
}
```

---

## Demo Script (5-7 Minutes)

**Minute 0-1: Introduction**
- "This is an autonomous CI/CD agent with self-governance"
- Show agent status - running, demo mode, freeze mode
- Explain: "Freeze mode means deterministic decisions, no learning drift"

**Minute 1-2: App Onboarding**
- "Let's onboard a new application without touching terminal"
- Fill form: my-demo-app, github URL, nodejs
- Submit → watch agent process
- "Agent validated input, generated spec, triggered deployment"

**Minute 2-4: Crash Recovery**
- "Now let's see autonomous failure recovery"
- Click crash button
- "Application crashed → Agent detected it"
- "RL decided to restart → Orchestrator executed"
- "System stabilized → All logged to proof log"

**Minute 4-6: Overload Handling**
- "What happens when load increases?"
- Click overload button
- "High CPU detected → Agent analyzed"
- "RL decided to scale up → Added replica"
- "Load distributed → System healthy"

**Minute 6-7: Governance & Safety**
- "Agent has self-restraint rules"
- Show governance documentation
- "Cooldowns prevent rapid actions"
- "Repetition limits prevent loops"
- "All decisions logged and explained"

---

## Key Talking Points

1. **Autonomous** - Agent runs continuously, no manual intervention
2. **Self-Governing** - Blocks itself when needed (cooldowns, repetition)
3. **Explainable** - Every decision logged with explanation
4. **Safe** - Demo freeze prevents drift, governance prevents bad actions
5. **Terminal-Free** - All demos work through web interface

---

## Troubleshooting

**Issue**: API not responding
- **Solution**: Check live URL is correct, verify Render deployment status

**Issue**: Demo not triggering
- **Solution**: Check demo mode is enabled, verify endpoint URL

**Issue**: Agent status shows old data
- **Solution**: Refresh page, check API health endpoint

**Issue**: Onboarding fails
- **Solution**: Verify all required fields provided, check validation rules
