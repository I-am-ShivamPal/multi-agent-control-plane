#!/usr/bin/env python3
"""
External RL API Client
Consumes Ritesh's demo-frozen RL API for decision-making
Zero local decision logic - pure API consumption
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RLAPIConfig:
    """Configuration for RL API client"""
    base_url: str = "http://localhost:5000"
    timeout: int = 5
    max_retries: int = 3
    retry_delay: float = 0.5
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            base_url=os.getenv("RL_API_BASE_URL", "http://localhost:5000"),
            timeout=int(os.getenv("RL_API_TIMEOUT", "5")),
            max_retries=int(os.getenv("RL_API_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RL_API_RETRY_DELAY", "0.5"))
        )


class ExternalRLClient:
    """
    External RL API Client
    
    Connects to Ritesh's demo-frozen RL API for decision-making.
    NO local decision logic - all decisions come from external API.
    
    Endpoints:
    - POST /api/decision - Get RL decision for given state
    - GET  /api/status   - Health check
    - GET  /api/demo/scenarios - Get demo scenarios (optional)
    
    Error Handling:
    - All errors default to NOOP (action=0)
    - Comprehensive logging for debugging
    """
    
    def __init__(self, config: Optional[RLAPIConfig] = None, env: str = 'dev'):
        self.config = config or RLAPIConfig.from_env()
        self.env = env
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'Multi-Agent-System/{env}'
        })
    
    def get_decision(self, state: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Get RL decision from external API
        
        Args:
            state: Runtime state dictionary
            
        Returns:
            Tuple of (action_index, api_response_data)
            - action_index: 0-4 (NOOP, RESTART, SCALE_UP, SCALE_DOWN, ROLLBACK)
            - api_response_data: Full API response for logging
            
        On Error:
            Returns (0, error_info) - NOOP action with error details
        """
        from core.proof_logger import write_proof, ProofEvents
        
        endpoint = f"{self.config.base_url}/api/decision"
        
        # Prepare request payload
        payload = {
            'state': state,
            'env': self.env
        }
        
        # Log API call
        write_proof(ProofEvents.RL_API_CALL, {
            'env': self.env,
            'endpoint': endpoint,
            'state': state,
            'status': 'calling'
        })
        
        # Attempt API call with retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=self.config.timeout
                )
                
                # Check HTTP status
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Log successful API response
                    write_proof(ProofEvents.RL_API_RESPONSE, {
                        'env': self.env,
                        'endpoint': endpoint,
                        'response': response_data,
                        'status': 'success',
                        'attempt': attempt + 1
                    })
                    
                    # Extract action from response
                    action = response_data.get('action', 0)
                    
                    return (action, response_data)
                
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout after {self.config.timeout}s"
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                
            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"
                
            except ValueError as e:
                last_error = f"Invalid JSON response: {str(e)}"
            
            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        # All retries failed - log error and return NOOP
        write_proof(ProofEvents.RL_API_ERROR, {
            'env': self.env,
            'endpoint': endpoint,
            'error': last_error,
            'attempts': self.config.max_retries,
            'fallback_action': 0  # NOOP
        })
        
        return (0, {
            'action': 0,
            'error': last_error,
            'fallback': True,
            'reason': 'API call failed - defaulting to NOOP'
        })
    
    def check_health(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if RL API is healthy and available
        
        Returns:
            Tuple of (is_healthy, status_data)
        """
        endpoint = f"{self.config.base_url}/api/status"
        
        try:
            response = self.session.get(
                endpoint,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                status_data = response.json()
                return (True, status_data)
            else:
                return (False, {
                    'status': 'unhealthy',
                    'http_status': response.status_code,
                    'error': response.text
                })
                
        except Exception as e:
            return (False, {
                'status': 'unreachable',
                'error': str(e)
            })
    
    def get_demo_scenarios(self) -> Optional[Dict[str, Any]]:
        """
        Get demo scenarios from API (optional)
        
        Returns:
            Dictionary of demo scenarios or None on error
        """
        endpoint = f"{self.config.base_url}/api/demo/scenarios"
        
        try:
            response = self.session.get(
                endpoint,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None


# Global client instance
_rl_client = None


def get_rl_client(env: str = 'dev') -> ExternalRLClient:
    """
    Get global RL API client instance
    
    Args:
        env: Environment name (dev, stage, prod)
        
    Returns:
        ExternalRLClient instance
    """
    global _rl_client
    if _rl_client is None:
        _rl_client = ExternalRLClient(env=env)
    return _rl_client


def is_external_rl_enabled() -> bool:
    """
    Check if external RL API is enabled via configuration
    
    Returns:
        True if USE_EXTERNAL_RL_API=true, False otherwise
    """
    return os.getenv("USE_EXTERNAL_RL_API", "true").lower() == "true"
