#!/usr/bin/env python3
"""
Demo: Perception & Memory System
Demonstrates the perception layer and short-term memory capabilities.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_memory import AgentMemory
from core.perception import PerceptionLayer, Perception, PerceptionType, PerceptionPriority
from core.perception_adapters import OnboardingInputAdapter, SystemAlertAdapter
from core.memory_snapshot import visualize_memory, save_memory_snapshot


def demo_perception():
    """Demonstrate perception layer."""
    print("="*70)
    print("PERCEPTION LAYER DEMO")
    print("="*70)
    print()
    
    # Create perception layer
    perception_layer = PerceptionLayer("demo-agent")
    
    # Register adapters
    onboarding_adapter = OnboardingInputAdapter()
    alert_adapter = SystemAlertAdapter()
    
    perception_layer.register_adapter(onboarding_adapter)
    perception_layer.register_adapter(alert_adapter)
    
    print(f"[1] Registered {len(perception_layer.perception_adapters)} perception adapters")
    print()
    
    # Add some onboarding requests
    onboarding_adapter.add_onboarding_request({
        "app_name": "my-web-app",
        "repo_url": "https://github.com/user/app",
        "env": "dev"
    })
    
    onboarding_adapter.add_onboarding_request({
        "app_name": "api-service",
        "repo_url": "https://github.com/user/api",
        "env": "stage"
    })
    
    # Add system alerts
    alert_adapter.add_alert("cpu_high", "CPU usage above 90%", "critical")
    alert_adapter.add_alert("deploy_success", "Deployment completed", "low")
    
    print("[2] Added 2 onboarding requests and 2 system alerts")
    print()
    
    # Perceive
    perceptions = perception_layer.perceive()
    
    print(f"[3] Perceived {len(perceptions)} events (sorted by priority):")
    for i, p in enumerate(perceptions, 1):
        print(f"    {i}. {p.type} (priority {p.priority}): {p.data.get('app_name') or p.data.get('message', 'N/A')}")
    print()
    
    # Get highest priority
    highest = perception_layer.get_highest_priority_perception(perceptions)
    if highest:
        print(f"[4] Highest priority perception: {highest.type} (priority {highest.priority})")
    print()
    
    # Filter by type
    onboarding_perceptions = perception_layer.filter_by_type(
        perceptions, 
        PerceptionType.ONBOARDING_INPUT
    )
    print(f"[5] Onboarding perceptions: {len(onboarding_perceptions)}")
    print()
    
    # Stats
    stats = perception_layer.get_perception_stats()
    print("[6] Perception stats:")
    for key, value in stats.items():
        print(f"    {key}: {value}")
    print()


def demo_memory():
    """Demonstrate agent memory."""
    print("="*70)
    print("AGENT MEMORY DEMO")
    print("="*70)
    print()
    
    # Create memory
    memory = AgentMemory(
        max_decisions=10,
        max_states_per_app=5,
        agent_id="demo-agent"
    )
    
    print(f"[1] Created memory: max_decisions=10, max_states_per_app=5")
    print()
    
    # Remember some decisions
    print("[2] Remembering decisions...")
    for i in range(12):  # Exceed max to test FIFO
        memory.remember_decision(
            decision_type=f"deploy_decision_{i}",
            decision_data={"action": i % 3, "confidence": 0.8 + i * 0.01},
            outcome="success" if i % 2 == 0 else "failure"
        )
    print(f"    Added 12 decisions, memory should keep last 10 (FIFO eviction)")
    print()
    
    # Remember app states
    print("[3] Remembering app states...")
    apps = ["web-app", "api-service", "worker"]
    for app in apps:
        for i in range(3):
            memory.remember_app_state(
                app_id=app,
                status="running" if i % 2 == 0 else "deploying",
                health={"cpu": 40 + i * 10, "memory": 60 + i * 5},
                recent_events=[f"event_{i}"]
            )
    print(f"    Added states for 3 apps (3 states each)")
    print()
    
    # Recall recent decisions
    recent = memory.recall_recent_decisions(5)
    print(f"[4] Last 5 decisions:")
    for decision in recent:
        print(f"    - {decision.decision_type}: {decision.outcome}")
    print()
    
    # Recall app history
    print(f"[5] App history for 'web-app':")
    history = memory.recall_app_history("web-app")
    for state in history:
        print(f"    - {state.status} (CPU: {state.health.get('cpu')}%)")
    print()
    
    # Memory stats
    stats = memory.get_memory_stats()
    print("[6] Memory statistics:")
    for key, value in stats.items():
        print(f"    {key}: {value}")
    print()
    
    # Visualize memory
    print("[7] Memory visualization:")
    visualize_memory(memory, show_details=True)
    
    # Save snapshot
    snapshot_path = "logs/agent/demo_memory_snapshot.json"
    if save_memory_snapshot(memory, snapshot_path):
        print(f"\n[8] Memory snapshot saved to: {snapshot_path}")
    print()


def demo_memory_aware_decisions():
    """Demonstrate memory-aware decision making."""
    print("="*70)
    print("MEMORY-AWARE DECISIONS DEMO")
    print("="*70)
    print()
    
    memory = AgentMemory(max_decisions=5, agent_id="demo-agent")
    
    # Simulate agent loop with memory
    print("[Simulating Agent Loop with Memory]")
    print()
    
    for loop_num in range(3):
        print(f"Loop {loop_num + 1}:")
        
        # Get memory context
        recent_decisions = memory.recall_recent_decisions(3)
        
        print(f"  • Memory context: {len(recent_decisions)} recent decisions")
        if recent_decisions:
            print(f"    Last decision: {recent_decisions[-1].decision_type}")
        
        # Make decision influenced by memory
        if len(recent_decisions) >= 2 and all(d.outcome == "failure" for d in recent_decisions[-2:]):
            action = 0  # NOOP if last 2 decisions failed
            print(f"  • Decision: NOOP (memory shows recent failures)")
        else:
            action = (loop_num + 1) % 3
            print(f"  • Decision: ACTION_{action} (no recent failure pattern)")
        
        # Remember decision
        memory.remember_decision(
            decision_type=f"action_{action}_decision",
            decision_data={"action": action, "loop": loop_num},
            outcome="success" if action != 0 else "noop"
        )
        print(f"  • Decision remembered in memory")
        print()
    
    print("[Final Memory State]")
    stats = memory.get_memory_stats()
    print(f"  Decisions in memory: {stats['decision_count']}/{stats['decision_capacity']}")
    print(f"  Total decisions seen: {stats['total_decisions_seen']}")
    print()


def main():
    """Run all demos."""
    demo_perception()
    print("\n")
    demo_memory()
    print("\n")
    demo_memory_aware_decisions()
    
    print("="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print()
    print("Key Takeaways:")
    print("  1. Perception Layer aggregates from multiple sources with priority")
    print("  2. Memory is bounded (FIFO eviction when limits exceeded)")
    print("  3. Decisions can reference past context from memory")
    print("  4. Memory state is observable via snapshots")
    print()


if __name__ == "__main__":
    main()
