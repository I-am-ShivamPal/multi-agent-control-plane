
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_runtime import AgentRuntime

class TestAgentRuntimeIntegration(unittest.TestCase):
    
    @patch('agent_runtime.AutoScaler')
    @patch('agent_runtime.MultiDeployAgent')
    @patch('agent_runtime.RedisEventBus') # Don't connect to real Redis
    def setUp(self, mock_redis, mock_mda, mock_autoscaler):
        # Setup mocks
        self.mock_autoscaler_cls = mock_autoscaler
        self.mock_autoscaler_instance = mock_autoscaler.return_value
        
        # Configure Autoscaler mock to have a work queue perception
        self.mock_autoscaler_instance.multi_agent.work_queue.qsize.return_value = 0
        self.mock_autoscaler_instance.get_recommendation.return_value = {
            'action': 'noop',
            'reason': 'queue_low',
            'confidence': 1.0, 
            'source': 'auto_scaler_rules'
        }

        # Initialize Runtime (mocks will be used)
        self.agent = AgentRuntime(env='dev', loop_interval=0)
        
    def test_full_decision_flow(self):
        """Test the full flow: Event -> handle_external_event -> FSM Loop"""
        print("\nTesting Full Agent Decision Flow (Sync API)...")
        
        # 1. Simulate High CPU Event
        event_data = {
            "event_id": "test-flow-1",
            "event_type": "high_cpu",
            "app_id": "test-app",
            "metrics": {"cpu_percent": 95.0},
            "environment": "dev",
            "timestamp": 1234567890
        }
        
        # Use the synchronous handler (it manages state transitions internally)
        # Mock the remote client to return a valid scale_up response
        with patch('core.rl_remote_client.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'action': 'scale_up',
                'confidence': 0.9,
                'reason': 'High CPU detected'
            }
            mock_post.return_value = mock_response
            
            result = self.agent.handle_external_event(event_data)
        
        print(f"Sync Decision Result: {result.get('conclusion')}")
        
        # Assertions
        self.assertEqual(self.agent.state_manager.current_state.value, 'idle') # Loop completes to idle
        decision = result.get('decision', {})
        self.assertEqual(decision.get('action_name'), 'scale_up')
        print("✅ Sync flow correctly processed high CPU event via Remote RL")

    def test_remote_rl_failure_fallback(self):
        """Test circuit breaker and fallback when Remote RL hangs/fails"""
        print("\nTesting Remote RL Failure & Fallback...")
        
        event_data = {
            "event_id": "test-remote-failure",
            "event_type": "high_cpu",
            "app_id": "test-app",
            "metrics": {"cpu_percent": 95.0},
            "timestamp": 1234567890
        }
        
        # Mock requests to timeout
        import requests
        with patch('core.rl_remote_client.requests.post', side_effect=requests.exceptions.Timeout):
            result = self.agent.handle_external_event(event_data)
            
        print(f"Fallback Result: {result.get('conclusion')}")
        
        # Should fallback to rule-based or noop (since RL failed)
        decision = result.get('decision', {})
        # Note: In our current setup, if RL fails, we expect a source other than 'rl_brain' or a 'noop'
        self.assertNotEqual(decision.get('source'), 'rl_brain')
        print("✅ Correctly handled Remote RL timeout with fallback")

    def test_arbitration_fallback(self):
        """Test that low confidence RL (from remote) falls back to rules"""
        print("\nTesting Low-Confidence Remote RL Fallback...")
        
        event_data = {
            "event_id": "test-arbitration",
            "event_type": "high_cpu", 
            "app_id": "test-app",
            "metrics": {"cpu_percent": 85.0},
            "timestamp": 1234567890
        }
        
        # Mock remote RL to return low confidence
        with patch('core.rl_remote_client.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'action': 'scale_down',
                'confidence': 0.05, # VERY LOW
                'reason': 'Uncertain'
            }
            mock_post.return_value = mock_response
            
            result = self.agent.handle_external_event(event_data)
        
        print(f"Low Confidence Result: {result.get('conclusion')}")
        
        decision = result.get('decision', {})
        self.assertEqual(decision['source'], 'rule_based')
        print("✅ Correctly fell back to Rule-Based logic due to low Remote RL confidence")

if __name__ == "__main__":
    unittest.main()
