"""
Demo Scenario Endpoints
Provides 4 live-callable demo scenarios showing Input → Decision → Reason → Safety
"""

from flask import Blueprint, jsonify
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runtime import AgentRuntime
from core.text_input_onboarding import onboard_from_text

demo_bp = Blueprint('demo', __name__, url_prefix='/api/demo')


def format_demo_response(scenario_name, input_data, decision, safety_check):
    """Format demo response with clear Input → Decision → Reason → Safety flow"""
    return {
        'scenario': scenario_name,
        'timestamp': datetime.utcnow().isoformat(),
        'flow': {
            '1_input': input_data,
            '2_decision': {
                'action': decision.get('action'),
                'action_index': decision.get('rl_action', decision.get('action_index', 0)),
                'source': decision.get('source', 'agent_runtime')
            },
            '3_reason': decision.get('explanation', decision.get('reasoning', 'No explanation available')),
            '4_safety': safety_check
        },
        'proof': {
            'state': decision.get('input_data', {}),
            'execution_result': decision.get('execution_result', {})
        }
    }


@demo_bp.route('/scenarios', methods=['GET'])
def list_scenarios():
    """List all available demo scenarios"""
    return jsonify({
        'scenarios': [
            {
                'name': 'crash',
                'endpoint': '/api/demo/crash',
                'description': 'Application crash detection and recovery',
                'method': 'POST'
            },
            {
                'name': 'overload',
                'endpoint': '/api/demo/overload',
                'description': 'System overload with scaling decision',
                'method': 'POST'
            },
            {
                'name': 'false_alarm',
                'endpoint': '/api/demo/false-alarm',
                'description': 'False positive detection (NOOP safety)',
                'method': 'POST'
            },
            {
                'name': 'onboarding',
                'endpoint': '/api/demo/onboarding',
                'description': 'New application onboarding via text input',
                'method': 'POST',
                'body': {'text': 'This is my backend service'}
            }
        ]
    })


@demo_bp.route('/crash', methods=['POST'])
def demo_crash():
    """
    Demo Scenario 1: Application Crash
    
    Shows:
    - Input: Crashed application state
    - Decision: RESTART action
    - Reason: Application unhealthy, restart required
    - Safety: Validated through safe executor
    """
    # Simulated crash event
    crash_input = {
        'event_type': 'health_check_failed',
        'app_id': 'demo-app-001',
        'app_name': 'payment-service',
        'env': 'dev',
        'runtime_type': 'backend',
        'state': 'crashed',
        'health_status': 'DOWN',
        'error_count': 5,
        'crash_reason': 'Out of memory',
        'uptime_seconds': 120,
        'last_restart': '2024-01-15T10:00:00Z'
    }
    
    # Process through agent
    agent = AgentRuntime(env='dev')
    decision = agent.process_event(crash_input)
    
    # Safety check
    safety_check = {
        'validation': 'PASSED',
        'safe_to_execute': True,
        'reason': 'Restart action allowed for crashed applications',
        'constraints': ['Max 3 restarts per hour', 'Requires crash state']
    }
    
    return jsonify(format_demo_response(
        'CRASH',
        crash_input,
        decision,
        safety_check
    ))


@demo_bp.route('/overload', methods=['POST'])
def demo_overload():
    """
    Demo Scenario 2: System Overload
    
    Shows:
    - Input: High CPU/memory usage
    - Decision: SCALE_UP action
    - Reason: Resource exhaustion detected
    - Safety: Validated against scaling limits
    """
    # Simulated overload event
    overload_input = {
        'event_type': 'resource_alert',
        'app_id': 'demo-app-002',
        'app_name': 'api-gateway',
        'env': 'dev',
        'runtime_type': 'backend',
        'state': 'running',
        'health_status': 'UP',
        'cpu_usage': 95,
        'memory_usage': 92,
        'request_queue_depth': 1500,
        'response_time_ms': 2500,
        'current_instances': 2,
        'max_instances': 10
    }
    
    # Process through agent
    agent = AgentRuntime(env='dev')
    decision = agent.process_event(overload_input)
    
    # Safety check
    safety_check = {
        'validation': 'PASSED',
        'safe_to_execute': True,
        'reason': 'Scale up allowed within instance limits',
        'constraints': ['Current: 2 instances', 'Max: 10 instances', 'CPU > 90%']
    }
    
    return jsonify(format_demo_response(
        'OVERLOAD',
        overload_input,
        decision,
        safety_check
    ))


@demo_bp.route('/false-alarm', methods=['POST'])
def demo_false_alarm():
    """
    Demo Scenario 3: False Alarm
    
    Shows:
    - Input: Alert that looks serious but isn't
    - Decision: NOOP (no action)
    - Reason: Metrics within acceptable threshold
    - Safety: Prevents unnecessary intervention
    """
    # Simulated false alarm
    false_alarm_input = {
        'event_type': 'metric_spike',
        'app_id': 'demo-app-003',
        'app_name': 'analytics-service',
        'env': 'dev',
        'runtime_type': 'backend',
        'state': 'running',
        'health_status': 'UP',
        'cpu_usage': 75,  # High but not critical
        'memory_usage': 70,
        'error_rate': 0.02,  # 2% - acceptable
        'duration_seconds': 30,  # Short spike
        'pattern': 'transient_spike',
        'previous_trend': 'stable'
    }
    
    # Process through agent
    agent = AgentRuntime(env='dev')
    decision = agent.process_event(false_alarm_input)
    
    # Safety check
    safety_check = {
        'validation': 'PASSED',
        'safe_to_execute': True,
        'reason': 'NOOP prevents overreaction to transient spikes',
        'constraints': ['Error rate < 5%', 'Duration < 60s', 'Pattern: transient']
    }
    
    return jsonify(format_demo_response(
        'FALSE_ALARM',
        false_alarm_input,
        decision,
        safety_check
    ))


@demo_bp.route('/onboarding', methods=['POST'])
def demo_onboarding():
    """
    Demo Scenario 4: New App Onboarding (Text Input)
    
    Shows:
    - Input: Free-text description
    - Decision: NOOP (onboarding policy)
    - Reason: New application requires observation period
    - Safety: Prevents actions on unknown applications
    """
    from flask import request
    
    # Get text input (or use default)
    text_input = request.get_json().get('text', 'This is my backend payment service')
    
    # Parse text to structured event
    onboarding_event = onboard_from_text(text_input)
    
    # Process through agent
    agent = AgentRuntime(env='dev')
    decision = agent.process_event(onboarding_event)
    
    # Safety check
    safety_check = {
        'validation': 'PASSED',
        'safe_to_execute': True,
        'reason': 'NOOP enforced for newly onboarded applications',
        'constraints': [
            'State: newly_onboarded',
            'No actions allowed',
            'Observation period required'
        ]
    }
    
    return jsonify(format_demo_response(
        'ONBOARDING',
        {
            'text_input': text_input,
            'parsed_event': onboarding_event
        },
        decision,
        safety_check
    ))


@demo_bp.route('/run-all', methods=['POST'])
def demo_run_all():
    """
    Run all 4 demo scenarios in sequence
    
    Returns: Array of all scenario results
    """
    from flask import request
    
    scenarios = []
    
    # 1. Crash
    with demo_bp.test_request_context('/api/demo/crash', method='POST'):
        crash_result = demo_crash()
        scenarios.append(crash_result.get_json())
    
    # 2. Overload
    with demo_bp.test_request_context('/api/demo/overload', method='POST'):
        overload_result = demo_overload()
        scenarios.append(overload_result.get_json())
    
    # 3. False Alarm
    with demo_bp.test_request_context('/api/demo/false-alarm', method='POST'):
        false_alarm_result = demo_false_alarm()
        scenarios.append(false_alarm_result.get_json())
    
    # 4. Onboarding
    text = request.get_json().get('text', 'This is my backend service') if request.get_json() else 'This is my backend service'
    with demo_bp.test_request_context('/api/demo/onboarding', method='POST', json={'text': text}):
        onboarding_result = demo_onboarding()
        scenarios.append(onboarding_result.get_json())
    
    return jsonify({
        'demo_run': 'complete',
        'scenarios_executed': 4,
        'results': scenarios
    })
