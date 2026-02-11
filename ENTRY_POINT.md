# System Entry Points

## Primary Entry Point (Recommended)

### `agent_runtime.py` - Autonomous Agent Mode
The main entry point for running the system as an autonomous agent.

**Usage:**
```bash
python agent_runtime.py --env dev
python agent_runtime.py --env stage
python agent_runtime.py --env prod
```

**Features:**
- Continuous autonomous operation
- Real-time monitoring and decision-making
- Reinforcement learning integration
- Full agent state tracking

## Legacy Entry Point

### `main.py` - Script Mode (Deprecated)
Legacy entry point maintained for backward compatibility.

**Usage:**
```bash
python main.py --dataset dataset/student.csv --planner rl
```

**Note:** This entry point runs a single execution and exits. Use `agent_runtime.py` for production deployments.

## Demo Entry Point

### `_demos/demo_run.py` - Full System Demo
Run complete system demonstration with autonomous agent capabilities.

**Usage:**
```bash
python _demos/demo_run.py
```

**What it demonstrates:**
- Application onboarding
- Runtime event handling
- Failure detection and recovery
- RL-based decision making
- Safety validation

## Quick Start

For first-time users:

1. **Run the demo:**
   ```bash
   python _demos/demo_run.py
   ```

2. **Start the agent:**
   ```bash
   python agent_runtime.py --env stage
   ```

3. **Launch dashboards:**
   ```bash
   streamlit run ui/dashboards/dashboard.py
   ```

## Additional Tools

- **Onboarding:** `onboarding_entry.py`
- **Deployment:** `deploy.py`
- **Monitoring:** `monitoring/` directory
- **Testing:** `testing/` directory
