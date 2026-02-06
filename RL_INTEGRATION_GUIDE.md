# RL Integration Final Lock - Quick Start Guide

## Overview

This system integrates with Ritesh's demo-frozen RL API to make all autonomous decisions. Zero local decision logic duplication.

## API Endpoints

Ritesh's RL API provides these endpoints:

- **POST** `http://localhost:5000/api/decision` - Get RL decision for runtime state
- **GET** `http://localhost:5000/api/status` - Health check
- **GET** `http://localhost:5000/api/demo/scenarios` - Demo scenarios

---

## Quick Start

### 1. Prerequisites

Ensure Ritesh's RL API is running:

```bash
# Check if API is accessible
curl http://localhost:5000/api/status
```

Expected response:
```json
{
  "status": "healthy",
  "api_version": "demo-frozen",
  "uptime": "..."
}
```

### 2. Configuration

Verify `.env` configuration:

```env
# RL API Integration
USE_EXTERNAL_RL_API=true                    # Enable external API
RL_API_BASE_URL=http://localhost:5000       # API base URL
RL_API_TIMEOUT=5                            # Timeout in seconds
RL_API_MAX_RETRIES=3                        # Retry attempts
RL_API_RETRY_DELAY=0.5                      # Retry delay
```

### 3. Run Demo

```bash
python demo_rl_integration.py
```

This will:
- ✅ Verify API configuration
- ✅ Test valid event processing
- ✅ Test invalid event handling (NOOP fallback)
- ✅ Verify proof logging
- ✅ Show integration summary

### 4. Run Tests

```bash
python testing/test_external_rl_integration.py
```

This runs comprehensive integration tests covering:
- Response validation
- Safety enforcement
- Error handling
- Proof logging

### 5. Monitor Proof Logs

```bash
# Watch real-time decision logging
tail -f runtime_rl_proof.log
```

---

## Usage Example

```python
from core.runtime_rl_pipe import get_rl_pipe

# Get RL pipe instance
rl_pipe = get_rl_pipe(env='dev')

# Send runtime event
event = {
    'event_type': 'latency_spike',
    'app_name': 'demo-app',
    'latency_ms': 3500,
    'timestamp': '2026-02-06T10:00:00'
}

# Process through RL integration
result = rl_pipe.pipe_runtime_event(event)

print(f"RL Action: {result['rl_action']}")
print(f"Execution: {result['execution']}")
print(f"Validation: {result['validation']}")
```

---

## Safety Guarantees

### 1. Unsafe RL Output → NOOP

```python
# API returns unsafe action (e.g., ROLLBACK in dev environment)
api_response = {'action': 4}  # ROLLBACK

# Validator refuses unsafe action
safe_action, metadata = validate_rl_response(api_response, env='dev')

# Result: safe_action = 0 (NOOP)
# Logged: RL_UNSAFE_REFUSED event
```

### 2. Missing Runtime → NOOP

```python
# Invalid event (missing required fields)
invalid_event = {'incomplete': 'data'}

# Pipeline validates input
result = rl_pipe.pipe_runtime_event(invalid_event)

# Result: rl_action = 0 (NOOP)
# Result: validation_error = "Missing required fields"
```

### 3. API Error → NOOP

```python
# API is unreachable or times out
# Client automatically retries with exponential backoff
# After 3 failed attempts, returns NOOP

# Result: action = 0 (NOOP)
# Logged: RL_API_ERROR event
```

---

## Proof Logging

Every decision creates a human-readable proof trail:

```
================================================================================
RL DECISION PROOF TRAIL
================================================================================
Timestamp: 2026-02-06T10:00:00
Environment: dev

INPUT STATE:
  Event Type: latency_spike
  App Name: demo-app

RL API RESPONSE:
  Action: 1 (RESTART)
  Response: {...}

VALIDATION: PASSED
SAFETY CHECK: SAFE
FINAL ACTION EXECUTED: 1 (RESTART)

DECISION FLOW: RL decision received -> validated -> executed
================================================================================
```

---

## Troubleshooting

### API Not Responding

**Issue:** `RL_API_ERROR` in logs, all actions are NOOP

**Solution:**
1. Check if Ritesh's API is running: `curl http://localhost:5000/api/status`
2. Verify `RL_API_BASE_URL` in `.env`
3. Check network connectivity
4. Review `runtime_rl_proof.log` for error details

### All Actions are NOOP

**Issue:** Valid events result in NOOP execution

**Solution:**
1. Check if `USE_EXTERNAL_RL_API=true` in `.env`
2. Verify API is returning valid response structure
3. Check environment safety rules (prod only allows NOOP)
4. Review `runtime_rl_proof.log` for validation failures

### Validation Failures

**Issue:** `RL_VALIDATION_FAILED` events in logs

**Solution:**
1. Verify API response contains `action` field
2. Ensure action is integer in range [0-4]
3. Check if action is allowed for environment (dev/stage/prod)
4. Review API response structure in proof logs

---

## Feature Flag: Local Fallback

To temporarily use local RL (for testing without API):

```env
USE_EXTERNAL_RL_API=false
```

This enables backwards compatibility during transition.

---

## Architecture

```
Runtime Event
     ↓
Input Validation
     ↓
External RL API Call ← [Ritesh's API]
     ↓
Response Validation
     ↓
Safety Check
     ↓
Execute/Refuse → NOOP fallback
     ↓
Proof Logging → runtime_rl_proof.log
```

---

## Key Files

| File | Purpose |
|------|---------|
| [external_rl_client.py](core/external_rl_client.py) | External API client with retry logic |
| [rl_response_validator.py](core/rl_response_validator.py) | Safety validation layer |
| [runtime_rl_pipe.py](core/runtime_rl_pipe.py) | Main integration pipeline |
| [proof_logger.py](core/proof_logger.py) | Proof logging with decision trail |
| [demo_rl_integration.py](demo_rl_integration.py) | Demo script |
| [test_external_rl_integration.py](testing/test_external_rl_integration.py) | Integration tests |

---

## Summary

✅ **Zero local decision logic** - All from external API  
✅ **Production safety** - Multi-layer validation  
✅ **Automatic NOOP fallback** - On any error  
✅ **Complete proof trail** - Human-readable logs  
✅ **Feature flag** - Gradual rollout support  

**Status:** ✅ Ready for production deployment
