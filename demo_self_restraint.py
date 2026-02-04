#!/usr/bin/env python3
"""
Demo: Self-Restraint Blocking
Demonstrates intentional self-blocking based on internal rules.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.self_restraint import SelfRestraint, BlockReason


def demo_memory_instability_block():
    """Demo: Self-block due to high memory instability."""
    print("="*70)
    print("DEMO 1: SELF-BLOCK - MEMORY INSTABILITY")
    print("="*70)
    print()
    
    restraint = SelfRestraint(max_instability_score=75)
    
    # Simulate high instability (80% failure rate)
    memory_signals = {
        'recent_failures': 8,
        'recent_successes': 2,
        'instability_score': 80,
        'repeated_actions': 1
    }
    
    print("[Memory Signals]")
    print(f"  Recent Failures: {memory_signals['recent_failures']}")
    print(f"  Instability Score: {memory_signals['instability_score']}/100")
    print(f"  Threshold: {restraint.max_instability_score}")
    print()
    
    block_decision = restraint.evaluate_block(memory_signals=memory_signals)
    
    print("[Self-Restraint Evaluation]")
    print(f"  Should Block: {block_decision.should_block}")
    if block_decision.should_block:
        print(f"  Block Reason: {block_decision.reason}")
        print(f"  Self-Imposed: {block_decision.self_imposed}")
        print(f"  Details: {block_decision.details}")
    print()
    
    print("RESULT: Agent self-blocks due to memory instability!")
    print("  agent_state → 'blocked'")
    print("  NO action executed")
    print("  Returns to 'observing' next cycle")
    print()


def demo_conflicting_signals_block():
    """Demo: Self-block due to conflicting health signals."""
    print("="*70)
    print("DEMO 2: SELF-BLOCK - CONFLICTING SIGNALS")
    print("="*70)
    print()
    
    restraint = SelfRestraint()
    
    # Simulate conflicting health signals
    health_signals = {
        'cpu_high': True,
        'cpu_low': True,  # Conflict!
        'memory_high': False,
        'memory_low': False
    }
    
    print("[Health Signals]")
    print(f"  CPU High: {health_signals['cpu_high']}")
    print(f"  CPU Low: {health_signals['cpu_low']}")
    print("  ⚠️  CONFLICT DETECTED: Both high and low!")
    print()
    
    block_decision = restraint.evaluate_block(health_signals=health_signals)
    
    print("[Self-Restraint Evaluation]")
    print(f"  Should Block: {block_decision.should_block}")
    if block_decision.should_block:
        print(f"  Block Reason: {block_decision.reason}")
        print(f"  Conflicts: {block_decision.details['conflicts']}")
        print(f"  Self-Imposed: {block_decision.self_imposed}")
    print()
    
    print("RESULT: Agent self-blocks due to conflicting signals!")
    print("  Cannot make reliable decision with contradictory data")
    print()


def demo_low_confidence_block():
    """Demo: Self-block due to low decision confidence."""
    print("="*70)
    print("DEMO 3: SELF-BLOCK - LOW CONFIDENCE")
    print("="*70)
    print()
    
    restraint = SelfRestraint(min_confidence=0.6)
    
    # Simulate low confidence decision
    decision_data = {
        'action': 'deploy',
        'confidence': 0.45  # Below threshold
    }
    
    print("[Decision Data]")
    print(f"  Action: {decision_data['action']}")
    print(f"  Confidence: {decision_data['confidence']}")
    print(f"  Threshold: {restraint.min_confidence}")
    print()
    
    block_decision = restraint.evaluate_block(decision_data=decision_data)
    
    print("[Self-Restraint Evaluation]")
    print(f"  Should Block: {block_decision.should_block}")
    if block_decision.should_block:
        print(f"  Block Reason: {block_decision.reason}")
        print(f"  Details: {block_decision.details}")
    print()
    
    print("RESULT: Agent self-blocks due to low confidence!")
    print("  Won't execute uncertain actions")
    print()


def demo_normal_flow():
    """Demo: Normal flow when no blocking conditions exist."""
    print("="*70)
    print("DEMO 4: NORMAL FLOW - NO SELF-BLOCKING")
    print("="*70)
    print()
    
    restraint = SelfRestraint(
        min_confidence=0.6,
        max_instability_score=75,
        max_recent_failures=5
    )
    
    # Healthy signals
    decision_data = {'confidence': 0.85}
    memory_signals = {
        'recent_failures': 1,
        'instability_score': 20,
        'repeated_actions': 1
    }
    health_signals = {
        'cpu_high': False,
        'cpu_low': False,
        'memory_high': False
    }
    
    print("[All Signals Healthy]")
    print(f"  Confidence: {decision_data['confidence']} (>= 0.6)")
    print(f"  Instability: {memory_signals['instability_score']} (<= 75)")
    print(f"  Recent Failures: {memory_signals['recent_failures']} (<= 5)")
    print(f"  No Conflicts: ✓")
    print()
    
    block_decision = restraint.evaluate_block(
        decision_data=decision_data,
        memory_signals=memory_signals,
        health_signals=health_signals
    )
    
    print("[Self-Restraint Evaluation]")
    print(f"  Should Block: {block_decision.should_block}")
    print()
    
    print("RESULT: Agent proceeds with normal decision!")
    print("  All self-restraint checks passed")
    print()


def demo_priority_rules():
    """Demo: Self-restraint rule priority."""
    print("="*70)
    print("DEMO 5: RULE PRIORITY")
    print("="*70)
    print()
    
    restraint = SelfRestraint(
        min_confidence=0.6,
        max_instability_score=75,
        max_recent_failures=5
    )
    
    # Multiple blocking conditions
    decision_data = {'confidence': 0.4}  # Low confidence
    memory_signals = {
        'recent_failures': 6,  # Too many failures
        'instability_score': 80  # High instability
    }
    health_signals = {
        'cpu_high': True,
        'cpu_low': True  # Conflict
    }
    
    print("[Multiple Blocking Conditions]")
    print("  1. Conflicting signals (CPU high AND low)")
    print("  2. Memory instability (score=80, failures=6)")
    print("  3. Low confidence (0.4 < 0.6)")
    print()
    
    block_decision = restraint.evaluate_block(
        decision_data=decision_data,
        memory_signals=memory_signals,
        health_signals=health_signals
    )
    
    print("[Self-Restraint Evaluation]")
    print(f"  Should Block: {block_decision.should_block}")
    print(f"  Block Reason: {block_decision.reason}")
    print()
    print("  ⚠️  Priority Order:")
    print("     1. Conflicting Signals (checked first)")
    print("     2. Memory Risk")
    print("     3. Low Confidence")
    print()
    print(f"  → Blocked by: {block_decision.reason}")
    print()


def main():
    """Run all demonstrations."""
    demo_memory_instability_block()
    print("\n")
    
    demo_conflicting_signals_block()
    print("\n")
    
    demo_low_confidence_block()
    print("\n")
    
    demo_normal_flow()
    print("\n")
    
    demo_priority_rules()
    
    print("="*70)
    print("SUMMARY: SELF-RESTRAINT BLOCKING")
    print("="*70)
    print()
    print("BLOCKED state now represents TWO types:")
    print()
    print("  1. ERROR-BASED (crashes, exceptions)")
    print("  2. SELF-IMPOSED (intentional restraint)")
    print()
    print("Self-Restraint Rules:")
    print()
    print("  Rule 1: Conflicting Signals")
    print("    Example: cpu_high=True AND cpu_low=True")
    print("    Action: Block (can't trust contradictory data)")
    print()
    print("  Rule 2: Memory Instability Risk")
    print("    Example: instability_score > 75 OR failures > 5")
    print("    Action: Block (system too unstable)")
    print()
    print("  Rule 3: Low Confidence")
    print("    Example: decision.confidence < 0.6")
    print("    Action: Block (too uncertain)")
    print()
    print("Behavior when self-blocked:")
    print("  • agent_state → 'blocked'")
    print("  • NO action executed")
    print("  • Explanation logged with 'self_imposed': true")
    print("  • Returns to 'observing' next cycle")
    print()
    print("Logging Format:")
    print('  {')
    print('    "agent_state": "blocked",')
    print('    "block_reason": "memory_instability_risk",')
    print('    "self_imposed": true,')
    print('    "block_details": {...}')
    print('  }')
    print()
    print("✅ SELF-RESTRAINT ENABLES INTENTIONAL SELF-BLOCKING")
    print()


if __name__ == "__main__":
    main()
