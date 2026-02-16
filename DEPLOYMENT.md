# Deployment Guide - Render Hosting

## Single Repo Deployment

This repository deploys as a single service on Render.

## Files Required

- `app.py` - Flask API server
- `middleware.py` - Transport layer
- `runtime_payload_schema.json` - Contract schema
- `requirements-deploy.txt` - Python dependencies
- `Procfile` - Gunicorn configuration

## Environment Variables

Configure in Render dashboard:

```bash
ENVIRONMENT=stage          # Options: dev, stage, prod
RL_ENDPOINT=<RL_URL>      # URL to Ritesh's RL service
PORT=5000                  # Auto-set by Render
```

## Render Setup

1. **Create Web Service**
   - Connect GitHub repo
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: Uses `Procfile` automatically

2. **Set Environment Variables**
   - `ENVIRONMENT=stage` (for demo)
   - `RL_ENDPOINT=<ritesh-rl-url>` (if separate service)

3. **Health Check**
   - Path: `/health`
   - Expected: `{"status": "healthy"}`

## Endpoints

### Health Check
```bash
GET /health
Response: {"status": "healthy", "environment": "stage"}
```

### Process Runtime Event
```bash
POST /api/runtime/process
Body: {
  "app": "demo-api",
  "env": "stage",
  "state": "crashed",
  "latency_ms": 250,
  "errors_last_min": 5,
  "workers": 2
}
Response: {"decision": {...}, "status": "success"}
```

### Demo Cycle
```bash
POST /api/demo/cycle
Response: {
  "cycle": "complete",
  "input": {...},
  "output": {...},
  "environment": "stage"
}
```

## Behavior Modes

### Stage (Deterministic)
- `ENVIRONMENT=stage`
- Predictable RL decisions
- Demo-safe operations
- Allowlist enforcement

### Prod (Freeze)
- `ENVIRONMENT=prod`
- Safety guards active
- Only `noop` allowed
- No destructive actions

## Testing Locally

```bash
# Install dependencies
pip install -r requirements-deploy.txt

# Set environment
export ENVIRONMENT=stage
export RL_ENDPOINT=http://localhost:5001/decide

# Run server
python app.py

# Test health
curl http://localhost:5000/health

# Test demo cycle
curl -X POST http://localhost:5000/api/demo/cycle
```

## Dual Service Setup (Optional)

If RL layer is separate service:

**Service 1: Runtime + Middleware** (this repo)
- Handles runtime events
- Validates payloads
- Calls RL endpoint

**Service 2: RL Decision Layer** (Ritesh's repo)
- Receives validated payloads
- Returns decisions
- Endpoint: `/decide`

Set `RL_ENDPOINT` to Service 2 URL.

## Verification

After deployment:

1. **Health Check**: `curl https://your-app.onrender.com/health`
2. **Demo Cycle**: `curl -X POST https://your-app.onrender.com/api/demo/cycle`
3. **Verify deterministic behavior in stage**
4. **Verify freeze behavior in prod** (set `ENVIRONMENT=prod`)
