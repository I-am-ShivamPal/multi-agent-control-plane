#!/usr/bin/env python3
"""
Test Memory-Driven Decision Overrides
Unit tests for memory influence on decision making.
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_memory import AgentMemory


class TestMemoryOverrides(unittest.TestCase):
    """Test cases for memory-driven decision overrides."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory(max_decisions=20, agent_id="test-agent")
    
    def test_failure_override_threshold(self):
        """Test that 3+ failures trigger override."""
        # Add 3 failures
        for i in range(3):
            self.memory.remember_decision(
                decision_type="test_decision",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        
        override = self.memory.should_override_decision(entity_id="app1", failure_threshold=3)
        self.assertTrue(override['override_applied'])
        self.assertEqual(override['override_decision'], 'noop')
        self.assertIn('recent_failures', override['override_reason'])
    
    def test_no_override_below_failure_threshold(self):
        """Test that <3 failures don't trigger override."""
        # Add 2 failures
        for i in range(2):
            self.memory.remember_decision(
                decision_type="test_decision",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        
        override = self.memory.should_override_decision(entity_id="app1", failure_threshold=3)
        self.assertFalse(override['override_applied'])
    
    def test_repetition_override(self):
        """Test that 3+ repeated actions trigger override."""
        # Add 3 identical actions
        for i in range(3):
            self.memory.remember_decision(
                decision_type="scale_decision",
                decision_data={"action": "scale_up"},
                outcome="success",
                context={"app_id": "app1"}
            )
        
        override = self.memory.should_override_decision(entity_id="app1", repetition_threshold=3)
        self.assertTrue(override['override_applied'])
        self.assertEqual(override['override_decision'], 'observe')
        self.assertIn('repetition_suppression', override['override_reason'])
    
    def test_instability_override(self):
        """Test that >66% failure rate triggers override."""
        # Add 7 failures, 3 successes (70% failure rate)
        for i in range(7):
            self.memory.remember_decision(
                decision_type="test_decision",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        for i in range(3):
            self.memory.remember_decision(
                decision_type="test_decision",
                decision_data={"action": 1},
                outcome="success",
                context={"app_id": "app1"}
            )
        
        override = self.memory.should_override_decision(entity_id="app1")
        self.assertTrue(override['override_applied'])
        # Should trigger failure override first (7 >= 3)
        self.assertIn('failures', override['override_reason'].lower())
    
    def test_memory_signals_extraction(self):
        """Test memory signal extraction."""
        # Add mixed decisions
        for i in range(5):
            self.memory.remember_decision(
                decision_type="test_decision",
                decision_data={"action": i % 3},
                outcome="failure" if i % 2 == 0 else "success",
                context={"app_id": "app1"}
            )
        
        signals = self.memory.get_memory_context(entity_id="app1")
        
        self.assertEqual(signals['recent_failures'], 3)  # 0, 2, 4
        self.assertEqual(signals['recent_successes'], 2)  # 1, 3
        self.assertEqual(signals['total_recent_decisions'], 5)
        self.assertIn('instability_score', signals)
        self.assertIn('last_action_outcome', signals)
        self.assertIn('recent_actions', signals)
    
    def test_repeated_actions_count(self):
        """Test repeated action counting."""
        # Add 4 consecutive identical actions
        for i in range(4):
            self.memory.remember_decision(
                decision_type="restart",
                decision_data={"action": "restart"},
                outcome="success",
                context={"app_id": "app1"}
            )
        
        signals = self.memory.get_memory_context(entity_id="app1")
        self.assertEqual(signals['repeated_actions'], 4)
    
    def test_entity_filtering(self):
        """Test that memory signals filter by entity."""
        # Add decisions for different apps
        for i in range(3):
            self.memory.remember_decision(
                decision_type="app1_decision",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        for i in range(2):
            self.memory.remember_decision(
                decision_type="app2_decision",
                decision_data={"action": 1},
                outcome="success",
                context={"app_id": "app2"}
            )
        
        # Check app1 signals
        signals_app1 = self.memory.get_memory_context(entity_id="app1")
        self.assertEqual(signals_app1['recent_failures'], 3)
        self.assertEqual(signals_app1['total_recent_decisions'], 3)
        
        # Check app2 signals
        signals_app2 = self.memory.get_memory_context(entity_id="app2")
        self.assertEqual(signals_app2['recent_successes'], 2)
        self.assertEqual(signals_app2['total_recent_decisions'], 2)
    
    def test_instability_score_calculation(self):
        """Test instability score calculation."""
        # 100% failure rate
        for i in range(5):
            self.memory.remember_decision(
                decision_type="test",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        
        signals = self.memory.get_memory_context(entity_id="app1")
        self.assertEqual(signals['instability_score'], 100)
        
        # 0% failure rate
        memory2 = AgentMemory(agent_id="test2")
        for i in range(5):
            memory2.remember_decision(
                decision_type="test",
                decision_data={"action": 1},
                outcome="success",
                context={"app_id": "app1"}
            )
        
        signals2 = memory2.get_memory_context(entity_id="app1")
        self.assertEqual(signals2['instability_score'], 0)
    
    def test_override_priority(self):
        """Test override priority (failures > instability)."""
        # Both failure threshold and instability should trigger
        # But failure override should take precedence
        for i in range(5):
            self.memory.remember_decision(
                decision_type="test",
                decision_data={"action": 1},
                outcome="failure",
                context={"app_id": "app1"}
            )
        
        override = self.memory.should_override_decision(entity_id="app1")
        self.assertTrue(override['override_applied'])
        # Should mention failures (first priority)
        self.assertIn('failures', override['override_reason'].lower())


if __name__ == "__main__":
    unittest.main()
