#!/usr/bin/env python3
"""
Test Agent Memory
Unit tests for bounded short-term memory system.
"""

import sys
import os
import unittest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_memory import AgentMemory, DecisionRecord, AppStateSnapshot


class TestAgentMemory(unittest.TestCase):
    """Test cases for agent memory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory(
            max_decisions=10,
            max_states_per_app=5,
            agent_id="test-agent"
        )
    
    def test_remember_decision(self):
        """Test remembering decisions."""
        decision = self.memory.remember_decision(
            decision_type="test_decision",
            decision_data={"action": 1},
            outcome="success"
        )
        
        self.assertIsInstance(decision, DecisionRecord)
        self.assertEqual(decision.decision_type, "test_decision")
        self.assertEqual(len(self.memory.decision_memory), 1)
    
    def test_decision_memory_bounds(self):
        """Test that decision memory respects max bounds (FIFO)."""
        # Add more than max_decisions
        for i in range(15):
            self.memory.remember_decision(
                decision_type=f"decision_{i}",
                decision_data={"index": i}
            )
        
        # Should only keep last 10
        self.assertEqual(len(self.memory.decision_memory), 10)
        
        # First should be decision_5 (0-4 evicted)
        first_decision = list(self.memory.decision_memory)[0]
        self.assertEqual(first_decision.decision_type, "decision_5")
        
        # Last should be decision_14
        last_decision = list(self.memory.decision_memory)[-1]
        self.assertEqual(last_decision.decision_type, "decision_14")
    
    def test_remember_app_state(self):
        """Test remembering app states."""
        snapshot = self.memory.remember_app_state(
            app_id="app1",
            status="running",
            health={"cpu": 50},
            recent_events=["deploy"]
        )
        
        self.assertIsInstance(snapshot, AppStateSnapshot)
        self.assertEqual(snapshot.app_id, "app1")
        self.assertEqual(snapshot.status, "running")
    
    def test_app_state_memory_bounds(self):
        """Test that app state memory respects max bounds per app (FIFO)."""
        # Add more than max_states_per_app for one app
        for i in range(8):
            self.memory.remember_app_state(
                app_id="app1",
                status=f"state_{i}",
                health={"index": i},
                recent_events=[]
            )
        
        # Should only keep last 5
        states = self.memory.app_state_memory["app1"]
        self.assertEqual(len(states), 5)
        
        # First should be state_3
        first_state = list(states)[0]
        self.assertEqual(first_state.status, "state_3")
    
    def test_recall_recent_decisions(self):
        """Test recalling recent decisions."""
        # Add some decisions
        for i in range(5):
            self.memory.remember_decision(
                decision_type=f"decision_{i}",
                decision_data={"index": i}
            )
        
        # Recall last 3
        recent = self.memory.recall_recent_decisions(3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1].decision_type, "decision_4")
    
    def test_recall_app_history(self):
        """Test recalling app history."""
        # Add states for app
        for i in range(5):
            self.memory.remember_app_state(
                app_id="app1",
                status=f"state_{i}",
                health={},
                recent_events=[]
            )
        
        # Recall history
        history = self.memory.recall_app_history("app1")
        self.assertEqual(len(history), 5)
        
        # Recall last 2
        history = self.memory.recall_app_history("app1", 2)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[-1].status, "state_4")
    
    def test_get_last_decision(self):
        """Test getting last decision."""
        self.assertIsNone(self.memory.get_last_decision())
        
        self.memory.remember_decision("test", {})
        last = self.memory.get_last_decision()
        self.assertIsNotNone(last)
        self.assertEqual(last.decision_type, "test")
    
    def test_get_app_current_state(self):
        """Test getting current app state."""
        self.assertIsNone(self.memory.get_app_current_state("app1"))
        
        self.memory.remember_app_state("app1", "running", {}, [])
        current = self.memory.get_app_current_state("app1")
        self.assertIsNotNone(current)
        self.assertEqual(current.status, "running")
    
    def test_memory_stats(self):
        """Test memory statistics."""
        self.memory.remember_decision("test", {})
        self.memory.remember_app_state("app1", "running", {}, [])
        
        stats = self.memory.get_memory_stats()
        self.assertEqual(stats["decision_count"], 1)
        self.assertEqual(stats["app_count"], 1)
        self.assertEqual(stats["total_app_states"], 1)
    
    def test_memory_snapshot(self):
        """Test memory snapshot export."""
        self.memory.remember_decision("test", {})
        self.memory.remember_app_state("app1", "running", {}, [])
        
        snapshot = self.memory.get_memory_snapshot()
        self.assertIn("memory_stats", snapshot)
        self.assertIn("recent_decisions", snapshot)
        self.assertIn("app_states", snapshot)
        self.assertEqual(len(snapshot["recent_decisions"]), 1)
    
    def test_load_memory_snapshot(self):
        """Test loading memory from snapshot."""
        # Create some memory
        self.memory.remember_decision("test1", {"data": 1})
        self.memory.remember_decision("test2", {"data": 2})
        self.memory.remember_app_state("app1", "running", {}, [])
        
        # Get snapshot
        snapshot = self.memory.get_memory_snapshot()
        
        # Create new memory and load snapshot
        new_memory = AgentMemory(max_decisions=10, max_states_per_app=5)
        new_memory.load_memory_snapshot(snapshot)
        
        # Verify
        self.assertEqual(len(new_memory.decision_memory), 2)
        self.assertEqual(len(new_memory.app_state_memory["app1"]), 1)
    
    def test_clear_memory(self):
        """Test clearing memory."""
        self.memory.remember_decision("test", {})
        self.memory.remember_app_state("app1", "running", {}, [])
        
        self.memory.clear_memory()
        
        self.assertEqual(len(self.memory.decision_memory), 0)
        self.assertEqual(len(self.memory.app_state_memory), 0)
    
    def test_json_save_load(self):
        """Test JSON save and load."""
        import tempfile
        import json
        
        # Add some data
        self.memory.remember_decision("test", {})
        self.memory.remember_app_state("app1", "running", {}, [])
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.memory.to_json(filepath)
            
            # Load into new memory
            new_memory = AgentMemory()
            new_memory.from_json(filepath)
            
            # Verify
            self.assertEqual(len(new_memory.decision_memory), 1)
            self.assertEqual(len(new_memory.app_state_memory), 1)
        
        finally:
            os.unlink(filepath)


if __name__ == "__main__":
    unittest.main()
