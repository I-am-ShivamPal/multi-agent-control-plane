#!/usr/bin/env python3
"""
Test External RL Integration
Comprehensive tests for RL API integration with safety validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.external_rl_client import ExternalRLClient, RLAPIConfig
from core.rl_response_validator import RLResponseValidator, validate_rl_response
from core.runtime_rl_pipe import get_rl_pipe


class TestExternalRLIntegration:
    """Test suite for external RL API integration"""
    
    def __init__(self):
        self.env = 'dev'
        self.test_results = []
    
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        print(result)
        self.test_results.append((test_name, passed, details))
    
    def test_rl_response_validator(self):
        """Test RL response validator"""
        print("\n" + "="*80)
        print("TEST 1: RL Response Validator")
        print("="*80)
        
        validator = RLResponseValidator(env='dev')
        
        # Test 1.1: Valid safe action
        response = {'action': 0, 'confidence': 0.95}
        is_valid, action, reason = validator.validate_response(response)
        self.log_test(
            "Valid NOOP action",
            is_valid and action == 0,
            f"action={action}, reason={reason}"
        )
        
        # Test 1.2: Out of bounds action
        response = {'action': 99, 'confidence': 0.95}
        is_valid, action, reason = validator.validate_response(response)
        self.log_test(
            "Out-of-bounds action → NOOP",
            not is_valid and action == 0,
            f"action={action}, reason={reason}"
        )
        
        # Test 1.3: Missing action field
        response = {'confidence': 0.95}
        is_valid, action, reason = validator.validate_response(response)
        self.log_test(
            "Missing action field → NOOP",
            not is_valid and action == 0,
            f"action={action}, reason={reason}"
        )
        
        # Test 1.4: Unsafe action for environment (ROLLBACK in dev)
        response = {'action': 4, 'confidence': 0.95}  # ROLLBACK
        is_valid, action, reason = validator.validate_response(response)
        self.log_test(
            "Unsafe action (ROLLBACK in dev) → NOOP",
            not is_valid and action == 0,
            f"action={action}, reason={reason}"
        )
        
        # Test 1.5: Safe action for dev (RESTART)
        response = {'action': 1, 'confidence': 0.95}  # RESTART
        is_valid, action, reason = validator.validate_response(response)
        self.log_test(
            "Safe action (RESTART in dev)",
            is_valid and action == 1,
            f"action={action}, reason={reason}"
        )
    
    def test_external_rl_client_mock(self):
        """Test external RL client with mock scenarios"""
        print("\n" + "="*80)
        print("TEST 2: External RL Client (Mock Scenarios)")
        print("="*80)
        
        # Test 2.1: Response structure validation
        test_response = {
            'action': 0,
            'confidence': 0.95,
            'metadata': {'model': 'demo-frozen'}
        }
        
        safe_action, metadata = validate_rl_response(test_response, env='dev')
        self.log_test(
            "Valid API response structure",
            metadata['is_valid'] and safe_action == 0,
            f"action={safe_action}, validation={metadata['reason']}"
        )
        
        # Test 2.2: Error response handling
        error_response = {
            'action': 0,
            'error': 'Simulated API error',
            'fallback': True
        }
        
        safe_action, metadata = validate_rl_response(error_response, env='dev')
        self.log_test(
            "Error response → NOOP fallback",
            not metadata['is_valid'] and safe_action == 0,
            f"action={safe_action}, validation={metadata['reason']}"
        )
    
    def test_runtime_pipeline_integration(self):
        """Test full runtime pipeline integration"""
        print("\n" + "="*80)
        print("TEST 3: Runtime Pipeline Integration")
        print("="*80)
        
        # Test 3.1: Invalid event validation
        rl_pipe = get_rl_pipe(env='dev')
        
        invalid_event = {}  # Missing required fields
        result = rl_pipe.pipe_runtime_event(invalid_event)
        
        self.log_test(
            "Invalid event → NOOP execution",
            result['rl_action'] == 0 and 'validation_error' in result,
            f"action={result['rl_action']}"
        )
        
        # Test 3.2: Valid event with mock local RL
        # Temporarily disable external API for this test
        original_setting = os.getenv("USE_EXTERNAL_RL_API")
        os.environ["USE_EXTERNAL_RL_API"] = "false"
        
        rl_pipe_local = get_rl_pipe(env='dev')
        
        valid_event = {
            'event_id': 'test-002',  # Required field
            'event_type': 'latency_spike',
            'app_name': 'test-app',
            'latency_ms': 3000,
            'timestamp': '2026-02-06T10:00:00'
        }
        
        try:
            result = rl_pipe_local.pipe_runtime_event(valid_event)
            self.log_test(
                "Valid event → RL decision",
                'rl_action' in result and 'execution' in result,
                f"action={result.get('rl_action', 'N/A')}"
            )
        except Exception as e:
            self.log_test(
                "Valid event → RL decision",
                False,
                f"Error: {str(e)}"
            )
        
        # Restore original setting
        if original_setting:
            os.environ["USE_EXTERNAL_RL_API"] = original_setting
        else:
            os.environ.pop("USE_EXTERNAL_RL_API", None)
    
    def test_proof_logging(self):
        """Test proof logging functionality"""
        print("\n" + "="*80)
        print("TEST 4: Proof Logging")
        print("="*80)
        
        from core.proof_logger import write_rl_decision_proof
        
        # Test proof trail generation
        state = {'event_type': 'test', 'app_name': 'test-app'}
        api_response = {'action': 0, 'confidence': 0.95}
        
        try:
            write_rl_decision_proof(
                state=state,
                api_response=api_response,
                validation_result="PASSED",
                safety_status="SAFE",
                executed_action=0,
                env='dev'
            )
            
            # Check if proof log exists
            proof_log_exists = os.path.exists('runtime_rl_proof.log')
            self.log_test(
                "Proof logging creates log file",
                proof_log_exists,
                f"File exists: {proof_log_exists}"
            )
            
            if proof_log_exists:
                with open('runtime_rl_proof.log', 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for Unicode arrow (→) - this is the correct format
                    has_decision_flow = "RL decision received → validated →" in content
                    self.log_test(
                        "Proof log contains decision flow with Unicode arrows",
                        has_decision_flow,
                        "Unicode arrow (→) format verified"
                    )
                
                if "RL DECISION PROOF TRAIL" in content:
                    print("✅ Proof trail header found")
                
                if has_decision_flow:
                    print("\n✅ Sample from proof log:")
                    print("-" * 80)
                    # Show last 20 lines
                    lines = content.split('\n')
                    for line in lines[-15:]:
                        if line.strip():
                            print(line)
                    print("-" * 80)
            
        except Exception as e:
            self.log_test(
                "Proof logging execution",
                False,
                f"Error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*20 + "RL INTEGRATION FINAL LOCK - TEST SUITE" + " "*20 + "║")
        print("╚" + "="*78 + "╝")
        
        self.test_rl_response_validator()
        self.test_external_rl_client_mock()
        self.test_runtime_pipeline_integration()
        self.test_proof_logging()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        failed = sum(1 for _, p, _ in self.test_results if not p)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! RL Integration Final Lock is ready.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review output above.")
        
        return failed == 0


if __name__ == "__main__":
    tester = TestExternalRLIntegration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
