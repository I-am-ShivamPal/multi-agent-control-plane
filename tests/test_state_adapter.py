
import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.state_adapter import StateAdapter

class TestStateAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = StateAdapter(env='dev')

    def test_adapt_state(self):
        """Test full state adaptation"""
        event = {
            'event_type': 'high_cpu',
            'metrics': {'cpu_percent': 90.5, 'memory_percent': 50.0}
        }
        agent_state = 'DECIDING'
        memory_context = {'recent_failures': 2, 'instability_score': 45}
        
        rl_request = self.adapter.adapt_state(event, agent_state, memory_context)
        
        # Check structure
        self.assertEqual(rl_request['environment'], 'dev')
        self.assertEqual(rl_request['event_type'], 'high_cpu')
        
        # Check enriched context
        self.assertEqual(rl_request['agent_context']['fsm_state'], 'DECIDING')
        self.assertEqual(rl_request['agent_context']['recent_failures'], 2)
        
        # Check normalized metrics
        self.assertAlmostEqual(rl_request['metrics']['cpu_percent'], 90.5)

    def test_normalization(self):
        """Test metric normalization handles missing/bad data"""
        event = {
            'event_type': 'crash',
            'metrics': {'cpu_percent': 'invalid', 'memory_percent': None}
        }
        
        rl_request = self.adapter.adapt_state(event, 'IDLE', {})
        
        # Should default to 0.0 without crashing
        self.assertEqual(rl_request['metrics']['cpu_percent'], 0.0)
        self.assertEqual(rl_request['metrics']['memory_percent'], 0.0)

    def test_vectorization(self):
        """Test vector output for future model compatibility"""
        event = {
            'event_type': 'scale',
            'metrics': {'cpu_percent': 50, 'memory_percent': 60, 'error_rate': 0.1}
        }
        
        rl_request = self.adapter.adapt_state(event, 'IDLE', {})
        vector = self.adapter.to_vector(rl_request)
        
        # Expect [0.5, 0.6, 0.1]
        self.assertEqual(vector, [0.5, 0.6, 0.1])

if __name__ == "__main__":
    unittest.main()
