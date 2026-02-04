"""
Agent Status API Server
Provides REST endpoints for agent status, onboarding, and demo triggers.
Enables terminal-free demos and agent visibility.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
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












# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_state import AgentStateManager, AgentState
from demo_mode_config import is_demo_mode_active, is_freeze_mode_active

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global agent state (LEGACY - now using real AgentRuntime above)
# These are kept for backwards compatibility but not used for status endpoint
_agent_state_manager = None
_last_decision = None
_start_time = datetime.datetime.now()


def get_or_create_agent_state():
    """Get or create agent state (LEGACY - for backwards compatibility only)."""
    global _agent_state_manager
    if _agent_state_manager is None:
        try:
            # Try to load from file if exists
            state_file = 'logs/agent_state.json'
            if os.path.exists(state_file):
                _agent_state_manager = AgentStateManager.load_from_file(state_file, 'agent-demo-001')
            else:
                _agent_state_manager = AgentStateManager('agent-demo-001', AgentState.IDLE)
        except Exception as e:
            # Create default state manager on error
            _agent_state_manager = AgentStateManager('agent-demo-001', AgentState.IDLE)
    
    # Return dict representation for API
    state_info = _agent_state_manager.get_current_state_info()
    return {
        'agent_id': _agent_state_manager.agent_id,
        'state': _agent_state_manager.current_state.value,
        'loop_count': len(_agent_state_manager.get_state_history()),
        'last_decision': None
    }


def update_last_decision(action: str, confidence: float, explanation: str):
    """Update last decision globally (LEGACY - for backwards compatibility only)."""
    global _last_decision
    _last_decision = {
        'action': action,
        'confidence': confidence,
        'timestamp': datetime.datetime.now().isoformat(),
        'explanation': explanation
    }


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
        
        # Update last decision
        update_last_decision(
            action='onboard',
            confidence=1.0,
            explanation=f'Successfully onboarded {data["app_name"]} to stage environment'
        )
        
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


@app.route('/api/demo/crash', methods=['POST'])
def demo_crash_recovery():
    """Trigger crash recovery demonstration."""
    try:
        # Simulate crash scenario
        from core.rl_orchestrator_safe import SafeOrchestrator
        
        orchestrator = SafeOrchestrator(env='stage')
        
        # Simulate crash recovery decision
        context = {
            'app_name': 'demo-api',
            'failure_type': 'crash',
            'exit_code': 1
        }
        
        result = orchestrator.execute_action(
            action='restart',
            context=context,
            source='rl_decision_layer'
        )
        
        explanation = (
            f"Crash detected in demo-api (exit code 1) → "
            f"RL decided to restart service → "
            f"{'Success' if result.get('success') else 'Failed'}"
        )
        
        update_last_decision(
            action='restart',
            confidence=0.95,
            explanation=explanation
        )
        
        return jsonify({
            'status': 'success',
            'scenario': 'crash_recovery',
            'decision': 'restart',
            'confidence': 0.95,
            'explanation': explanation,
            'result': result,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/demo/overload', methods=['POST'])
def demo_overload_handling():
    """Trigger overload handling demonstration."""
    try:
        # Simulate overload scenario
        from core.rl_orchestrator_safe import SafeOrchestrator
        
        orchestrator = SafeOrchestrator(env='stage')
        
        # Simulate overload handling decision
        context = {
            'app_name': 'demo-api',
            'cpu_usage': 85,
            'memory_usage': 75,
            'replicas': 1
        }
        
        result = orchestrator.execute_action(
            action='scale_up',
            context=context,
            source='rl_decision_layer'
        )
        
        explanation = (
            f"High CPU (85%) detected in demo-api → "
            f"RL decided to scale up → "
            f"{'Success' if result.get('success') else 'Failed'}"
        )
        
        update_last_decision(
            action='scale_up',
            confidence=0.92,
            explanation=explanation
        )
        
        return jsonify({
            'status': 'success',
            'scenario': 'overload_handling',
            'decision': 'scale_up',
            'confidence': 0.92,
            'explanation': explanation,
            'result': result,
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


@app.route('/', methods=['GET'])
def index():
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
