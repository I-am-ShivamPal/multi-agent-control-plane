"""
Demo Validation Script
Tests deterministic behavior and action scope enforcement
"""

from rl_decision_brain import RLDecisionBrain, Environment, EventType
import json
import time

def test_deterministic_behavior():
    """Test that identical inputs produce identical outputs"""
    print("Testing Deterministic Behavior...")
    
    brain = RLDecisionBrain(demo_mode=True)
    
    # Test case: Same input multiple times
    test_cases = [
        (Environment.DEV, EventType.CRASH, {"service": "api"}),
        (Environment.STAGE, EventType.OVERLOAD, {"cpu": 80}),
        (Environment.PROD, EventType.FALSE_FAILURE, {"alert": "test"})
    ]
    
    for env, event, data in test_cases:
        print(f"\nTesting: {env.value} + {event.value}")
        
        # Make same decision 3 times
        decisions = []
        for i in range(3):
            decision = brain.make_decision(env, event, data)
            # Remove timestamp for comparison
            comparable = {k: v for k, v in decision.items() if k != 'timestamp'}
            decisions.append(comparable)
        
        # Verify all decisions are identical
        if all(d == decisions[0] for d in decisions):
            print(f"PASS: Deterministic behavior confirmed")
            print(f"   Action: {decisions[0]['final_action']}")
        else:
            print(f"FAIL: Non-deterministic behavior detected")
            return False
    
    return True

def test_action_scope_enforcement():
    """Test that illegal actions are never proposed"""
    print("\nTesting Action Scope Enforcement...")
    
    brain = RLDecisionBrain(demo_mode=True)
    
    # Test all environment/event combinations
    environments = [Environment.DEV, Environment.STAGE, Environment.PROD]
    events = [EventType.CRASH, EventType.OVERLOAD, EventType.FALSE_FAILURE]
    
    violations = []
    
    for env in environments:
        allowed = brain.allowed_actions[env]
        print(f"\nTesting {env.value} (allowed: {[a.value for a in allowed]})")
        
        for event in events:
            decision = brain.make_decision(env, event, {})
            final_action = decision['final_action']
            
            # Check if final action is in allowed set
            if final_action not in [a.value for a in allowed]:
                violations.append(f"{env.value}: {final_action} not in allowed actions")
            else:
                print(f"   {event.value} -> {final_action}")
    
    if violations:
        print(f"\nAction scope violations found:")
        for violation in violations:
            print(f"   - {violation}")
        return False
    else:
        print(f"\nAll actions within scope")
        return True

def test_prod_restrictions():
    """Specifically test that PROD never gets scale_up or rollback"""
    print("\nTesting PROD Restrictions...")
    
    brain = RLDecisionBrain(demo_mode=True)
    
    # Test all events in PROD
    for event in EventType:
        decision = brain.make_decision(Environment.PROD, event, {})
        action = decision['final_action']
        
        if action in ['scale_up', 'scale_down', 'rollback']:
            print(f"FAIL: PROD received illegal action {action} for {event.value}")
            return False
        else:
            print(f"PROD {event.value} -> {action} (safe)")
    
    return True

def generate_demo_logs():
    """Generate logs showing system behavior for demo proof"""
    print("\nGenerating Demo Proof Logs...")
    
    brain = RLDecisionBrain(demo_mode=True)
    
    demo_scenarios = [
        ("Dev Crash", Environment.DEV, EventType.CRASH, {"service": "api-server"}),
        ("Stage Overload", Environment.STAGE, EventType.OVERLOAD, {"cpu": 85}),
        ("Prod Conservative", Environment.PROD, EventType.OVERLOAD, {"memory": 90}),
        ("False Failure", Environment.PROD, EventType.FALSE_FAILURE, {"alert": "network"})
    ]
    
    logs = []
    
    for name, env, event, data in demo_scenarios:
        decision = brain.make_decision(env, event, data)
        
        log_entry = {
            "scenario": name,
            "timestamp": decision["timestamp"],
            "input": {
                "environment": env.value,
                "event": event.value,
                "data": data
            },
            "output": {
                "action": decision["final_action"],
                "filtered": decision["action_filtered"]
            },
            "demo_safe": True
        }
        
        logs.append(log_entry)
        print(f"{name}: {env.value} + {event.value} -> {decision['final_action']}")
    
    # Save logs to file
    with open('demo_proof_logs.json', 'w') as f:
        json.dump({
            "test_timestamp": time.time(),
            "system_status": brain.get_system_status(),
            "demo_scenarios": logs
        }, f, indent=2)
    
    print(f"Demo proof logs saved to demo_proof_logs.json")

if __name__ == "__main__":
    print("RL Decision Brain Demo Validation")
    print("=" * 50)
    
    # Run all tests
    tests_passed = 0
    total_tests = 3
    
    if test_deterministic_behavior():
        tests_passed += 1
    
    if test_action_scope_enforcement():
        tests_passed += 1
        
    if test_prod_restrictions():
        tests_passed += 1
    
    # Generate proof logs
    generate_demo_logs()
    
    print("\n" + "=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("DEMO FREEZE VALIDATION: PASSED")
        print("System ready for demo deployment")
    else:
        print("DEMO FREEZE VALIDATION: FAILED")
        print("System NOT ready for demo")