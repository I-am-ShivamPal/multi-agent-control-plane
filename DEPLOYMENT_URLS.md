# Multi-Agent Control Plane - Deployment URLs

## Live Deployment (Render)
- **Dashboard:** https://multi-agent-control-plane.onrender.com
- **API Docs:** https://multi-agent-control-plane.onrender.com/api
- **Health Check:** https://multi-agent-control-plane.onrender.com/api/health

## Local Development
- **Dashboard:** http://localhost:5000
- **API Docs:** http://localhost:5000/api
- **Health Check:** http://localhost:5000/api/health

## Running Locally

### Start Backend (Flask API)
```bash
python wsgi.py
```

### Start Dashboard (Streamlit - Alternative)
```bash
python -m streamlit run ui/dashboards/dashboard.py
```

## API Endpoints

### Agent Status
```bash
GET /api/agent/status
```

### Demo Scenarios
```bash
POST /api/demo/crash
POST /api/demo/overload
POST /api/demo/healthy
```

### Onboard Application
```bash
POST /api/agent/onboard
Body: {
  "app_name": "my-app",
  "repo_url": "https://github.com/user/repo",
  "runtime": "backend"
}
```

## Configuration

The dashboard automatically detects the environment:
- **Production:** Uses `https://multi-agent-control-plane.onrender.com`
- **Local:** Uses `http://localhost:5000`

To manually configure, edit `static/config.js`
