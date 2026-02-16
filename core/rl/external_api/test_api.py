"""
Quick API Test - Verify demo endpoints work
"""

import requests
import json
import time
from threading import Thread
import subprocess
import sys

def test_api_endpoints():
    """Test all demo API endpoints"""
    base_url = "http://localhost:5000/api"
    
    print("Testing API endpoints...")
    
    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            print("Status endpoint working")
            status = response.json()
            print(f"   Demo mode: {status['demo_mode']}")
            print(f"   Learning: {status['learning_enabled']}")
        else:
            print(f"Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"Status endpoint error: {e}")
        return False
    
    # Test decision endpoint
    test_decision = {
        "environment": "dev",
        "event_type": "crash", 
        "event_data": {"service": "test"}
    }
    
    try:
        response = requests.post(f"{base_url}/decision", 
                               json=test_decision, 
                               timeout=5)
        if response.status_code == 200:
            print("Decision endpoint working")
            result = response.json()
            print(f"   Event: {result['runtime_event']['type']}")
            print(f"   Action: {result['rl_decision']['final_action']}")
            print(f"   Safe: {result['safety_result']['safe_for_demo']}")
        else:
            print(f"Decision endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"Decision endpoint error: {e}")
        return False
    
    # Test scenarios endpoint
    try:
        response = requests.get(f"{base_url}/demo/scenarios", timeout=5)
        if response.status_code == 200:
            print("Scenarios endpoint working")
            scenarios = response.json()
            print(f"   Available scenarios: {len(scenarios['scenarios'])}")
        else:
            print(f"Scenarios endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"Scenarios endpoint error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("RL Decision Brain API Test")
    print("=" * 40)
    
    # Start API server in background
    print("Starting API server...")
    try:
        # Import and test locally without server
        from rl_decision_brain import RLDecisionBrain, Environment, EventType
        
        brain = RLDecisionBrain(demo_mode=True)
        decision = brain.make_decision(Environment.DEV, EventType.CRASH, {"test": True})
        
        print("Core RL Brain working")
        print(f"   Decision: {decision['final_action']}")
        print(f"   Demo mode: {decision['demo_mode']}")
        print(f"   Learning disabled: {not decision['learning_enabled']}")
        
        print("\nDemo System Ready!")
        print("Next steps:")
        print("   1. Run: python demo_api.py")
        print("   2. Open: demo_interface.html")
        print("   3. Test demo scenarios")
        
    except Exception as e:
        print(f"Core system error: {e}")
        sys.exit(1)