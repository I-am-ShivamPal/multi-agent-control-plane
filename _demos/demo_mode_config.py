"""
Demo Mode Configuration - Execution Gate for Stage Demonstrations

This module provides hard-blocking execution gate configuration to ensure
orchestrator behavior is predictable and safe during stage demonstrations.

CRITICAL SAFETY:
- When DEMO_MODE=True, orchestrator only accepts actions from RL intake gate
- Production-level safety rules enforced regardless of environment
- Only explicitly allowed actions can execute
- All decision points logged for proof verification
"""

import os
import sys
from typing import List, Set

# ========== DEMO MODE FLAGS ==========

# Master demo mode switch - set to True for stage demonstrations
DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'

# Demo Freeze Mode Configuration
DEMO_FREEZE_MODE = os.getenv('DEMO_FREEZE_MODE', 'true').lower() == 'true'

# Enforce production-level safety rules even in dev/stage when DEMO_MODE active
DEMO_ENFORCE_PROD_SAFETY = True

# Require all actions to originate from RL decision layer
DEMO_REQUIRE_RL_INTAKE = True

# Block any direct orchestrator calls when DEMO_MODE active
DEMO_BLOCK_DIRECT_CALLS = True

# ========== ACTION ALLOWLIST ==========

# Explicitly allowed actions in DEMO_MODE
# ONLY these actions can execute, all others refused
DEMO_SAFE_ACTIONS: Set[str] = {
    'noop',           # No operation - always safe
    'restart',        # Service restart - controlled recovery
    'scale_up',       # Horizontal scaling - performance fix
    'scale_down',     # Resource optimization - safe downscale
}

# Actions explicitly BLOCKED in DEMO_MODE (redundant with allowlist, but explicit)
DEMO_BLOCKED_ACTIONS: Set[str] = {
    'rollback',              # Deployment rollback - too disruptive for demo
    'delete_data',           # Data operations - never allowed
    'modify_config',         # Configuration changes - unpredictable
    'external_call',         # External system access - unsafe
    'shell_exec',            # Shell command execution - dangerous
    'modify_permissions',    # Permission changes - security violation
    'stop_service',          # Service stoppage - demo blocker
}

# ========== PROOF LOGGING ==========

# Proof log file for demo freeze verification
DEMO_PROOF_LOG = "logs/demo_freeze_proof.log"

# Enable verbose proof logging in DEMO_MODE
DEMO_VERBOSE_PROOF = True

# Log every decision point including source validation
DEMO_LOG_ALL_GATES = True

# ========== SAFETY VALIDATION ==========

def is_demo_mode_active() -> bool:
    """Check if demo mode is currently active"""
    return DEMO_MODE

def is_action_allowed(action: str) -> bool:
    """
    Check if action is allowed in DEMO_MODE
    
    Args:
        action: Action name to validate
        
    Returns:
        True if action is on allowlist, False otherwise
    """
    if not DEMO_MODE:
        return True  # All actions allowed when demo mode inactive
    
    return action in DEMO_SAFE_ACTIONS

def is_action_blocked(action: str) -> bool:
    """
    Check if action is explicitly blocked in DEMO_MODE
    
    Args:
        action: Action name to validate
        
    Returns:
        True if action is explicitly blocked, False otherwise
    """
    if not DEMO_MODE:
        return False  # No blocks when demo mode inactive
    
    return action in DEMO_BLOCKED_ACTIONS

def validate_action_source(source: str) -> bool:
    """
    Validate that action came from approved source (RL layer)
    
    Args:
        source: Source identifier of action
        
    Returns:
        True if source is validated, False otherwise
    """
    if not DEMO_MODE or not DEMO_REQUIRE_RL_INTAKE:
        return True  # Skip validation when demo mode inactive
    
    approved_sources = {'rl_decision_layer', 'rl_intake_gate'}
    return source in approved_sources

def get_refusal_reason(action: str, source: str = None) -> str:
    """
    Generate detailed refusal reason for blocked action
    
    Args:
        action: Action that was refused
        source: Source of the action (optional)
        
    Returns:
        Human-readable refusal reason
    """
    if action in DEMO_BLOCKED_ACTIONS:
        return f"Action '{action}' is explicitly blocked in DEMO_MODE"
    
    if action not in DEMO_SAFE_ACTIONS:
        return f"Action '{action}' not on DEMO_MODE allowlist"
    
    if source and not validate_action_source(source):
        return f"Action source '{source}' not validated - must come from RL intake gate"
    
    return "Action refused by DEMO_MODE execution gate"

# ========== DEBUG INFO ==========

def get_demo_config_info() -> dict:
    """Get current demo mode configuration for debugging"""
    return {
        'demo_mode_active': DEMO_MODE,
        'enforce_prod_safety': DEMO_ENFORCE_PROD_SAFETY,
        'require_rl_intake': DEMO_REQUIRE_RL_INTAKE,
        'block_direct_calls': DEMO_BLOCK_DIRECT_CALLS,
        'allowed_actions': list(DEMO_SAFE_ACTIONS),
        'blocked_actions': list(DEMO_BLOCKED_ACTIONS),
        'proof_log': DEMO_PROOF_LOG,
    }

def is_freeze_mode_active() -> bool:
    """Check if demo freeze mode is active.
    
    Freeze mode prevents learning and behavior drift:
    - RL epsilon locked to 0 (deterministic)
    - Q-table updates disabled
    - No model drift
    
    Returns:
        bool: True if freeze mode is enabled via DEMO_FREEZE_MODE
    """
    return DEMO_FREEZE_MODE

def get_freeze_epsilon() -> float:
    """Get epsilon value for freeze mode.
    
    Returns:
        float: 0.0 if freeze mode active (deterministic), 0.1 otherwise
    """
    return 0.0 if DEMO_FREEZE_MODE else 0.1

def log_freeze_skip(state: str, action: str, reason: str = "freeze_mode_active"):
    """Log Q-table update skip due to freeze mode.
    
    Args:
        state: Current state
        action: Action that was skipped
        reason: Reason for skipping (default: freeze_mode_active)
    """
    try:
        from core.proof_logger import write_proof, ProofEvents
        write_proof(ProofEvents.RUNTIME_EMIT, {
            'event': 'q_table_update_skipped',
            'state': state,
            'action': action,
            'reason': reason,
            'freeze_mode': True,
            'message': 'Q-table update blocked by demo freeze mode'
        })
    except ImportError:
        # Proof logger not available, skip logging
        pass

# ========== ACTIVATION MESSAGE ==========

if DEMO_MODE:
    print("=" * 70)
    print("DEMO_MODE ACTIVE - Execution Gate Enabled")
    print("=" * 70)
    print("RL intake gate enforcement: ACTIVE")
    print("Production safety rules: ENFORCED")
    print(f"Allowed actions: {', '.join(sorted(DEMO_SAFE_ACTIONS))}")
    print(f"Proof logging: {DEMO_PROOF_LOG}")
    if DEMO_FREEZE_MODE:
        print("FREEZE MODE: Learning disabled, deterministic decisions")
    print("=" * 70)
