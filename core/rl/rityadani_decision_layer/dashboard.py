"""
Advanced Dashboard for RL Decision Layer
Universal DevOps Runtime Intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
import os

# Add current directory to path to import decision module
sys.path.append(os.path.dirname(__file__))
from decision import RLDecisionLayer, ALLOWED_ACTIONS, REQUIRED_SIGNALS, OPTIONAL_SIGNALS

# Initialize RL Layer
rl = RLDecisionLayer()

# Page configuration
st.set_page_config(
    page_title="RL Decision Layer Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_examples():
    """Load examples from JSON file"""
    try:
        with open('examples.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_logs():
    """Load logs from final_logs.txt"""
    try:
        with open('final_logs.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No logs available"

def main():
    # Main header
    st.markdown('<div class="main-header">🧠 RL Decision Layer Dashboard</div>', unsafe_allow_html=True)
    st.markdown("*Universal DevOps Runtime Intelligence - Production Safe Decisions*")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", [
        "Overview",
        "Decision Maker",
        "Environment Scopes",
        "Signal Requirements",
        "Logs & Metrics",
        "Examples"
    ])

    # Load data
    examples = load_examples()
    logs_content = load_logs()

    if page == "Overview":
        show_overview()
    elif page == "Decision Maker":
        show_decision_maker()
    elif page == "Environment Scopes":
        show_environment_scopes()
    elif page == "Signal Requirements":
        show_signal_requirements()
    elif page == "Logs & Metrics":
        show_logs_metrics(logs_content)
    elif page == "Examples":
        show_examples(examples)

def show_overview():
    st.header("📊 System Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Decision Types", len(ALLOWED_ACTIONS))
        st.markdown("Environments configured")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Required Signals", len(REQUIRED_SIGNALS))
        st.markdown("Mandatory for decisions")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Optional Signals", len(OPTIONAL_SIGNALS))
        st.markdown("Enhance decision quality")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # System Status
    st.subheader("🔒 Safety Status")
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("✅ **Production Safe**: Action scope enforcement active")
    st.markdown("✅ **Conservative**: NOOP downgrades for unsafe actions")
    st.markdown("✅ **Honest**: Required signal validation")
    st.markdown("✅ **Deterministic**: No learning, rule-based only")
    st.markdown('</div>', unsafe_allow_html=True)

    # Architecture Diagram
    st.subheader("🏗️ System Architecture")
    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        Runtime_Signals -> RL_Decision_Layer;
        RL_Decision_Layer -> Action_Scope_Enforcement;
        Action_Scope_Enforcement -> Safe_Decision_Output;
        Safe_Decision_Output -> Orchestrator;
        Orchestrator -> Infrastructure;

        Runtime_Signals [shape=box, style=filled, fillcolor=lightblue];
        RL_Decision_Layer [shape=box, style=filled, fillcolor=lightgreen];
        Action_Scope_Enforcement [shape=box, style=filled, fillcolor=yellow];
        Safe_Decision_Output [shape=box, style=filled, fillcolor=lightcoral];
        Orchestrator [shape=box, style=filled, fillcolor=orange];
        Infrastructure [shape=box, style=filled, fillcolor=gray];
    }
    """)

def show_decision_maker():
    st.header("🎯 Interactive Decision Maker")

    st.markdown("Input runtime signals and see the RL decision in real-time.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input Signals")

        # Required signals
        st.markdown("**Required Signals**")
        app = st.text_input("Application", value="web", help="Application name")
        env = st.selectbox("Environment", ["dev", "stage", "prod"], help="Deployment environment")
        state = st.selectbox("State", ["healthy", "warning", "critical"], help="Current system state")

        # Optional signals
        st.markdown("**Optional Signals**")
        latency = st.number_input("Latency (ms)", min_value=0, value=0, help="Response latency in milliseconds")
        errors = st.number_input("Errors Last Minute", min_value=0, value=0, help="Error count in last minute")

        # Build signals dict
        signals = {
            "app": app,
            "env": env,
            "state": state
        }

        if latency > 0:
            signals["latency_ms"] = latency
        if errors > 0:
            signals["errors_last_min"] = errors

        if st.button("Make Decision", type="primary"):
            decision = rl.make_decision(signals)
            st.session_state.last_decision = decision
            st.session_state.last_signals = signals

    with col2:
        st.subheader("Decision Output")

        if 'last_decision' in st.session_state:
            decision = st.session_state.last_decision
            signals = st.session_state.last_signals

            # Display input
            st.markdown("**Input Signals:**")
            st.json(signals)

            st.markdown("---")

            # Display decision
            action = decision['action']
            if action == 'noop':
                st.error(f"🚫 Action: {action.upper()}")
            elif action == 'restart':
                st.warning(f"🔄 Action: {action.upper()}")
            else:
                st.success(f"✅ Action: {action.upper()}")

            st.markdown(f"**Reason:** {decision['reason']}")
            st.markdown(f"**Timestamp:** {decision['timestamp']}")
            st.markdown(f"**Learning Active:** {decision['learning_active']}")

            # Safety indicators
            if decision.get('downgraded', False):
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.markdown("⚠️ **Action was downgraded to NOOP for safety**")
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("Enter signals and click 'Make Decision' to see results")

def show_environment_scopes():
    st.header("🏭 Environment Action Scopes")

    st.markdown("Strict action boundaries enforced per environment:")

    # Create dataframe for display
    data = []
    for env, actions in ALLOWED_ACTIONS.items():
        for action in ['noop', 'scale_up', 'scale_down', 'restart', 'rollback']:
            allowed = "✅" if action in actions else "❌"
            data.append({"Environment": env.upper(), "Action": action.replace('_', ' ').title(), "Allowed": allowed})

    df = pd.DataFrame(data)
    df_pivot = df.pivot(index="Action", columns="Environment", values="Allowed")

    st.table(df_pivot)

    # Visual representation
    st.subheader("Visual Scope Matrix")
    fig = go.Figure(data=go.Heatmap(
        z=[[1 if action in ALLOWED_ACTIONS[env.lower()] else 0 for env in ['DEV', 'STAGE', 'PROD']] for action in ['noop', 'scale_up', 'scale_down', 'restart']],
        x=['DEV', 'STAGE', 'PROD'],
        y=['NOOP', 'SCALE UP', 'SCALE DOWN', 'RESTART'],
        colorscale=['red', 'green'],
        showscale=False
    ))
    fig.update_layout(title="Action Allowances by Environment")
    st.plotly_chart(fig)

def show_signal_requirements():
    st.header("📡 Signal Requirements")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 Required Signals")
        st.markdown("**Must be present for any decision**")
        for signal in REQUIRED_SIGNALS:
            st.markdown(f"- `{signal}`")

        st.markdown("---")
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("**If any required signal is missing:**")
        st.markdown("- RL returns NOOP")
        st.markdown("- Logs 'insufficient runtime truth'")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("🟡 Optional Signals")
        st.markdown("**Enhance decision quality when present**")
        for signal in OPTIONAL_SIGNALS:
            st.markdown(f"- `{signal}`")

        st.markdown("---")
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("**When optional signals are missing:**")
        st.markdown("- Conservative decision making")
        st.markdown("- No aggressive inferences")
        st.markdown('</div>', unsafe_allow_html=True)

def show_logs_metrics(logs_content):
    st.header("📋 Logs & Metrics")

    tab1, tab2 = st.tabs(["📄 Recent Logs", "📊 Metrics"])

    with tab1:
        st.subheader("System Logs")
        if logs_content:
            st.code(logs_content, language="text")
        else:
            st.info("No logs available")

    with tab2:
        st.subheader("Decision Metrics")

        # Parse logs for metrics (simplified)
        log_lines = logs_content.split('\n') if logs_content else []

        downgrade_count = sum(1 for line in log_lines if 'Downgrading unsafe action' in line)
        insufficient_count = sum(1 for line in log_lines if 'insufficient runtime truth' in line)
        reward_disabled_count = sum(1 for line in log_lines if 'Reward computation disabled' in line)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("NOOP Downgrades", downgrade_count)
            st.markdown("*Unsafe actions prevented*")

        with col2:
            st.metric("Insufficient Data", insufficient_count)
            st.markdown("*Conservative fallbacks*")

        with col3:
            st.metric("Learning Disabled", reward_disabled_count)
            st.markdown("*No false learning claims*")

        # Safety Score
        total_decisions = len([line for line in log_lines if 'Test' in line or 'Missing signals' in line])
        safe_decisions = total_decisions - downgrade_count
        safety_score = (safe_decisions / total_decisions * 100) if total_decisions > 0 else 100

        st.markdown("---")
        st.subheader("Safety Score")
        st.progress(safety_score / 100)
        st.markdown(f"**{safety_score:.1f}%** of decisions were inherently safe")

def show_examples(examples):
    st.header("📚 Examples & Test Cases")

    examples = load_examples()

    if examples:
        # Day 2 Examples
        if 'day2_examples' in examples:
            st.subheader("Day 2: Signal Honesty Correction")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Before Correction**")
                before = examples['day2_examples']['before_correction']
                st.json(before)

            with col2:
                st.markdown("**After Correction**")
                after = examples['day2_examples']['after_correction']
                st.json(after)

        # Deterministic Examples
        if 'deterministic_decisions' in examples:
            st.subheader("Deterministic Behavior (No Learning)")
            st.markdown("Same input always produces same output:")

            det = examples['deterministic_decisions']
            st.json(det)
    else:
        st.info("No examples available")

if __name__ == "__main__":
    main()