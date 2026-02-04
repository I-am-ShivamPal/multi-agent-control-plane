#!/usr/bin/env python3
"""
Demo: Memory-Driven Decision Overrides
Demonstrates how memory actively influences and overrides decisions.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_memory import AgentMemory


def demo_failure_override():
    """Demo: Memory overrides decision due to recent failures."""
    print("="*70)
    print("DEMO 1: MEMORY OVERRIDE - RECENT FAILURES")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=20, agent_id="demo-agent")
    
    # Simulate 5 consecutive failures for an app
    print("[Simulating 5 consecutive failures for 'web-app']")
    for i in range(5):
        memory.remember_decision(
            decision_type=f"restart_decision_{i}",
            decision_data={"action": "restart", "app_id": "web-app"},
            outcome="failure",
            context={"app_id": "web-app"}
        )
        print(f"  {i+1}. restart_decision_{i}: failure")
    print()
    
    # Check if memory should override
    override_check = memory.should_override_decision(entity_id="web-app")
    
    print("[Memory Override Check]")
    print(f"  Override Applied: {override_check['override_applied']}")
    if override_check['override_applied']:
        print(f"  Override Decision: {override_check['override_decision']}")
        print(f"  Override Reason: {override_check['override_reason']}")
    print()
    
    print("[Memory Signals]")
    signals = override_check['memory_signals']
    print(f"  Recent Failures: {signals['recent_failures']}")
    print(f"  Recent Actions: {signals['recent_actions']}")
    print(f"  Instability Score: {signals['instability_score']}/100")
    print(f"  Last Outcome: {signals['last_action_outcome']}")
    print()
    
    print("✅ RESULT: Memory prevents further restart attempts due to repeated failures")
    print()


def demo_repetition_override():
    """Demo: Memory overrides decision due to repeated same actions."""
    print("="*70)
    print("DEMO 2: MEMORY OVERRIDE - REPETITION SUPPRESSION")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=20, agent_id="demo-agent")
    
    # Simulate 4 consecutive identical actions
    print("[Simulating 4 consecutive 'scale_up' actions for 'api-service']")
    for i in range(4):
        memory.remember_decision(
            decision_type=f"scale_decision_{i}",
            decision_data={"action": "scale_up", "app_id": "api-service"},
            outcome="success",
            context={"app_id": "api-service"}
        )
        print(f"  {i+1}. scale_up: success")
    print()
    
    # Check override
    override_check = memory.should_override_decision(entity_id="api-service")
    
    print("[Memory Override Check]")
    print(f"  Override Applied: {override_check['override_applied']}")
    if override_check['override_applied']:
        print(f"  Override Decision: {override_check['override_decision']}")
        print(f"  Override Reason: {override_check['override_reason']}")
    print()
    
    print("[Memory Signals]")
    signals = override_check['memory_signals']
    print(f"  Repeated Actions: {signals['repeated_actions']} consecutive")
    print(f"  Recent Actions: {signals['recent_actions']}")
    print()
    
    print("✅ RESULT: Memory suppresses further 'scale_up' to force observation")
    print()


def demo_instability_override():
    """Demo: Memory overrides decision due to high instability."""
    print("="*70)
    print("DEMO 3: MEMORY OVERRIDE - HIGH INSTABILITY")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=20, agent_id="demo-agent")
    
    # Simulate mixed results with >66% failure rate
    print("[Simulating mixed deployment results (7 failures, 3 successes)]")
    outcomes = ['failure', 'failure', 'success', 'failure', 'failure', 
                'failure', 'success', 'failure', 'success', 'failure']
    
    for i, outcome in enumerate(outcomes):
        memory.remember_decision(
            decision_type=f"deploy_decision_{i}",
            decision_data={"action": "deploy", "app_id": "worker"},
            outcome=outcome,
            context={"app_id": "worker"}
        )
        print(f"  {i+1}. deploy: {outcome}")
    print()
    
    # Check override
    override_check = memory.should_override_decision(entity_id="worker")
    
    print("[Memory Override Check]")
    print(f"  Override Applied: {override_check['override_applied']}")
    if override_check['override_applied']:
        print(f"  Override Decision: {override_check['override_decision']}")
        print(f"  Override Reason: {override_check['override_reason']}")
    print()
    
    print("[Memory Signals]")
    signals = override_check['memory_signals']
    print(f"  Recent Failures: {signals['recent_failures']}/10")
    print(f"  Recent Successes: {signals['recent_successes']}/10")
    print(f"  Instability Score: {signals['instability_score']}/100 (>66 triggers override)")
    print()
    
    print("✅ RESULT: Memory prevents actions due to high instability")
    print()


def demo_normal_flow():
    """Demo: Normal decision flow when memory allows."""
    print("="*70)
    print("DEMO 4: NORMAL FLOW - NO MEMORY OVERRIDE")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=20, agent_id="demo-agent")
    
    # Simulate healthy pattern (mostly successes, varied actions)
    print("[Simulating healthy decision pattern]")
    decisions = [
        ("deploy", "success"),
        ("scale_up", "success"),
        ("deploy", "success"),
        ("restart", "failure"),
        ("observe", "success"),
    ]
    
    for i, (action, outcome) in enumerate(decisions):
        memory.remember_decision(
            decision_type=f"{action}_decision_{i}",
            decision_data={"action": action, "app_id": "healthy-app"},
            outcome=outcome,
            context={"app_id": "healthy-app"}
        )
        print(f"  {i+1}. {action}: {outcome}")
    print()
    
    # Check override
    override_check = memory.should_override_decision(entity_id="healthy-app")
    
    print("[Memory Override Check]")
    print(f"  Override Applied: {override_check['override_applied']}")
    print()
    
    print("[Memory Signals]")
    signals = override_check['memory_signals']
    print(f"  Recent Failures: {signals['recent_failures']}/5 (threshold: 3)")
    print(f"  Repeated Actions: {signals['repeated_actions']} (threshold: 3)")
    print(f"  Instability Score: {signals['instability_score']}/100 (threshold: >66)")
    print()
    
    print("✅ RESULT: Memory allows normal RL decision to proceed")
    print()


def demo_memory_signals_detail():
    """Demo: Detailed memory signal extraction."""
    print("="*70)
    print("DEMO 5: MEMORY SIGNAL DETAILS")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=20, agent_id="demo-agent")
    
    # Create diverse decision history
    history = [
        ("restart", "failure", "app1"),
        ("deploy", "success", "app1"),
        ("restart", "failure", "app1"),
        ("scale_up", "success", "app2"),
        ("restart", "failure", "app1"),  # 3 failures for app1
        ("observe", "success", "app2"),
    ]
    
    print("[Creating decision history...]")
    for i, (action, outcome, app_id) in enumerate(history):
        memory.remember_decision(
            decision_type=f"{action}_decision",
            decision_data={"action": action},
            outcome=outcome,
            context={"app_id": app_id}
        )
    print(f"  Added {len(history)} decisions")
    print()
    
    # Get memory signals for specific app
    print("[Memory Signals for 'app1']")
    context = memory.get_memory_context(entity_id="app1", lookback=10)
    
    print(f"  Entity ID: {context['entity_id']}")
    print(f"  Total Recent Decisions: {context['total_recent_decisions']}")
    print(f"  Recent Failures: {context['recent_failures']}")
    print(f"  Recent Successes: {context['recent_successes']}")
    print(f"  Recent Actions: {context['recent_actions']}")
    print(f"  Repeated Actions: {context['repeated_actions']}")
    print(f"  Instability Score: {context['instability_score']}/100")
    print(f"  Last Action Outcome: {context['last_action_outcome']}")
    print()
    
    # Get global memory signals (all apps)
    print("[Global Memory Signals (all apps)]")
    global_context = memory.get_memory_context(entity_id=None, lookback=10)
    
    print(f"  Total Recent Decisions: {global_context['total_recent_decisions']}")
    print(f"  Recent Failures: {global_context['recent_failures']}")
    print(f"  Recent Successes: {global_context['recent_successes']}")
    print(f"  Instability Score: {global_context['instability_score']}/100")
    print()


def main():
    """Run all demonstrations."""
    demo_failure_override()
    print("\n")
    
    demo_repetition_override()
    print("\n")
    
    demo_instability_override()
    print("\n")
    
    demo_normal_flow()
    print("\n")
    
    demo_memory_signals_detail()
    
    print("="*70)
    print("SUMMARY: MEMORY-DRIVEN DECISIONS")
    print("="*70)
    print()
    print("Memory actively influences decisions through 3 override mechanisms:")
    print()
    print("  1. Recent Failures (≥3) → NOOP")
    print("     Prevents actions when repeated failures detected")
    print()
    print("  2. Repeated Actions (≥3) → OBSERVE")
    print("     Suppresses identical actions to force observation")
    print()
    print("  3. High Instability (>66% failure rate) → NOOP")
    print("     Blocks actions when system is unstable")
    print()
    print("Every decision logs memory signals used:")
    print("  - recent_failures")
    print("  - recent_actions")
    print("  - repeated_actions")
    print("  - instability_score")
    print("  - last_action_outcome")
    print("  - override_applied (true/false)")
    print()
    print("✅ MEMORY NOW ACTIVELY CHANGES AGENT BEHAVIOR")
    print()


if __name__ == "__main__":
    main()
