# Integration API Guide

This document shows how to integrate with Shivam's Orchestrator.

## For External Consumers (Python)

```python
import requests

# Base URL of deployed orchestrator
BASE_URL = "http://your-orchestrator-url.com"

# Step 1: Get runtime data from Shivam
def get_runtime_data():
    """Get current runtime event payload."""
    response = requests.get(f"{BASE_URL}/api/runtime/latest")
    return response.json()

# Step 2: Process payload through agent
def process_runtime_payload(payload):
    """Send runtime payload to agent for decision."""
    response = requests.post(
        f"{BASE_URL}/api/agent/process",
        json=payload
    )
    result = response.json()
    return result['decision'], result['status']

# Step 3: Execute action
def execute_action(decision):
    """Execute the decided action."""
    response = requests.post(
        f"{BASE_URL}/api/action/execute",
        json=decision
    )
    return response.json()

# Full flow example
if __name__ == "__main__":
    # Get payload
    payload = get_runtime_data()
    print(f"Runtime payload: {payload}")
    
    # Process through agent
    decision, status = process_runtime_payload(payload)
    print(f"Decision: {decision}, Status: {status}")
    
    # Execute
    result = execute_action(decision)
    print(f"Execution result: {result}")
```

## API Endpoints You Need to Provide

Your orchestrator needs these 3 endpoints:

### 1. GET `/api/runtime/latest`
**Purpose**: Get latest runtime event data

**Response**:
```json
{
  "app_id": "app-123",
  "event_type": "crash",
  "exit_code": 1,
  "timestamp": "2026-02-05T20:00:00Z",
  "environment": "dev"
}
```

### 2. POST `/api/agent/process`
**Purpose**: Process runtime payload through agent

**Request**:
```json
{
  "app_id": "app-123",
  "event_type": "crash",
  "exit_code": 1
}
```

**Response**:
```json
{
  "decision": {
    "action": "restart",
    "confidence": 0.95,
    "reasoning": "App crashed, restart recommended"
  },
  "status": "validated"
}
```

### 3. POST `/api/action/execute`
**Purpose**: Execute decided action

**Request**:
```json
{
  "action": "restart",
  "app_id": "app-123",
  "confidence": 0.95
}
```

**Response**:
```json
{
  "success": true,
  "action": "restart",
  "timestamp": "2026-02-05T20:00:05Z",
  "result": "Service restarted successfully"
}
```

---

## Quick Setup for External Users

### Installation
```bash
pip install requests
```

### Usage
```python
from integration_client import get_runtime_data, process_runtime_payload, execute_action

# Full flow
payload = get_runtime_data()
decision, status = process_runtime_payload(payload)
result = execute_action(decision)
```

---

## What You Need to Share

Send them:
1. ✅ This `INTEGRATION_API.md` file
2. ✅ Your deployed URL (e.g., `https://shivam-orchestrator.vercel.app`)
3. ✅ Sample payload format (shown above)
