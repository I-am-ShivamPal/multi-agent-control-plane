#!/usr/bin/env python3
"""
Text Input Onboarding Demo
Demonstrates TEXT INPUT ONBOARDING feature with Observation → NOOP → Explanation

Test Cases:
1. "This is my backend service" → backend-app in dev
2. "my frontend ui" → frontend-app in dev
3. Verify NOOP decision (no RL call)
4. Verify explanation logged
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.text_input_onboarding import onboard_from_text, TextInputOnboarder
from core.proof_logger import write_proof, ProofEvents


def print_section(title):
    """Print section separator"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def demo_text_parsing():
    """Demo 1: Text Input Parsing"""
    print_section("DEMO 1: TEXT INPUT PARSING (No NLP/ML)")
    
    test_cases = [
        "This is my backend service",
        "my frontend ui application",
        "api server for production",
        "web app"
    ]
    
    onboarder = TextInputOnboarder()
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{text}\"")
        
        # Log text input received
        write_proof(ProofEvents.TEXT_INPUT_RECEIVED, {
            'text': text,
            'source': 'demo'
        })
        
        # Parse text
        result = onboarder.parse_text_input(text)
        
        # Log parsed result
        write_proof(ProofEvents.ONBOARDING_PARSED, {
            'app_name': result['app_name'],
            'runtime_type': result['runtime_type'],
            'env': result['env'],
            'state': result['state']
        })
        
        print(f"   ✅ App Name: {result['app_name']}")
        print(f"   ✅ Runtime Type: {result['runtime_type']}")
        print(f"   ✅ Environment: {result['env']}")
        print(f"   ✅ State: {result['state']}")
        print(f"   ℹ️  Event ID: {result['event_id']}")


def demo_onboarding_structure():
    """Demo 2: Structured Onboarding Event"""
    print_section("DEMO 2: STRUCTURED ONBOARDING EVENT")
    
    text = "This is my backend service"
    print(f"Input: \"{text}\"\n")
    
    event = onboard_from_text(text)
    
    print("Structured Event for Agent Runtime:")
    print("-" * 80)
    
    import json
    print(json.dumps(event, indent=2))
    
    print("\n✅ Ready to feed into agent runtime")
    print("✅ Expected behavior: Observation → NOOP → Explanation")


def demo_noop_explanation():
    """Demo 3: Expected NOOP Decision & Explanation"""
    print_section("DEMO 3: EXPECTED AGENT RUNTIME BEHAVIOR")
    
    text = "This is my backend service"
    event = onboard_from_text(text)
    
    print("Input Event:")
    print(f"  App Name: {event['app_name']}")
    print(f"  State: {event['state']}")
    print(f"  Environment: {event['env']}")
    
    print("\nAgent Runtime Flow:")
    print("  1. SENSE     → Detects onboarding event (state='newly_onboarded')")
    print("  2. VALIDATE  → Validates event structure")
    print("  3. DECIDE    → ✅ FORCED NOOP (onboarding policy)")
    print("  4. ENFORCE   → NOOP passes safety checks")
    print("  5. ACT       → Execute NOOP (do nothing)")
    print("  6. OBSERVE   → Monitor new app state")
    print("  7. EXPLAIN   → Log explanation")
    
    print("\nExpected Decision:")
    print("  {")
    print(f"    'action': 'noop',")
    print(f"    'rl_action': 0,")
    print(f"    'source': 'onboarding_policy',")
    print(f"    'skip_rl': True,  # No RL decision for onboarding")
    print(f"    'reasoning': \"New application '{event['app_name']}' onboarding policy\"")
    print("  }")
    
    print("\nExpected Explanation:")
    print(f"  \"New application '{event['app_name']}' ({event['runtime_type']}) onboarded to {event['env']} environment.")
    print(f"   Monitoring initialized. No action required (onboarding policy).")
    print(f"   Establishing baseline metrics before autonomous actions.\"")


def demo_why_noop():
    """Demo 4: WHY NOOP is Correct for Onboarding"""
    print_section("DEMO 4: WHY NOOP IS CORRECT FOR ONBOARDING")
    
    print("\n✅ Safety First")
    print("   - Never take action on unknown/new applications")
    print("   - Avoid unintended consequences on onboarding")
    
    print("\n✅ Observation Period")
    print("   - New apps need baseline monitoring before decisions")
    print("   - Collect initial metrics, health signals, behavior patterns")
    
    print("\n✅ Demo Clarity")
    print("   - Shows agent can recognize when NOT to act")
    print("   - Demonstrates restraint and caution")
    
    print("\n✅ Trust Building")
    print("   - Predictable behavior for onboarding")
    print("   - User knows exactly what to expect")
    
    print("\n✅ Deterministic")
    print("   - Onboarding always → NOOP (no randomness)")
    print("   - Same input → same output")
    
    print("\n✅ No RL Pollution")
    print("   - Onboarding doesn't pollute RL training data")
    print("   - RL decisions are for operational events only")


def demo_proof_logging():
    """Demo 5: Proof Logging Verification"""
    print_section("DEMO 5: PROOF LOGGING VERIFICATION")
    
    text = "This is my backend service"
    event = onboard_from_text(text)
    
    print("Proof Events Logged:")
    print("  1. TEXT_INPUT_RECEIVED")
    print(f"     - text: \"{text}\"")
    
    print("\n  2. ONBOARDING_PARSED")
    print(f"     - app_name: {event['app_name']}")
    print(f"     - runtime_type: {event['runtime_type']}")
    print(f"     - env: {event['env']}")
    
    print("\n  3. ONBOARDING_NOOP_FORCED (when fed to agent runtime)")
    print(f"     - decision: noop")
    print(f"     - reason: Onboarding policy - no action on new applications")
    
    # Check if proof log exists
    proof_log_path = "logs/day1_proof.log"
    if os.path.exists(proof_log_path):
        print(f"\n✅ Proof log exists: {proof_log_path}")
        
        # Read last few entries
        with open(proof_log_path, 'r') as f:
            lines = f.readlines()
            
        # Find onboarding-related entries
        onboarding_entries = [line for line in lines if 'TEXT_INPUT' in line or 'ONBOARDING_PARSED' in line]
        
        if onboarding_entries:
            print(f"   Found {len(onboarding_entries)} onboarding-related entries")
            print("\n   Last entry:")
            print(f"   {onboarding_entries[-1][:150]}...")
    else:
        print(f"\nℹ️  Proof log will be created at: {proof_log_path}")


def demo_comparison():
    """Demo 6: Text Input vs Traditional Onboarding"""
    print_section("DEMO 6: TEXT INPUT vs TRADITIONAL ONBOARDING")
    
    print("\n📝 Traditional Onboarding (onboarding_entry.py):")
    print("   Input: {")
    print("     'repo_url': 'https://github.com/user/repo',")
    print("     'app_name': 'my-service',")
    print("     'runtime_type': 'backend'")
    print("   }")
    print("   → Requires 3 structured fields")
    print("   → Generates app_spec.json")
    print("   → Triggers deployment")
    
    print("\n💬 Text Input Onboarding (NEW):")
    print("   Input: \"This is my backend service\"")
    print("   → Single text string")
    print("   → Converts to runtime event")
    print("   → Feeds into agent (Observation → NOOP → Explanation)")
    
    print("\n🎯 Use Cases:")
    print("   Traditional: Production onboarding with full config")
    print("   Text Input:  Demo/quick onboarding for testing")


def main():
    """Run all demos"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "TEXT INPUT ONBOARDING DEMO" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    demos = [
        ("Text Input Parsing", demo_text_parsing),
        ("Structured Onboarding Event", demo_onboarding_structure),
        ("Expected NOOP Behavior", demo_noop_explanation),
        ("WHY NOOP is Correct", demo_why_noop),
        ("Proof Logging", demo_proof_logging),
        ("Comparison with Traditional", demo_comparison)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    
    print("\n✅ Key Takeaways:")
    print("   1. Simple text → structured app data (no NLP/ML)")
    print("   2. Onboarding always forces NOOP (safety)")
    print("   3. Clear explanation logged")
    print("   4. No RL decision for onboarding")
    print("   5. Deterministic and reviewer-friendly")
    
    print("\n📁 Next Steps:")
    print("   1. Feed onboarding event to agent runtime")
    print("   2. Verify Observation → NOOP → Explanation flow")
    print("   3. Check proof logs for ONBOARDING_NOOP_FORCED event")


if __name__ == "__main__":
    main()
