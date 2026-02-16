"""Unified Dashboard Component - Embeds RL decisions into main UI"""

import streamlit as st
import json
import os
from datetime import datetime

def render_unified_pipeline():
    """Render the 4-panel unified view: Runtime → RL → Action → Status"""
    
    st.header("🔄 Unified CI/CD Pipeline")
    
    # Create 4 columns for the pipeline stages
    col1, col2, col3, col4 = st.columns(4)
    
    # Panel 1: Runtime State
    with col1:
        st.subheader("📊 Runtime State")
        runtime_data = load_latest_runtime()
        if runtime_data:
            st.metric("App", runtime_data.get("app", "N/A"))
            st.metric("State", runtime_data.get("state", "N/A"))
            st.metric("Latency", f"{runtime_data.get('latency_ms', 0)}ms")
            st.metric("Errors", runtime_data.get("errors_last_min", 0))
            st.metric("Workers", runtime_data.get("workers", 0))
        else:
            st.info("No runtime data")
    
    # Panel 2: RL Decision
    with col2:
        st.subheader("🧠 RL Decision")
        rl_decision = load_latest_rl_decision()
        if rl_decision:
            action = rl_decision.get("decision_str", "noop")
            confidence = rl_decision.get("confidence", 0)
            st.metric("Action", action)
            st.metric("Confidence", f"{confidence:.2f}")
            st.caption(f"Timestamp: {rl_decision.get('timestamp', 'N/A')}")
        else:
            st.info("No RL decision")
    
    # Panel 3: Action Executed
    with col3:
        st.subheader("⚡ Action Executed")
        action_result = load_latest_action()
        if action_result:
            st.metric("Status", action_result.get("status", "N/A"))
            st.metric("Action", action_result.get("action", "N/A"))
            st.caption(f"Executed: {action_result.get('timestamp', 'N/A')}")
        else:
            st.info("No action executed")
    
    # Panel 4: Environment Status
    with col4:
        st.subheader("🌍 Environment")
        env_status = get_environment_status()
        st.metric("Environment", env_status["env"])
        st.metric("Health", env_status["health"])
        st.metric("Uptime", env_status["uptime"])


def load_latest_runtime():
    """Load latest runtime event from proof log"""
    proof_log = "logs/day1_proof.log"
    if not os.path.exists(proof_log):
        return None
    
    try:
        with open(proof_log, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                entry = json.loads(line)
                if entry.get("event_name") == "RUNTIME_EMIT":
                    return entry.get("payload", {})
    except:
        pass
    return None


def load_latest_rl_decision():
    """Load latest RL decision from proof log"""
    proof_log = "logs/day1_proof.log"
    if not os.path.exists(proof_log):
        return None
    
    try:
        with open(proof_log, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                entry = json.loads(line)
                if entry.get("event_name") == "RL_DECISION":
                    return entry
    except:
        pass
    return None


def load_latest_action():
    """Load latest orchestrator action from proof log"""
    proof_log = "logs/day1_proof.log"
    if not os.path.exists(proof_log):
        return None
    
    try:
        with open(proof_log, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                entry = json.loads(line)
                if entry.get("event_name") == "ORCH_EXEC":
                    return entry
    except:
        pass
    return None


def get_environment_status():
    """Get current environment status"""
    # Default values
    status = {
        "env": "stage",
        "health": "🟢 Healthy",
        "uptime": "99.5%"
    }
    
    # Try to load from uptime log
    uptime_log = "logs/uptime_log.csv"
    if os.path.exists(uptime_log):
        try:
            import pandas as pd
            df = pd.read_csv(uptime_log)
            if not df.empty:
                up_count = (df['status'] == 'UP').sum()
                uptime_pct = up_count / len(df) * 100
                status["uptime"] = f"{uptime_pct:.1f}%"
                status["health"] = "🟢 Healthy" if uptime_pct > 95 else "🟡 Degraded"
        except:
            pass
    
    return status
