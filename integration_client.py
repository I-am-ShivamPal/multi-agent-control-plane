# Integration Client for External Consumers
# Use this to integrate with Shivam's Orchestrator

import requests

class OrchestatorClient:
    """Client to integrate with Shivam's Orchestrator API."""
    
    def __init__(self, base_url):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of deployed orchestrator
                     Example: "http://localhost:5000" or "https://your-app.vercel.app"
        """
        self.base_url = base_url.rstrip('/')
    
    def get_runtime_data(self):
        """
        Step 1: Get runtime data from Shivam's orchestrator.
        
        Returns:
            dict: Latest runtime event payload
        """
        response = requests.get(f"{self.base_url}/api/runtime/latest")
        response.raise_for_status()
        return response.json()
    
    def process_runtime_payload(self, payload):
        """
        Step 2: Process payload through agent for decision.
        
        Args:
            payload: Runtime event data dict
            
        Returns:
            tuple: (decision, status)
        """
        response = requests.post(
            f"{self.base_url}/api/agent/process",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result['decision'], result['status']
    
    def execute_action(self, decision):
        """
        Step 3: Execute the decided action.
        
        Args:
            decision: Decision dict from process_runtime_payload
            
        Returns:
            dict: Execution result
        """
        response = requests.post(
            f"{self.base_url}/api/action/execute",
            json=decision
        )
        response.raise_for_status()
        return response.json()


# Example Usage
if __name__ == "__main__":
    # Initialize client with your deployed URL
    client = OrchestatorClient("http://localhost:5000")
    
    # Full integration flow
    print("Step 1: Getting runtime data...")
    payload = client.get_runtime_data()
    print(f"Payload: {payload}")
    
    print("\nStep 2: Processing through agent...")
    decision, status = client.process_runtime_payload(payload)
    print(f"Decision: {decision}")
    print(f"Status: {status}")
    
    print("\nStep 3: Executing action...")
    result = client.execute_action(decision)
    print(f"Result: {result}")
