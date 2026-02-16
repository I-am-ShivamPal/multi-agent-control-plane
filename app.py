"""Flask API for Render Deployment"""

from flask import Flask, jsonify, request
import os
import json
from middleware import process_runtime_event
from api_registry import registry_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(registry_bp, url_prefix='/api/registry')

# Environment configuration
ENV = os.getenv("ENVIRONMENT", "stage")
RL_ENDPOINT = os.getenv("RL_ENDPOINT", "http://localhost:5001/decide")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "environment": ENV,
        "service": "pravah-cicd"
    }), 200

@app.route("/api/runtime/process", methods=["POST"])
def process_runtime():
    """Process runtime event through middleware"""
    payload = request.json
    result = process_runtime_event(payload, RL_ENDPOINT)
    return jsonify(result), 200 if result["status"] == "success" else 400

@app.route("/api/demo/cycle", methods=["POST"])
def demo_cycle():
    """Run one complete demo cycle"""
    try:
        # Sample runtime event
        payload = {
            "app": "demo-api",
            "env": ENV,
            "state": "crashed",
            "latency_ms": 250,
            "errors_last_min": 5,
            "workers": 2
        }
        
        result = process_runtime_event(payload, RL_ENDPOINT)
        
        return jsonify({
            "cycle": "complete",
            "input": payload,
            "output": result,
            "environment": ENV
        }), 200
    except Exception as e:
        return jsonify({
            "cycle": "error",
            "error": str(e),
            "explanation": "Demo cycle failed - check logs"
        }), 500

@app.route("/api/demo/validate", methods=["GET"])
def validate_demo():
    """Run demo lock validation"""
    try:
        from validate_demo_lock import validate_demo_lock
        proof = validate_demo_lock()
        return jsonify(proof), 200
    except Exception as e:
        return jsonify({
            "validation": "FAIL",
            "error": str(e),
            "explanation": "Validation failed - check configuration"
        }), 500

@app.route("/", methods=["GET"])
def index():
    """API documentation"""
    return jsonify({
        "service": "Pravah - Multi-Agent CI/CD System",
        "environment": ENV,
        "endpoints": {
            "/health": "Health check",
            "/api/runtime/process": "Process runtime event (POST)",
            "/api/demo/cycle": "Run demo cycle (POST)"
        }
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
