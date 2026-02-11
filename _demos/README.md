# Demo Scripts

This directory contains all demonstration scripts for the Multi-Agent CI/CD System.

## Main Demo

### `demo_run.py` - Full System Demo
**Purpose:** Complete end-to-end demonstration of the autonomous agent system.

**Usage:**
```bash
python _demos/demo_run.py
```

**What it demonstrates:**
- Application onboarding with validation
- Runtime event emission
- Failure scenarios (crash, overload, false alarm)
- RL-based decision making
- Automated recovery execution
- Proof logging

**Expected output:** Complete demo flow with 18+ proof events logged.

---

## Capability Demos

### `demo_agent_autonomous.py` - Autonomous Agent
**Purpose:** Demonstrates the agent's autonomous loop and decision-making.

**Usage:**
```bash
python _demos/demo_agent_autonomous.py
```

### `demo_action_governance.py` - Action Governance
**Purpose:** Shows safety validation and action governance rules.

**Usage:**
```bash
python _demos/demo_action_governance.py
```

### `demo_self_restraint.py` - Self-Restraint
**Purpose:** Demonstrates when the agent refuses to act (uncertainty, conflicts).

**Usage:**
```bash
python _demos/demo_self_restraint.py
```

### `demo_memory_influence.py` - Memory Influence
**Purpose:** Shows how memory affects decision-making and creates overrides.

**Usage:**
```bash
python _demos/demo_memory_influence.py
```

### `demo_perception_memory.py` - Perception & Memory
**Purpose:** Demonstrates perception sources and memory integration.

**Usage:**
```bash
python _demos/demo_perception_memory.py
```

---

## Integration Demos

### `demo_file_onboarding.py` - File-Based Onboarding
**Purpose:** Shows file-based application onboarding flow.

**Usage:**
```bash
python _demos/demo_file_onboarding.py
```

### `demo_rl_integration.py` - RL Integration
**Purpose:** Demonstrates RL decision layer integration with Ritesh's API.

**Usage:**
```bash
python _demos/demo_rl_integration.py
```

### `demo_text_input_onboarding.py` - Text Input Onboarding
**Purpose:** Shows text-based application onboarding.

**Usage:**
```bash
python _demos/demo_text_input_onboarding.py
```

---

## Verification Scripts

### `verify_action_governance.py`
**Purpose:** Validates action governance safety rules.

### `verify_agent_core.py`
**Purpose:** Verifies core agent functionality.

### `verify_endpoints.py`
**Purpose:** Tests API endpoint functionality.

---

## Utilities

### `demo_utils.py`
Shared utility functions for all demo scripts.

---

## Quick Start

**First-time users:** Start with the main demo:
```bash
python _demos/demo_run.py
```

**For specific capabilities:** Run individual capability demos to see focused demonstrations.

**For verification:** Run verification scripts to validate system integrity.

---

## Demo Mode Configuration

All demos run in **DEMO_MODE** with:
- ✅ Deterministic RL decisions
- ✅ Action allowlists enforced
- ✅ Stage environment safety
- ✅ Comprehensive proof logging

See `demo_mode_config.py` for configuration details.
