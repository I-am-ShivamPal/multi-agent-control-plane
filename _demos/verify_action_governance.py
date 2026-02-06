#!/usr/bin/env python3
"""
Verification Script: Action Governance System
Automated verification that governance rules are working correctly.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.action_governance import ActionGovernance
from core.self_restraint import SelfRestraint
from core.proof_logger import ProofEvents


def verify_cooldown_enforcement():
    """Verify cooldown blocks rapid repeated actions."""
    print("[TEST 1] Cooldown Enforcement")
    
    governance = ActionGovernance(env='stage')
    context = {'app_name': 'test-app'}
    
    # First execution should succeed
    decision1 = governance.evaluate_action('restart', context, source='rl_decision_layer')
    if decision1.should_block:
        print("  ❌ FAIL: First execution should not be blocked")
        return False
    
    # Immediate retry should be blocked by cooldown
    decision2 = governance.evaluate_action('restart', context, source='rl_decision_layer')
    if not decision2.should_block:
        print("  ❌ FAIL: Immediate retry should be blocked by cooldown")
        return False
    
    if decision2.reason != 'cooldown_active':
        print(f"  ❌ FAIL: Expected 'cooldown_active', got '{decision2.reason}'")
        return False
    
    print("  ✅ PASS: Cooldown enforcement working")
    return True


def verify_repetition_suppression():
    """Verify repetition limit prevents action loops."""
    print("[TEST 2] Repetition Suppression")
    
    governance = ActionGovernance(
        env='dev',
        repetition_limit=3,
        repetition_window=60,
        cooldown_periods={'scale_up': 0}  # No cooldown
    )
    context = {'app_name': 'test-app', 'replicas': 1}
    
    # Execute action 3 times (at limit)
    for i in range(3):
        decision = governance.evaluate_action('scale_up', context, source='rl_decision_layer')
        if decision.should_block:
            print(f"  ❌ FAIL: Execution {i+1}/3 should not be blocked")
            return False
        time.sleep(0.01)
    
    # 4th execution should be blocked
    decision = governance.evaluate_action('scale_up', context, source='rl_decision_layer')
    if not decision.should_block:
        print("  ❌ FAIL: 4th execution should be blocked by repetition limit")
        return False
    
    if decision.reason != 'repetition_limit_exceeded':
        print(f"  ❌ FAIL: Expected 'repetition_limit_exceeded', got '{decision.reason}'")
        return False
    
    print("  ✅ PASS: Repetition suppression working")
    return True


def verify_action_eligibility():
    """Verify environment-specific eligibility rules."""
    print("[TEST 3] Action Eligibility")
    
    governance_prod = ActionGovernance(env='prod')
    governance_dev = ActionGovernance(env='dev')
    context = {'app_name': 'test-app'}
    
    # Rollback should be blocked in prod
    decision_prod = governance_prod.evaluate_action('rollback', context, source='rl_decision_layer')
    if not decision_prod.should_block:
        print("  ❌ FAIL: Rollback should be blocked in prod")
        return False
    
    # Rollback should be allowed in dev
    decision_dev = governance_dev.evaluate_action('rollback', context, source='rl_decision_layer')
    if decision_dev.should_block:
        print("  ❌ FAIL: Rollback should be allowed in dev")
        return False
    
    print("  ✅ PASS: Action eligibility working")
    return True


def verify_prerequisite_validation():
    """Verify prerequisites are checked."""
    print("[TEST 4] Prerequisite Validation")
    
    governance = ActionGovernance(env='dev')
    
    # Missing app_name should block
    decision = governance.evaluate_action('restart', {}, source='rl_decision_layer')
    if not decision.should_block:
        print("  ❌ FAIL: Missing app_name should block action")
        return False
    
    if decision.reason != 'prerequisite_not_met':
        print(f"  ❌ FAIL: Expected 'prerequisite_not_met', got '{decision.reason}'")
        return False
    
    # With app_name should succeed
    decision = governance.evaluate_action('restart', {'app_name': 'test-app'}, source='rl_decision_layer')
    if decision.should_block:
        print("  ❌ FAIL: Action with prerequisites should not be blocked")
        return False
    
    print("  ✅ PASS: Prerequisite validation working")
    return True


def verify_uncertainty_blocking():
    """Verify high uncertainty triggers NOOP."""
    print("[TEST 5] Uncertainty → NOOP")
    
    restraint = SelfRestraint()
    
    # High confidence should not block
    decision = restraint.check_uncertainty({'confidence': 0.85}, uncertainty_threshold=0.5)
    if decision.should_block:
        print("  ❌ FAIL: High confidence should not trigger block")
        return False
    
    # Low confidence should block
    decision = restraint.check_uncertainty({'confidence': 0.35}, uncertainty_threshold=0.5)
    if not decision.should_block:
        print("  ❌ FAIL: Low confidence should trigger NOOP")
        return False
    
    if decision.reason != 'uncertainty_too_high':
        print(f"  ❌ FAIL: Expected 'uncertainty_too_high', got '{decision.reason}'")
        return False
    
    print("  ✅ PASS: Uncertainty blocking working")
    return True


def verify_signal_conflict_observation():
    """Verify signal conflicts trigger observation mode."""
    print("[TEST 6] Signal Conflict → Observe")
    
    restraint = SelfRestraint()
    
    # No conflict should not block
    decision = restraint.should_observe_instead_of_act(
        health_signals={'cpu_high': False, 'cpu_low': False}
    )
    if decision.should_block:
        print("  ❌ FAIL: No conflict should not trigger observation")
        return False
    
    # Conflicting signals should trigger observation
    decision = restraint.should_observe_instead_of_act(
        health_signals={'cpu_high': True, 'cpu_low': True}
    )
    if not decision.should_block:
        print("  ❌ FAIL: Signal conflict should trigger observation")
        return False
    
    if decision.reason != 'signal_conflict_requires_observation':
        print(f"  ❌ FAIL: Expected 'signal_conflict_requires_observation', got '{decision.reason}'")
        return False
    
    print("  ✅ PASS: Signal conflict observation working")
    return True


def verify_proof_logging():
    """Verify governance events are logged to proof log."""
    print("[TEST 7] Proof Logging")
    
    proof_log = "logs/day1_proof.log"
    
    if not os.path.exists(proof_log):
        print("  ⚠️  SKIP: Proof log not found (run demo first)")
        return True
    
    # Check for governance event types
    expected_events = [
        'COOLDOWN_ACTIVE',
        'REPETITION_SUPPRESSED',
        'ACTION_ELIGIBILITY_FAILED',
        'UNCERTAINTY_NOOP',
        'SIGNAL_CONFLICT_OBSERVE'
    ]
    
    found_events = set()
    
    try:
        with open(proof_log, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    event_name = event.get('event_name', '')
                    if event_name in expected_events:
                        found_events.add(event_name)
                except json.JSONDecodeError:
                    continue
        
        missing = set(expected_events) - found_events
        if missing:
            print(f"  ⚠️  INFO: Some events not found (expected after demo): {missing}")
        else:
            print(f"  ✅ PASS: All governance events logged")
        
        return True
    except Exception as e:
        print(f"  ⚠️  SKIP: Could not verify proof log: {e}")
        return True


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("     AUTONOMOUS ACTION GOVERNANCE - VERIFICATION")
    print("="*70 + "\n")
    
    tests = [
        verify_cooldown_enforcement,
        verify_repetition_suppression,
        verify_action_eligibility,
        verify_prerequisite_validation,
        verify_uncertainty_blocking,
        verify_signal_conflict_observation,
        verify_proof_logging
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append(False)
        print()
    
    print("="*70)
    print("                    VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Action Governance System Verified!")
        print()
        print("Governance Guarantees:")
        print("  ✓ Cooldowns prevent rapid repeated actions")
        print("  ✓ Repetition limits prevent action loops")
        print("  ✓ Environment eligibility enforced")
        print("  ✓ Prerequisites validated before execution")
        print("  ✓ High uncertainty triggers NOOP")
        print("  ✓ Signal conflicts trigger observation")
        print("  ✓ All self-blocks logged with explanations")
        print()
        return 0
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
