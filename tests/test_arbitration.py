
import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.decision_arbitrator import DecisionArbitrator

class TestArbitration(unittest.TestCase):
    def setUp(self):
        self.arbitrator = DecisionArbitrator(env='dev')
        # Set threshold for testing
        self.arbitrator.confidence_threshold = 0.7

    def test_rl_high_confidence(self):
        """Test RL wins when confidence is high"""
        rl_decision = {'action': 'scale_up', 'confidence': 0.9, 'source': 'rl_brain'}
        rule_decision = {'action': 'noop', 'reason': 'queue_low', 'source': 'rules'}
        
        result = self.arbitrator.arbitrate(rl_decision, rule_decision, {})
        
        self.assertEqual(result['action'], 'scale_up')
        self.assertEqual(result['source'], 'rl_brain')
        self.assertTrue('confidence' in result)

    def test_rl_low_confidence(self):
        """Test Rules win when RL confidence is low"""
        rl_decision = {'action': 'scale_down', 'confidence': 0.5, 'source': 'rl_brain'}
        rule_decision = {'action': 'noop', 'reason': 'queue_stable', 'source': 'rules'}
        
        result = self.arbitrator.arbitrate(rl_decision, rule_decision, {})
        
        self.assertEqual(result['action'], 'noop')
        self.assertEqual(result['source'], 'rule_based')
        self.assertIn("RL confidence", result['reason'])

    def test_rule_advice(self):
        """Test Rules can advise an action when RL is unsure/noop"""
        rl_decision = {'action': 'noop', 'confidence': 0.0, 'source': 'rl_brain'}
        rule_decision = {'action': 'scale_up', 'reason': 'queue_depth_high', 'source': 'rules'}
        
        # With 0.0 confidence, RL falls back to rules
        result = self.arbitrator.arbitrate(rl_decision, rule_decision, {})
        
        self.assertEqual(result['action'], 'scale_up')
        self.assertEqual(result['source'], 'rule_based')

if __name__ == "__main__":
    unittest.main()
