"""Middleware: Transport + Validation Only. NO business logic."""

import json
import requests
from jsonschema import validate, ValidationError

# Load frozen contract
with open("runtime_payload_schema.json") as f:
    SCHEMA = json.load(f)


def validate_payload(payload):
    """Validate against frozen contract."""
    validate(instance=payload, schema=SCHEMA)


def send_to_rl(payload, rl_endpoint):
    """Send validated payload to RL endpoint."""
    response = requests.post(rl_endpoint, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()


def process_runtime_event(payload, rl_endpoint):
    """
    Bridge layer: validate → send → return.
    
    Args:
        payload: Runtime data dict
        rl_endpoint: RL system URL
        
    Returns:
        dict: {"decision": ..., "status": "success"/"error"}
    """
    try:
        validate_payload(payload)
        decision = send_to_rl(payload, rl_endpoint)
        return {"decision": decision, "status": "success"}
    except ValidationError as e:
        return {"decision": None, "status": "error", "error": f"Invalid payload: {e.message}"}
    except requests.RequestException as e:
        return {"decision": None, "status": "error", "error": f"RL endpoint failed: {str(e)}"}
