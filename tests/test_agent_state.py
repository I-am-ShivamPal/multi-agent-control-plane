#!/usr/bin/env python3
"""
Test Agent State Machine
Tests for the agent state management system.
"""

import unittest
from core.agent_state import AgentState, AgentStateManager


class TestAgentState(unittest.TestCase):
    """Test cases for agent state management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "test-agent-001"
        self.manager = AgentStateManager(self.agent_id)
    
    def test_initial_state(self):
        """Test initial state is IDLE."""
        self.assertEqual(self.manager.current_state, AgentState.IDLE)
    
    def test_valid_transition(self):
        """Test valid state transitions."""
        # IDLE -> OBSERVING
        self.assertTrue(self.manager.can_transition_to(AgentState.OBSERVING))
        self.assertTrue(self.manager.transition_to(AgentState.OBSERVING, "test"))
        self.assertEqual(self.manager.current_state, AgentState.OBSERVING)
        
        # OBSERVING -> VALIDATING
        self.assertTrue(self.manager.can_transition_to(AgentState.VALIDATING))
        self.assertTrue(self.manager.transition_to(AgentState.VALIDATING, "test"))
        self.assertEqual(self.manager.current_state, AgentState.VALIDATING)
    
    def test_invalid_transition(self):
        """Test invalid state transitions raise ValueError."""
        # IDLE -> ACTING is invalid
        with self.assertRaises(ValueError):
            self.manager.transition_to(AgentState.ACTING, "invalid")
    
    def test_complete_loop(self):
        """Test complete agent loop state transitions."""
        transitions = [
            (AgentState.OBSERVING, "start observing"),
            (AgentState.VALIDATING, "start validating"),
            (AgentState.DECIDING, "start deciding"),
            (AgentState.ENFORCING, "start enforcing"),
            (AgentState.ACTING, "start acting"),
            (AgentState.OBSERVING_RESULTS, "start observing results"),
            (AgentState.EXPLAINING, "start explaining"),
            (AgentState.IDLE, "return to idle")
        ]
        
        for target_state, reason in transitions:
            self.assertTrue(self.manager.transition_to(target_state, reason))
            self.assertEqual(self.manager.current_state, target_state)
    
    def test_state_history(self):
        """Test state history tracking."""
        self.manager.transition_to(AgentState.OBSERVING, "test1")
        self.manager.transition_to(AgentState.VALIDATING, "test2")
        
        history = self.manager.get_state_history()
        self.assertGreaterEqual(len(history), 3)  # init + 2 transitions
        
        # Check last entry
        last_entry = history[-1]
        self.assertEqual(last_entry["state"], AgentState.VALIDATING.value)
        self.assertEqual(last_entry["reason"], "test2")
        self.assertEqual(last_entry["agent_id"], self.agent_id)
    
    def test_blocked_state(self):
        """Test transition to blocked state from various states."""
        # From OBSERVING
        self.manager.transition_to(AgentState.OBSERVING, "test")
        self.assertTrue(self.manager.transition_to(AgentState.BLOCKED, "error"))
        self.assertEqual(self.manager.current_state, AgentState.BLOCKED)
        
        # From BLOCKED back to IDLE
        self.assertTrue(self.manager.transition_to(AgentState.IDLE, "recovery"))
        self.assertEqual(self.manager.current_state, AgentState.IDLE)
    
    def test_shutdown_state(self):
        """Test shutdown state (terminal)."""
        self.manager.transition_to(AgentState.SHUTTING_DOWN, "shutdown")
        self.assertEqual(self.manager.current_state, AgentState.SHUTTING_DOWN)
        
        # Cannot transition from SHUTTING_DOWN
        self.assertFalse(self.manager.can_transition_to(AgentState.IDLE))
    
    def test_state_info(self):
        """Test current state info."""
        info = self.manager.get_current_state_info()
        
        self.assertEqual(info["agent_id"], self.agent_id)
        self.assertEqual(info["current_state"], AgentState.IDLE.value)
        self.assertIn("entered_at", info)
        self.assertIn("duration_seconds", info)


if __name__ == "__main__":
    unittest.main()
