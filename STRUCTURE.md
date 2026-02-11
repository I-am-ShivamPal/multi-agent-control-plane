# Repository Structure

## Overview
This repository contains a multi-agent CI/CD system with autonomous operation, reinforcement learning optimization, and comprehensive safety controls.

## Core System

### `/agents` - Agent Implementations
Multi-agent system components for deployment, monitoring, and orchestration.

### `/core` - Core System Logic
- `/rl` - Reinforcement learning decision engine
  - `/external_api` - Ritesh's RL API integration (demo-frozen)
- `action_governance.py` - Action safety validation
- `memory_*.py` - Agent memory management
- `perception_*.py` - Environment perception
- `rl_orchestrator_safe.py` - RL intake gate

### `/orchestrator` - Orchestration Layer
Application orchestration, deployment, and lifecycle management.

## Entry Points

- `agent_runtime.py` - **PRIMARY** entry point (autonomous agent mode)
- `main.py` - Legacy entry point (script mode, deprecated)

See [ENTRY_POINT.md](ENTRY_POINT.md) for detailed usage.

## Demos & Testing

### `/_demos` - Demo Scripts
All demonstration scripts consolidated here:
- `demo_run.py` - Full system demo
- `demo_action_governance.py` - Action governance demo
- `demo_agent_autonomous.py` - Autonomous agent demo
- `demo_file_onboarding.py` - File-based onboarding demo
- `demo_memory_influence.py` - Memory influence demo
- `demo_perception_memory.py` - Perception and memory demo
- `demo_self_restraint.py` - Self-restraint demo
- Additional verification scripts

### `/testing` - Test Suites
Integration and system tests.

### `/tests` - Unit Tests
Component-level unit tests.

## User Interface

### `/ui` - Unified UI Directory
- `/dashboards` - Streamlit dashboards
  - `dashboard.py` - Main dashboard
  - `observability_dashboard.py` - Observability view
  - `app_dashboard.py` - Application status
  - Additional specialized dashboards
- `/web` - Web interfaces
- `/devops` - DevOps control panels

## Configuration & Data

### `/apps` - Application Registry
Application specifications and configuration files.

### `/data` - Runtime Data
Logs, metrics, and runtime state data.

### `/dataset` - Sample Datasets
Sample data for testing and demos.

### `/environments` - Environment Configs
Environment-specific configuration (dev/stage/prod).

## Supporting Components

### `/api` - API Layer
REST API for external integrations.

### `/integration` - Integration Adapters
External system integration points.

### `/monitoring` - Monitoring Tools
System health monitoring and alerting.

### `/security` - Security Components
Authentication, validation, and security utilities.

### `/scripts` - Utility Scripts
Helper scripts for setup and maintenance.

## Key Files

- `README.md` - Main documentation
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker orchestration
- `Dockerfile` - Container definition
- `.env.example` - Environment variable template

## Directory Tree (Simplified)

```
Multi-Intelligent-agent-system-main/
├── agent_runtime.py          # PRIMARY ENTRY POINT
├── main.py                   # Legacy entry point
├── onboarding_entry.py       # Application onboarding
├── deploy.py                 # Deployment script
├── _demos/                   # All demo scripts
├── agents/                   # Agent implementations
├── core/                     # Core logic
│   └── rl/                   # RL engine
│       └── external_api/     # Ritesh's RL API
├── orchestrator/             # Orchestration layer
├── ui/                       # Unified UI
│   ├── dashboards/          # Streamlit dashboards
│   ├── web/                 # Web interfaces
│   └── devops/              # DevOps panels
├── api/                      # API layer
├── integration/              # Integration adapters
├── monitoring/               # Monitoring tools
├── security/                 # Security components
├── testing/                  # Test suites
├── tests/                    # Unit tests
├── apps/                     # Application registry
├── data/                     # Runtime data
├── environments/             # Environment configs
└── scripts/                  # Utility scripts
```

## Integration Points

### Shivam's Orchestrator
Main system orchestration, agent runtime, and safety validation.

### Ritesh's RL API
Located in `core/rl/external_api/`, provides demo-frozen reinforcement learning decision engine.

## Migration Notes

**Recent Changes (2026-02-11):**
- ✅ Removed nested `Multi-intelligent-agent/` subfolder duplication
- ✅ Consolidated all demos into `_demos/` directory
- ✅ Integrated Ritesh's RL API into `core/rl/external_api/`
- ✅ Reorganized UI components into unified `ui/` directory
- ✅ Established clear entry point hierarchy

**Backup:** Pre-consolidation state saved in Git commit `7eaafad`
