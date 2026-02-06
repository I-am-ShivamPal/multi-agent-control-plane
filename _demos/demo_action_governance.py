#!/usr/bin/env python3
"""
Demo: Action Governance System
Demonstrates autonomous action governance with eligibility, cooldowns, and repetition suppression.

Day 2 Deliverable: Agent knows when NOT to act.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.action_governance import ActionGovernance, GovernanceReason
from core.self_restraint import SelfRestraint, BlockReason
from core.proof_logger import write_proof, ProofEvents


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70 + "\n")


def print_result(blocked: bool, reason: str = None, details: dict = None):
    """Print formatted result."""
    if blocked:
        print(f"  ❌ Action BLOCKED")
        print(f"  Reason: {reason}")
        if details:
            for key, value in details.items():
                if key not in ['message']:
                    print(f"  {key}: {value}")
    else:
        print(f"  ✅ Action ALLOWED")
    print()


def demo_cooldown_enforcement():
    """Demo: Cooldown prevents rapid repeated actions."""
    print_header("SCENARIO 1: COOLDOWN ENFORCEMENT")
    
    governance = ActionGovernance(env='stage')
    context = {'app_name': 'demo-api'}
    
    print("[First Execution]")
    print("  → Attempting 'restart' action...")
    decision = governance.evaluate_action('restart', context, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("[Second Execution - Immediate Retry]")
    print("  → Attempting 'restart' action again (cooldown: 60s)...")
    decision = governance.evaluate_action('restart', context, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("RESULT: Agent self-blocks due to active cooldown!")
    print("  • No orchestrator intervention needed")
    print("  • Self-imposed block logged with explanation")
    print()


def demo_repetition_suppression():
    """Demo: Repetition limit prevents action loops."""
    print_header("SCENARIO 2: REPETITION SUPPRESSION")
    
    # Use shorter window for demo
    governance = ActionGovernance(
        env='stage',
        repetition_limit=3,
        repetition_window=10,  # 10 seconds for demo
        cooldown_periods={'scale_up': 0}  # No cooldown for demo clarity
    )
    context = {'app_name': 'demo-api', 'replicas': 1}
    
    print(f"[Repetition Limit: {governance.repetition_limit} actions in {governance.repetition_window}s]")
    print()
    
    for i in range(1, 5):
        print(f"[Execution {i}]")
        print(f"  → Attempting 'scale_up' action...")
        decision = governance.evaluate_action('scale_up', context, source='rl_decision_layer')
        print_result(decision.should_block, decision.reason, decision.details)
        
        if not decision.should_block:
            time.sleep(0.1)  # Small delay between actions
    
    print("RESULT: Agent blocks itself after repetition limit!")
    print("  • Prevents infinite scaling loops")
    print("  • Self-imposed block with action history logged")
    print()


def demo_action_eligibility():
    """Demo: Action eligibility prevents unauthorized actions."""
    print_header("SCENARIO 3: ACTION ELIGIBILITY")
    
    governance_prod = ActionGovernance(env='prod')
    governance_stage = ActionGovernance(env='stage')
    context = {'app_name': 'demo-api'}
    
    print("[Production Environment]")
    print("  → Attempting 'rollback' action in prod...")
    decision = governance_prod.evaluate_action('rollback', context, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("[Stage Environment]")
    print("  → Attempting 'rollback' action in stage...")
    decision = governance_stage.evaluate_action('rollback', context, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("RESULT: Environment-specific eligibility enforced!")
    print("  • Production blocks unsafe actions")
    print("  • Stage allows safe testing actions")
    print()


def demo_prerequisite_check():
    """Demo: Prerequisites must be met before action execution."""
    print_header("SCENARIO 4: PREREQUISITE VALIDATION")
    
    governance = ActionGovernance(env='dev')
    
    print("[Missing App Name]")
    print("  → Attempting 'restart' without app_name...")
    decision = governance.evaluate_action('restart', {}, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("[With App Name]")
    print("  → Attempting 'restart' with app_name...")
    decision = governance.evaluate_action('restart', {'app_name': 'demo-api'}, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("RESULT: Prerequisites validated before execution!")
    print("  • Missing requirements cause self-block")
    print("  • Clear explanation of what's missing")
    print()


def demo_uncertainty_noop():
    """Demo: High uncertainty triggers NOOP."""
    print_header("SCENARIO 5: UNCERTAINTY → NOOP")
    
    restraint = SelfRestraint()
    
    print("[High Confidence Decision]")
    decision_data = {'confidence': 0.85, 'action': 'restart'}
    print(f"  Confidence: {decision_data['confidence']}")
    decision = restraint.check_uncertainty(decision_data, uncertainty_threshold=0.5)
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("[Low Confidence Decision]")
    decision_data = {'confidence': 0.35, 'action': 'restart'}
    print(f"  Confidence: {decision_data['confidence']}")
    print(f"  Uncertainty: {1 - decision_data['confidence']}")
    decision = restraint.check_uncertainty(decision_data, uncertainty_threshold=0.5)
    print_result(decision.should_block, decision.reason, decision.details)
    
    # Log to proof log
    if decision.should_block:
        write_proof(ProofEvents.UNCERTAINTY_NOOP, {
            'env': 'stage',
            'confidence': decision_data['confidence'],
            'uncertainty': decision.details.get('uncertainty'),
            'threshold': 0.5,
            'recommended_action': 'noop'
        })
    
    print("RESULT: High uncertainty triggers NOOP!")
    print("  • Agent refuses to act when uncertain")
    print("  • Self-imposed restraint without orchestrator")
    print()


def demo_signal_conflict_observe():
    """Demo: Conflicting signals trigger observation mode."""
    print_header("SCENARIO 6: SIGNAL CONFLICT → OBSERVE")
    
    restraint = SelfRestraint()
    
    print("[Healthy Signals]")
    health_signals = {
        'cpu_high': False,
        'cpu_low': False,
        'memory_high': False
    }
    print(f"  CPU High: {health_signals['cpu_high']}")
    print(f"  CPU Low: {health_signals['cpu_low']}")
    decision = restraint.should_observe_instead_of_act(health_signals=health_signals)
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("[Conflicting Signals]")
    health_signals = {
        'cpu_high': True,
        'cpu_low': True,  # Conflict!
        'memory_high': False
    }
    print(f"  CPU High: {health_signals['cpu_high']}")
    print(f"  CPU Low: {health_signals['cpu_low']}")
    print("  ⚠️  CONFLICT DETECTED!")
    decision = restraint.should_observe_instead_of_act(health_signals=health_signals)
    print_result(decision.should_block, decision.reason, decision.details)
    
    # Log to proof log
    if decision.should_block:
        write_proof(ProofEvents.SIGNAL_CONFLICT_OBSERVE, {
            'env': 'stage',
            'conflicts': decision.details.get('conflicts', []),
            'recommended_action': 'observe',
            'message': 'Conflicting signals → observe mode'
        })
    
    print("RESULT: Signal conflicts trigger observation!")
    print("  • Agent observes instead of acting on bad data")
    print("  • Self-restraint prevents wrong decisions")
    print()


def demo_normal_flow():
    """Demo: Normal execution when all checks pass."""
    print_header("SCENARIO 7: NORMAL FLOW - ALL CHECKS PASS")
    
    governance = ActionGovernance(env='dev')
    context = {'app_name': 'demo-api', 'replicas': 2}
    
    print("[All Governance Checks]")
    print("  ✓ Action eligible for dev environment")
    print("  ✓ No active cooldown")
    print("  ✓ Repetition limit not exceeded")
    print("  ✓ All prerequisites met")
    print()
    
    print("  → Attempting 'restart' action...")
    decision = governance.evaluate_action('restart', context, source='rl_decision_layer')
    print_result(decision.should_block, decision.reason, decision.details)
    
    print("RESULT: Action allowed when governance checks pass!")
    print("  • Agent proceeds with normal execution")
    print("  • All gates validated and logged")
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("       DAY 2: AUTONOMOUS ACTION GOVERNANCE - DEMONSTRATION")
    print("="*70)
    print()
    print("Goal: Agent must know when NOT to act")
    print()
    print("Governance Rules:")
    print("  1. Action Eligibility    - Environment-specific allowlists")
    print("  2. Cooldown Enforcement  - Minimum time between actions")
    print("  3. Repetition Suppression - Prevent action loops")
    print("  4. Prerequisite Check    - Validate requirements")
    print("  5. Uncertainty → NOOP    - Block when confidence low")
    print("  6. Conflict → Observe    - Observe when signals conflict")
    print()
    print("All self-blocks logged with detailed explanations.")
    print()
    
    # Clear proof log for fresh demo
    proof_log = "logs/day1_proof.log"
    os.makedirs(os.path.dirname(proof_log), exist_ok=True)
    
    demo_cooldown_enforcement()
    input("Press Enter to continue...")
    
    demo_repetition_suppression()
    input("Press Enter to continue...")
    
    demo_action_eligibility()
    input("Press Enter to continue...")
    
    demo_prerequisite_check()
    input("Press Enter to continue...")
    
    demo_uncertainty_noop()
    input("Press Enter to continue...")
    
    demo_signal_conflict_observe()
    input("Press Enter to continue...")
    
    demo_normal_flow()
    
    print("="*70)
    print("                         DEMONSTRATION COMPLETE")
    print("="*70)
    print()
    print("Summary:")
    print("  ✅ Cooldown enforcement demonstrated")
    print("  ✅ Repetition suppression demonstrated")
    print("  ✅ Action eligibility demonstrated")
    print("  ✅ Prerequisite validation demonstrated")
    print("  ✅ Uncertainty → NOOP demonstrated")
    print("  ✅ Signal conflict → Observe demonstrated")
    print("  ✅ Normal flow demonstrated")
    print()
    print("Proof Log: logs/day1_proof.log")
    print("  • All self-blocks logged with explanations")
    print("  • Events: COOLDOWN_ACTIVE, REPETITION_SUPPRESSED,")
    print("           ACTION_ELIGIBILITY_FAILED, UNCERTAINTY_NOOP,")
    print("           SIGNAL_CONFLICT_OBSERVE")
    print()
    print("✅ AGENT CAN NOW REFUSE ITSELF WITHOUT ORCHESTRATOR INTERVENTION")
    print()


if __name__ == "__main__":
    main()
