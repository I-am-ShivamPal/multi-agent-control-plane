# Multi-Intelligent Agent System - Complete Working

## 🎯 Project Overview

An **autonomous CI/CD system** powered by Reinforcement Learning (RL) that monitors applications, detects issues, and takes corrective actions without human intervention.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│  Dashboard (HTML) → https://multi-agent-control-plane.onrender.com │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    FLASK API SERVER                          │
│  api/agent_api.py → Exposes REST endpoints                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   AGENT RUNTIME (Core)                       │
│  agent_runtime.py → Autonomous decision loop                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. PERCEPTION → Monitors system health                │  │
│  │ 2. DECISION   → RL Brain decides action               │  │
│  │ 3. ACTION     → Executes (restart/scale/noop)         │  │
│  │ 4. OBSERVATION→ Validates outcome                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  SUPPORTING COMPONENTS                       │
│  • Deploy Agents → Handle deployments                       │
│  • Auto Heal Agent → Restart crashed services               │
│  • Uptime Monitor → Track service health                    │
│  • Metrics Collector → Gather performance data              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow

### 1. **Application Onboarding**
```
User → Dashboard → POST /api/agent/onboard
  ↓
{
  "app_name": "my-app",
  "repo_url": "https://github.com/user/repo",
  "runtime": "backend"
}
  ↓
System creates: apps/registry/my-app.json
  ↓
App is now monitored by agents
```

**File Created:** `apps/registry/my-app.json`
```json
{
  "name": "my-app",
  "type": "backend",
  "repo_path_or_url": "https://github.com/user/repo",
  "environments": ["dev", "stage", "prod"],
  "health_endpoint": "/health",
  "scaling": {
    "min_replicas": 1,
    "max_replicas": 3
  }
}
```

---

### 2. **Continuous Monitoring Loop**

```python
# agent_runtime.py - Runs continuously

while True:
    # STEP 1: PERCEPTION
    events = perception_layer.sense()
    # Detects: crashes, high CPU, memory leaks, slow response
    
    # STEP 2: DECISION (RL Brain)
    decision = rl_brain.decide(events)
    # Returns: restart, scale_up, scale_down, or noop
    
    # STEP 3: SAFETY CHECK
    if demo_mode:
        decision = safety_filter(decision)
    
    # STEP 4: ACTION
    orchestrator.execute(decision)
    # Performs: docker restart, scale workers, etc.
    
    # STEP 5: OBSERVATION
    result = observe_outcome()
    # Validates: Did action fix the issue?
    
    # STEP 6: LOGGING
    log_to_proof_system(decision, result)
    
    sleep(5)  # Check every 5 seconds
```

---

### 3. **Demo Scenario: Crash Recovery**

**User Action:**
```bash
curl -X POST https://multi-agent-control-plane.onrender.com/api/demo/crash
```

**System Flow:**
```
1. API receives crash event
   ↓
2. Agent Runtime processes:
   - Event: "demo-api crashed"
   - Metrics: CPU=0%, Memory=0%
   ↓
3. RL Brain Decision:
   - Analyzes: Service is down
   - Proposes: "restart"
   - Confidence: 95%
   ↓
4. Safety Filter:
   - Checks: Is restart allowed in demo mode?
   - Result: ✅ Approved
   ↓
5. Orchestrator Executes:
   - Runs: docker restart demo-api
   - Logs: Action taken
   ↓
6. Observation:
   - Waits 10s
   - Checks: /health endpoint
   - Result: ✅ Service restored
   ↓
7. Response to User:
   {
     "status": "success",
     "decision": "restart",
     "explanation": "Crash detected → Restart executed → Service restored"
   }
```

---

## 📁 Key Files & Their Roles

### **Core Components**

| File | Purpose |
|------|---------|
| `agent_runtime.py` | Main autonomous agent loop (Perception → Decision → Action) |
| `api/agent_api.py` | REST API server exposing all endpoints |
| `wsgi.py` | Entry point for production deployment |
| `static/dashboard.html` | Web UI for monitoring and testing |

### **Agent Modules**

| File | Purpose |
|------|---------|
| `agents/auto_heal_agent.py` | Detects and restarts crashed services |
| `agents/deploy_agent.py` | Handles application deployments |
| `agents/uptime_monitor.py` | Tracks service availability |
| `agents/issue_detector.py` | Identifies performance issues |

### **Core Logic**

| File | Purpose |
|------|---------|
| `core/rl_decision_layer.py` | RL Brain for decision making |
| `core/prod_safety.py` | Safety filters for production |
| `core/event_bus.py` | Event communication system |
| `core/metrics_collector.py` | Gathers system metrics |

### **Configuration**

| File | Purpose |
|------|---------|
| `demo_mode_config.py` | Demo mode settings (freeze learning) |
| `config.py` | Global configuration |
| `environments/*.env` | Environment-specific settings |

### **Application Registry**

| Directory | Purpose |
|-----------|---------|
| `apps/registry/*.json` | Onboarded application specifications |

---

## 🎮 How to Use

### **1. Access Dashboard**
```
https://multi-agent-control-plane.onrender.com
```

### **2. Test Scenarios**
Click buttons in dashboard:
- **Crash Recovery** → Simulates service crash
- **Overload Handling** → Simulates high CPU
- **Healthy System** → Shows normal operation

### **3. Onboard New App**
Fill form in dashboard:
- App Name: `my-service`
- Repo URL: `https://github.com/user/repo`
- Runtime: `backend`

### **4. Monitor Status**
Dashboard shows:
- Agent State (idle/observing/deciding/acting)
- Success Rate
- Recent Decisions
- System Uptime

---

## 🔧 Local Development

### **Start Backend**
```bash
cd Multi-Intelligent-agent-system-main
python wsgi.py
```
Access: http://localhost:5000

### **Test API**
```bash
# Health check
curl http://localhost:5000/api/health

# Agent status
curl http://localhost:5000/api/agent/status

# Trigger demo
curl -X POST http://localhost:5000/api/demo/crash
```

---

## 🧠 RL Decision Logic

### **Input (Perception)**
```json
{
  "event_type": "high_cpu",
  "environment": "stage",
  "metrics": {
    "cpu_percent": 85,
    "memory_percent": 75,
    "latency_ms": 200
  }
}
```

### **Processing (RL Brain)**
```python
# core/rl_decision_layer.py
def decide(event):
    if event.cpu > 80:
        return "scale_up"
    elif event.cpu < 20 and replicas > 1:
        return "scale_down"
    elif event.crashed:
        return "restart"
    else:
        return "noop"
```

### **Output (Decision)**
```json
{
  "action_name": "scale_up",
  "confidence": 0.92,
  "reason": "CPU usage 85% exceeds threshold"
}
```

---

## 📊 Data Flow

### **Metrics Collection**
```
Services → Metrics Collector → CSV Logs
  ↓
logs/stage/metrics/
  ├── deploy_success_rate.csv
  ├── error_metrics.csv
  ├── latency_metrics.csv
  └── uptime_metrics.csv
```

### **Event Flow**
```
Runtime Event → Event Bus → Agent Runtime → RL Brain → Orchestrator
     ↓              ↓             ↓             ↓            ↓
  Crash         Publish      Perceive      Decide       Execute
  Detected      Event        Event         Action       Action
```

---

## 🛡️ Safety Mechanisms

### **Demo Mode** (`demo_mode_config.py`)
```python
DEMO_MODE = True
FREEZE_MODE = True  # No learning, deterministic

ALLOWED_ACTIONS = ["noop", "restart", "scale_up", "scale_down"]
BLOCKED_ACTIONS = ["delete", "terminate", "modify_prod"]
```

### **Production Safety** (`core/prod_safety.py`)
- Validates all actions before execution
- Prevents destructive operations
- Requires approval for critical changes
- Logs all decisions for audit

---

## 📈 Monitoring & Logs

### **Proof Logs**
```
logs/day1_proof.log
```
Records every decision with:
- Timestamp
- Event detected
- Decision made
- Action taken
- Outcome

### **Performance Logs**
```
logs/stage/performance/
  ├── throughput_log.csv
  └── response_time_log.csv
```

### **Agent Logs**
```
logs/agent/agent_proof.jsonl
```
Detailed agent state transitions

---

## 🚀 Deployment

### **Render (Production)**
- **URL:** https://multi-agent-control-plane.onrender.com
- **Config:** `render.yaml`
- **Entry:** `wsgi.py`
- **Auto-deploy:** On git push to main

### **Environment Variables**
```bash
DEMO_MODE=true
DEMO_FREEZE_MODE=true
SKIP_SIMULATIONS=true
PORT=5000
```

---

## 🎯 Key Features

1. **Autonomous Operation** - No human intervention needed
2. **Self-Healing** - Automatically restarts crashed services
3. **Auto-Scaling** - Scales based on load
4. **Safety-First** - Demo mode prevents destructive actions
5. **Observable** - Full logging and metrics
6. **API-Driven** - REST API for all operations
7. **Web Dashboard** - Visual monitoring interface

---

## 📝 Example: Complete Cycle

```
1. User onboards app "my-api"
   → Creates apps/registry/my-api.json

2. Agent starts monitoring
   → Checks /health every 5s

3. Service crashes
   → Perception detects: status=down

4. RL Brain decides
   → Action: restart

5. Safety validates
   → Approved (restart is safe)

6. Orchestrator executes
   → docker restart my-api

7. Observation confirms
   → Service back online

8. Logs recorded
   → logs/stage/runtime_deploy_log.csv

9. Dashboard updates
   → Shows "restart" action successful
```

---

## 🔗 Quick Links

- **Live Dashboard:** https://multi-agent-control-plane.onrender.com
- **API Docs:** https://multi-agent-control-plane.onrender.com/api
- **GitHub:** https://github.com/I-am-ShivamPal/multi-agent-control-plane
- **Testing Guide:** `API_TESTING_GUIDE.md`
- **Deployment URLs:** `DEPLOYMENT_URLS.md`

---

## 💡 Summary

This is an **autonomous DevOps system** that:
1. Monitors applications continuously
2. Detects issues (crashes, high load, errors)
3. Makes intelligent decisions using RL
4. Takes corrective actions automatically
5. Validates outcomes and learns
6. Provides full observability via dashboard

**No manual intervention required** - the system self-manages!
