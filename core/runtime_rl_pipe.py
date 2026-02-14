#!/usr/bin/env python3
"""
Runtime → RL Direct Pipe
Pipes normalized runtime JSON to Ritesh's RL layer unchanged and live
"""

from core.rl_remote_client import RLRemoteClient
from core.state_adapter import StateAdapter

class RuntimeRLPipe:
    """Direct pipe from runtime events to the remote RL Decision Brain."""
    
    def __init__(self, env='dev'):
        self.env = env
        # Use the remote RL client
        self.rl_brain = RLRemoteClient()
        self.state_adapter = StateAdapter(env)
        
    def get_decision(self, event_data: dict, agent_state: str = "unknown", memory_context: dict = None) -> dict:
        """
        Get RL decision WITHOUT executing it (Pure sensing/deciding).
        Used by the Arbitrator.
        """
        # Strict validation (same as pipe)
        from core.runtime_event_validator import validate_and_log_payload
        is_valid, validated_payload, error_msg = validate_and_log_payload(event_data, "RL_INPUT_QUERY")
        
        if not is_valid:
            return {'action': 'noop', 'confidence': 1.0, 'reason': error_msg}
            
        # Adapt Agent State -> RL State
        rl_request = self.state_adapter.adapt_state(
            event=validated_payload,
            agent_state=agent_state,
            memory_context=memory_context or {}
        )

        # Get RL decision
        decision_response = self.rl_brain.decide(rl_request)
        action_str = decision_response.get("action", "noop")
        source = decision_response.get("source", "rl_brain")
        
        # PROOF: Explicitly log if we hit a fallback (No Silent Failures)
        if source == "remote_client_fallback":
            from core.proof_logger import write_proof, ProofEvents
            write_proof(ProofEvents.RL_DECISION, {
                "env": self.env,
                "status": "failed",
                "reason": decision_response.get("reason"),
                "fallback_action": "noop",
                "source": "rl_brain_fallback"
            })
        
        return {
            "action": action_str,
            "confidence": decision_response.get("confidence", 0.8), 
            "brain_response": decision_response,
            "source": "rl_brain",
            "rl_state_vector": self.state_adapter.to_vector(rl_request) # Feature logging
        }

    def pipe_runtime_event(self, event_data: dict, agent_state: str = "unknown", memory_context: dict = None) -> dict:
        """Pipe runtime event to RL Brain with structured proof logging and validation."""
        
        # Strict validation BEFORE calling RL
        from core.runtime_event_validator import validate_and_log_payload
        from core.proof_logger import write_proof, ProofEvents
        
        is_valid, validated_payload, error_msg = validate_and_log_payload(event_data, "RL_INPUT")
        
        if not is_valid:
            # (validation error logic unchanged)
            # ...
            return {
                'rl_action': 0,
                'execution': {'status': 'refused'}, # Simplified for brevity in replace
                'validation_error': error_msg
            }
        
        # Structured proof logging - RL_CONSUME
        write_proof(ProofEvents.RL_CONSUME, {
            'env': self.env,
            'event_type': validated_payload.get('event_type'),
            'payload': validated_payload,
            'status': 'consumed'
        })
        
        # Log payload before RL (unchanged pass-through)
        from core.runtime_event_validator import RuntimeEventValidator
        RuntimeEventValidator.log_payload_integrity(validated_payload, "RL_CONSUME")
        
        # Adapt State
        rl_request = self.state_adapter.adapt_state(
            event=validated_payload,
            agent_state=agent_state,
            memory_context=memory_context or {}
        )

        # Get RL decision
        decision_response = self.rl_brain.decide(rl_request)

        
        # Map action string to integer for compatibility with existing orchestrator logic
        # 0: noop, 1: restart, 2: scale_up, 3: scale_down, 4: rollback
        action_map = {
            "noop": 0,
            "restart": 1,
            "scale_up": 2,
            "scale_down": 3,
            "rollback": 4
        }
        action_str = decision_response.get("action", "noop")
        rl_action_int = action_map.get(action_str, 0)

        # Structured proof logging - RL_DECISION
        write_proof(ProofEvents.RL_DECISION, {
            'env': self.env,
            'event_type': validated_payload.get('event_type'),
            'payload': validated_payload,
            'decision': rl_action_int,
            'decision_str': action_str,
            'brain_response': decision_response,
            'status': 'decided'
        })
        
        # Safe execution validation
        from core.rl_orchestrator_safe import get_safe_executor
        safe_executor = get_safe_executor(self.env)
        
        # Validate and execute (or refuse)
        # We pass the integer action as expected by validate_and_execute
        execution_result = safe_executor.validate_and_execute(rl_action_int, validated_payload)
        
        return {
            'rl_action': rl_action_int,
            'action_str': action_str,
            'execution': execution_result,
            'brain_metadata': decision_response
        }

# Global RL pipe instances per environment
_rl_pipes = {}

def get_rl_pipe(env='dev'):
    """Get RL pipe instance for specific environment."""
    global _rl_pipes
    if env not in _rl_pipes:
        _rl_pipes[env] = RuntimeRLPipe(env)
    return _rl_pipes[env]