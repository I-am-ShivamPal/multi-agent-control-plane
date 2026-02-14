"""
Agent Status API Server
Provides REST endpoints for agent status, onboarding, and demo triggers.
Enables terminal-free demos and agent visibility.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import sys

# Define project root
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add project root and _demos to path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

demos_dir = os.path.join(root_dir, '_demos')
if demos_dir not in sys.path:
    sys.path.insert(0, demos_dir)

import datetime
import json










from agent_runtime import AgentRuntime
import threading

# Create ONE shared agent instance
agent = AgentRuntime(env="stage")

# Run agent loop in background thread
def start_agent():
    agent.run()

threading.Thread(target=start_agent, daemon=True).start()












# Imports from core and demos
from core.agent_state import AgentStateManager, AgentState
from demo_mode_config import is_demo_mode_active, is_freeze_mode_active

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# The agent instance defined above is the single source of truth for the API.
# Legacy mock state management has been removed.


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy', 'service': 'agent-api'}), 200


@app.route('/api/agent/status', methods=['GET'])
def get_agent_status():
    """Return LIVE autonomous agent status."""
    try:
        status = agent.get_agent_status()
        
        # Add demo mode and freeze mode flags
        status['demo_mode'] = is_demo_mode_active()
        status['freeze_mode'] = is_freeze_mode_active()
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to get agent status"}), 500


@app.route('/api/agent/onboard', methods=['POST'])
def onboard_app():
    """Onboard new application via text input."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['app_name', 'repo_url', 'runtime']
        missing = [f for f in required if f not in data]
        
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Call onboarding system
        from onboarding_entry import process_onboarding_request
        
        # Create request dict
        onboarding_request = {
            'app_name': data['app_name'],
            'repo_url': data['repo_url'],
            'runtime': data['runtime'],
            'env': 'stage'  # Always onboard to stage in demo
        }
        
        result = process_onboarding_request(onboarding_request)
        
        return jsonify({
            'status': 'success',
            'message': f'App {data["app_name"]} onboarded successfully',
            'spec_file': result.get('spec_file', f'apps/registry/{data["app_name"]}.json'),
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/decision', methods=['POST'])
def get_decision():
    """Stable endpoint for dashboard to trigger manual decisions."""
    try:
        data = request.get_json()
        
        # 1. Map dashboard input to Agent Perception schema
        event_type = data.get('event_type', 'unknown')
        environment = data.get('environment', 'dev')
        event_data = data.get('event_data', {})
        
        # Add metadata for the internal loop
        perception_payload = {
            'event_id': f"dashboard-{datetime.datetime.now().timestamp()}",
            'event_type': event_type,
            'environment': environment,
            'data': event_data,
            'timestamp': datetime.datetime.now().timestamp(),
            'app_id': event_data.get('service', event_data.get('app_name', 'demo-app'))
        }
        
        # 2. Process synchronously through Agent FSM
        result = agent.handle_external_event(perception_payload)
        
        # 3. Map result to Frontend-friendly schema (Dashboard expected)
        decision = result.get('decision', {})
        action_result = result.get('action_result', {})
        observation = result.get('observation', {})
        
        # Extract safety metrics
        safety_status = action_result.get('status', 'noop')
        # Dashboard expects 'safety_result': { executed: bool, refused: bool, safe_for_demo: bool }
        executed = safety_status in ['success', 'executed']
        refused = not executed and decision.get('action_name') != 'noop'
        
        response = {
            'runtime_event': {
                'environment': environment,
                'type': event_type,
                'data': event_data,
                'timestamp': perception_payload['timestamp']
            },
            'rl_decision': {
                'proposed_action': decision.get('action_name', 'noop'),
                'final_action': decision.get('action_name', 'noop'), # Since we are the arbitrator
                'action_filtered': decision.get('override_applied', False),
                'reasoning': decision.get('reason', 'Autonomous decision')
            },
            'safety_result': {
                'executed': executed,
                'refused': refused,
                'safe_for_demo': True # Agent governance handles this
            },
            'system_status': {
                'demo_mode': is_demo_mode_active(),
                'learning_disabled': True,
                'deterministic': True
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "message": "Decision cycle failed"}), 500


@app.route('/api/demo/crash', methods=['POST'])
def demo_crash_recovery():
    """Trigger crash recovery demonstration via full Agent FSM."""
    try:
        # 1. Prepare perception payload for crash
        perception_payload = {
            'event_id': f"demo-crash-{datetime.datetime.now().timestamp()}",
            'event_type': 'crash',
            'environment': 'stage',
            'app_id': 'demo-api',
            'data': {
                'failure_type': 'crash',
                'exit_code': 1,
                'metrics': {'cpu_percent': 0, 'memory_percent': 0}
            },
            'timestamp': datetime.datetime.now().timestamp()
        }
        
        # 2. Process through full chain: Runtime -> RL -> Orchestrator
        result = agent.handle_external_event(perception_payload)
        
        decision = result.get('decision', {})
        action_result = result.get('action_result', {})
        
        explanation = (
            f"Scenario: Crash recovery triggered for demo-api → "
            f"RL Brain proposed: {decision.get('action_name', 'noop')} → "
            f"Final Status: {action_result.get('status', 'refused')}"
        )
        
        return jsonify({
            'status': 'success',
            'scenario': 'crash_recovery',
            'full_chain': True,
            'decision': decision.get('action_name', 'noop'),
            'confidence': decision.get('confidence', 0.0),
            'explanation': explanation,
            'result': action_result,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/demo/overload', methods=['POST'])
def demo_overload_handling():
    """Trigger overload handling demonstration via full Agent FSM."""
    try:
        # 1. Prepare perception payload for overload
        perception_payload = {
            'event_id': f"demo-overload-{datetime.datetime.now().timestamp()}",
            'event_type': 'high_cpu',
            'environment': 'stage',
            'app_id': 'demo-api',
            'data': {
                'cpu_usage': 85,
                'metrics': {'cpu_percent': 85.0, 'memory_percent': 75.0, 'workers': 1}
            },
            'timestamp': datetime.datetime.now().timestamp()
        }
        
        # 2. Process through full chain
        result = agent.handle_external_event(perception_payload)
        
        decision = result.get('decision', {})
        action_result = result.get('action_result', {})
        
        explanation = (
            f"Scenario: High CPU (85%) detected in demo-api → "
            f"RL Brain proposed: {decision.get('action_name', 'noop')} → "
            f"Final Status: {action_result.get('status', 'refused')}"
        )
        
        return jsonify({
            'status': 'success',
            'scenario': 'overload_handling',
            'full_chain': True,
            'decision': decision.get('action_name', 'noop'),
            'confidence': decision.get('confidence', 0.0),
            'explanation': explanation,
            'result': action_result,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/demo/healthy', methods=['POST'])
def demo_healthy_noop():
    """Trigger healthy system simulation via full Agent FSM."""
    try:
        # 1. Prepare perception payload for healthy system
        perception_payload = {
            'event_id': f"demo-healthy-{datetime.datetime.now().timestamp()}",
            'event_type': 'false_alarm',
            'environment': 'stage',
            'app_id': 'demo-api',
            'data': {
                'status': 'healthy',
                'metrics': {'cpu_percent': 10.0, 'memory_percent': 20.0, 'latency_ms': 45.0}
            },
            'timestamp': datetime.datetime.now().timestamp()
        }
        
        # 2. Process through full chain
        result = agent.handle_external_event(perception_payload)
        
        decision = result.get('decision', {})
        action_result = result.get('action_result', {})
        
        explanation = (
            f"Scenario: System is healthy (CPU 10%) → "
            f"RL Brain proposed: {decision.get('action_name', 'noop')} → "
            f"Final Status: {action_result.get('status', 'executed')}"
        )
        
        return jsonify({
            'status': 'success',
            'scenario': 'healthy_noop',
            'full_chain': True,
            'decision': decision.get('action_name', 'noop'),
            'confidence': decision.get('confidence', 0.0),
            'explanation': explanation,
            'result': action_result,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/demo/scenarios', methods=['GET'])
def list_demo_scenarios():
    """List available demo scenarios."""
    scenarios = {
        'scenarios': [
            {
                'id': 'crash',
                'name': 'Crash Recovery',
                'description': 'Demonstrates autonomous crash detection and service restart',
                'endpoint': '/api/demo/crash',
                'method': 'POST'
            },
            {
                'id': 'overload',
                'name': 'Overload Handling',
                'description': 'Demonstrates autonomous scaling based on resource usage',
                'endpoint': '/api/demo/overload',
                'method': 'POST'
            },
            {
                'id': 'onboard',
                'name': 'App Onboarding',
                'description': 'Demonstrates text-based application onboarding',
                'endpoint': '/api/agent/onboard',
                'method': 'POST',
                'required_fields': ['app_name', 'repo_url', 'runtime']
            },
            {
                'id': 'healthy',
                'name': 'Healthy (NOOP)',
                'description': 'Demonstrates autonomous steady-state monitoring with no intervention',
                'endpoint': '/api/demo/healthy',
                'method': 'POST'
            }
        ]
    }
    
    return jsonify(scenarios), 200


@app.route('/api/logs/proof', methods=['GET'])
def get_proof_logs():
    """Get recent proof log entries."""
    try:
        limit = request.args.get('limit', 20, type=int)
        proof_log = 'logs/day1_proof.log'
        
        if not os.path.exists(proof_log):
            return jsonify({'logs': []}), 200
        
        logs = []
        with open(proof_log, 'r') as f:
            lines = f.readlines()
            
        # Get last N lines
        for line in lines[-limit:]:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        return jsonify({
            'logs': logs,
            'count': len(logs),
            'total_available': len(lines)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rl/health', methods=['GET'])
def get_rl_health():
    """Proxy health check to remote RL service."""
    try:
        if not hasattr(agent, 'rl_pipe') or not hasattr(agent.rl_pipe, 'rl_brain'):
             return jsonify({'status': 'error', 'message': 'RL Pipe not initialized'}), 503
        
        health = agent.rl_pipe.rl_brain.get_health()
        return jsonify(health), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/rl/scope', methods=['GET'])
def get_rl_scope():
    """Proxy action scope from remote RL service."""
    try:
        if not hasattr(agent, 'rl_pipe') or not hasattr(agent.rl_pipe, 'rl_brain'):
             return jsonify({'status': 'error', 'message': 'RL Pipe not initialized'}), 503
        
        scope = agent.rl_pipe.rl_brain.get_scope()
        return jsonify(scope), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/rl/info', methods=['GET'])
def get_rl_info():
    """Get RL service configuration."""
    try:
        if not hasattr(agent, 'rl_pipe') or not hasattr(agent.rl_pipe, 'rl_brain'):
             return jsonify({'status': 'error', 'message': 'RL Pipe not initialized'}), 503
        
        client = agent.rl_pipe.rl_brain
        return jsonify({
            'url': client.url,
            'timeout': client.timeout,
            'max_failures': client._max_failures,
            'consecutive_failures': client._consecutive_failures
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Serve the dashboard HTML."""
    dashboard_path = os.path.join(root_dir, 'core', 'rl', 'external_api', 'advanced_dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return jsonify({'error': 'Dashboard not found'}), 404

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve the dashboard HTML."""
    dashboard_path = os.path.join(root_dir, 'core', 'rl', 'external_api', 'advanced_dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return jsonify({'error': 'Dashboard not found'}), 404

@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation."""
    docs = {
        'service': 'Multi-Agent CI/CD API',
        'version': '1.0.0',
        'demo_mode': is_demo_mode_active(),
        'freeze_mode': is_freeze_mode_active(),
        'endpoints': {
            'health': {
                'path': '/api/health',
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            'agent_status': {
                'path': '/api/agent/status',
                'method': 'GET',
                'description': 'Get current agent state and last decision'
            },
            'onboard': {
                'path': '/api/agent/onboard',
                'method': 'POST',
                'description': 'Onboard new application',
                'body': {
                    'app_name': 'string',
                    'repo_url': 'string',
                    'runtime': 'string'
                }
            },
            'demo_crash': {
                'path': '/api/demo/crash',
                'method': 'POST',
                'description': 'Trigger crash recovery demo'
            },
            'demo_overload': {
                'path': '/api/demo/overload',
                'method': 'POST',
                'description': 'Trigger overload handling demo'
            },
            'demo_scenarios': {
                'path': '/api/demo/scenarios',
                'method': 'GET',
                'description': 'List available demo scenarios'
            },
            'proof_logs': {
                'path': '/api/logs/proof',
                'method': 'GET',
                'description': 'Get recent proof logs',
                'query_params': {'limit': 'int (default: 20)'}
            }
        },
        'documentation': 'See DEMO_WALKTHROUGH.md for usage guide'
    }
    
    return jsonify(docs), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 Agent API Server starting on port {port}")
    print(f"📊 Demo Mode: {is_demo_mode_active()}")
    print(f"🔒 Freeze Mode: {is_freeze_mode_active()}")
    print(f"📍 Access API documentation at: http://localhost:{port}/")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
