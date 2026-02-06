# TEXT INPUT ONBOARDING - Implementation Plan

## GOAL
Allow demo-level onboarding with ONE simple text input:  
**"This is my backend service"**

**Expected Behavior:**
1. Parse text → Extract app type
2. Convert to structured runtime data (app_name, env, state)
3. Feed into agent runtime
4. **Force: Observation → NOOP → Explanation**
5. NO actions taken (no restart, scale, etc.)
6. Clear logging of WHY NOOP was chosen

---

## ARCHITECTURE

```
Text Input
    ↓
[Text Parser] (demo-level, no NLP)
    ↓
Structured Data {app_name, env, state: "newly_onboarded"}
    ↓
[Agent Runtime]
    ↓
SENSE → "newly_onboarded" app detected
    ↓
VALIDATE → Valid onboarding event
    ↓
DECIDE → **FORCED NOOP** (no RL call for onboarding)
    ↓
ENFORCE → NOOP passes safety (always safe)
    ↓
ACT → Execute NOOP (do nothing)
    ↓
OBSERVE → Monitor new app state
    ↓
EXPLAIN → "New application onboarded. Monitoring initialized. No action required."
```

---

## WHY NOOP IS CORRECT FOR ONBOARDING

**Rationale:**
1. **Safety First:** Never take action on unknown/new applications
2. **Observation Period:** New apps need baseline monitoring before decisions
3. **Demo Clarity:** Shows agent can recognize when NOT to act
4. **Trust Building:** Demonstrates restraint and caution
5. **Deterministic:** Onboarding always → NOOP (predictable for demo)

**Explanation Template:**
```
"New application '{app_name}' onboarded to {env} environment.
Status: Monitoring initialized.
Decision: NOOP (no action required for newly onboarded applications).
Reason: Establishing baseline metrics before autonomous actions."
```

---

## IMPLEMENTATION STEPS

### Step 1: Create Text Input Parser

**File:** `core/text_input_onboarding.py` (NEW)

**Purpose:** Convert free text to structured app data (demo-level parsing)

**Logic:**
```python
Input: "This is my backend service"
                ↓
Keywords: ["backend", "service"]
                ↓
Output: {
    "app_name": "backend-service",
    "env": "dev",  # Default for onboarding
    "state": "newly_onboarded",
    "runtime_type": "backend"
}
```

### Step 2: Create Onboarding Perception Adapter

**File:** `core/onboarding_perception_adapter.py` (NEW)

**Purpose:** Feed onboarding events into agent runtime as perception

**Flow:**
```
Text Input → Parser → Structured Event → Perception Queue → Agent Runtime SENSE phase
```

### Step 3: Modify Agent Runtime Decision Logic

**File:** `agent_runtime.py` (MODIFY `_decide` method)

**Purpose:** Detect "newly_onboarded" state and **force NOOP** without calling RL

**Logic:**
```python
if validated_data.get('state') == 'newly_onboarded':
    # FORCE NOOP for onboarding - no RL decision needed
    return {
        'action': 'noop',
        'action_index': 0,
        'reasoning': 'New application onboarding detected',
        'source': 'onboarding_policy',
        'skip_rl': True  # Do NOT call RL for onboarding
    }
```

### Step 4: Add Onboarding Explanation

**File:** `agent_runtime.py` (MODIFY `_explain` method)

**Purpose:** Generate human-readable explanation for onboarding NOOP

**Output:**
```
"New application 'backend-service' onboarded to dev environment.
Monitoring initialized. No action required (onboarding policy)."
```

### Step 5: Add Proof Logging

**File:** `core/proof_logger.py` (ADD new ProofEvents)

**Events:**
- `TEXT_INPUT_RECEIVED` - Text input captured
- `ONBOARDING_PARSED` - Text parsed to structured data
- `ONBOARDING_NOOP_FORCED` - NOOP decision forced for onboarding

---

## DETAILED CODE CHANGES

### Change 1: Text Input Parser

**File:** `core/text_input_onboarding.py` (NEW)

```python
#!/usr/bin/env python3
"""
Text Input Onboarding - Demo-Level Parser
Converts simple text to structured app data
NO NLP, NO ML - Simple keyword matching only
"""

import re
from typing import Dict, Any
from datetime import datetime


class TextInputOnboarder:
    """Demo-level text input onboarding"""
    
    # Simple keyword mapping (demo logic only)
    KEYWORDS = {
        'backend': 'backend',
        'api': 'backend',
        'service': 'backend',
        'server': 'backend',
        'frontend': 'frontend',
        'ui': 'frontend',
        'web': 'frontend',
        'app': 'fullstack',
        'application': 'fullstack'
    }
    
    def parse_text_input(self, text_input: str) -> Dict[str, Any]:
        """
        Parse free text into structured onboarding data
        
        Demo-level logic:
        - Extract keywords
        - Infer runtime type
        - Generate safe app name
        - Default to 'dev' environment
        
        Args:
            text_input: Free text like "This is my backend service"
            
        Returns:
            Structured onboarding event
        """
        
        # Normalize input
        text_lower = text_input.lower().strip()
        
        # Extract runtime type from keywords
        runtime_type = self._detect_runtime_type(text_lower)
        
        # Generate safe app name from text
        app_name = self._generate_app_name(text_input, runtime_type)
        
        # Build structured event
        onboarding_event = {
            'event_type': 'app_onboarding',
            'event_id': f'onboard-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'app_name': app_name,
            'env': 'dev',  # Always dev for demo onboarding
            'state': 'newly_onboarded',
            'runtime_type': runtime_type,
            'original_input': text_input[:100],  # Truncate for logging
            'source': 'text_input_onboarding'
        }
        
        return onboarding_event
    
    def _detect_runtime_type(self, text: str) -> str:
        """
        Detect runtime type from keywords
        
        Args:
            text: Normalized text input
            
        Returns:
            Runtime type: 'backend', 'frontend', or 'fullstack'
        """
        words = re.findall(r'\w+', text)
        
        for word in words:
            if word in self.KEYWORDS:
                return self.KEYWORDS[word]
        
        # Default if no keywords found
        return 'backend'
    
    def _generate_app_name(self, text: str, runtime_type: str) -> str:
        """
        Generate safe app name from text
        
        Logic:
        - Extract meaningful words
        - Combine with runtime type
        - Ensure lowercase alphanumeric with hyphens
        
        Args:
            text: Original text input
            runtime_type: Detected runtime type
            
        Returns:
            Safe app name (e.g., 'backend-service')
        """
        # Extract words (alphanumeric only)
        words = re.findall(r'\w+', text.lower())
        
        # Filter out common filler words
        filler_words = {'this', 'is', 'my', 'the', 'a', 'an', 'for', 'to', 'of'}
        meaningful_words = [w for w in words if w not in filler_words and len(w) > 2]
        
        if meaningful_words:
            # Take first meaningful word
            base_name = meaningful_words[0]
        else:
            # Fallback
            base_name = 'app'
        
        # Combine with runtime type
        app_name = f"{runtime_type}-{base_name}"
        
        # Ensure valid format (lowercase alphanumeric with hyphens)
        app_name = re.sub(r'[^a-z0-9-]', '', app_name)
        app_name = re.sub(r'-+', '-', app_name)  # No double hyphens
        app_name = app_name.strip('-')  # No leading/trailing hyphens
        
        # Truncate to max 50 chars
        return app_name[:50]


def onboard_from_text(text_input: str) -> Dict[str, Any]:
    """
    Quick interface for text input onboarding
    
    Args:
        text_input: Free text input
        
    Returns:
        Structured onboarding event
    """
    onboarder = TextInputOnboarder()
    return onboarder.parse_text_input(text_input)
```

### Change 2: Agent Runtime Decision Logic Modification

**File:** `agent_runtime.py`

**Location:** `_decide()` method (around line 401-680)

**ADD THIS CHECK at the beginning of `_decide()` method:**

```python
def _decide(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
    """DECIDE: Make decision using memory-influenced logic."""
    
    # ============================================================
    # ONBOARDING POLICY: Force NOOP for newly onboarded apps
    # ============================================================
    if validated_data.get('state') == 'newly_onboarded':
        app_name = validated_data.get('app_name', 'unknown')
        env = validated_data.get('env', 'dev')
        
        # Log onboarding detection
        self.logger.info(f"🆕 Onboarding detected: {app_name} in {env}")
        
        # FORCE NOOP - No RL decision for onboarding
        decision = {
            'action': 'noop',
            'action_index': 0,
            'reasoning': f"New application '{app_name}' onboarding policy",
            'explanation': f"New application '{app_name}' onboarded to {env}. Monitoring initialized. No action required.",
            'source': 'onboarding_policy',
            'skip_rl': True,  # Do NOT call RL
            'app_name': app_name,
            'env': env,
            'state': 'newly_onboarded',
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Log proof of NOOP decision
        if hasattr(self, 'proof_logger'):
            try:
                from core.proof_logger import ProofEvents, write_proof
                write_proof(ProofEvents.ONBOARDING_NOOP_FORCED, {
                    'app_name': app_name,
                    'env': env,
                    'decision': 'noop',
                    'reason': 'Onboarding policy - no action on new applications'
                })
            except:
                pass
        
        return decision
    
    # ============================================================
    # CONTINUE WITH NORMAL DECISION LOGIC
    # ============================================================
    # ... (rest of existing _decide() logic)
```

### Change 3: Add Proof Logging Events

**File:** `core/proof_logger.py`

**ADD to ProofEvents enum:**

```python
class ProofEvents(str, Enum):
    # ... existing events ...
    
    # Onboarding events
    TEXT_INPUT_RECEIVED = "text_input_received"
    ONBOARDING_PARSED = "onboarding_parsed" 
    ONBOARDING_NOOP_FORCED = "onboarding_noop_forced"
```

### Change 4: Create Simple API Endpoint (Optional)

**File:** `api/text_onboarding_endpoint.py` (NEW)

```python
#!/usr/bin/env python3
"""
Text Input Onboarding API Endpoint
Demo endpoint for text-based app onboarding
"""

from flask import Blueprint, request, jsonify
from core.text_input_onboarding import onboard_from_text
from core.proof_logger import write_proof, ProofEvents

text_onboarding_bp = Blueprint('text_onboarding', __name__)


@text_onboarding_bp.route('/api/onboard/text', methods=['POST'])
def onboard_text():
    """
    Onboard application from text input
    
    Request Body:
        {
            "text": "This is my backend service"
        }
        
    Response:
        {
            "success": true,
            "app_name": "backend-service",
            "env": "dev",
            "message": "Application onboarded successfully. Monitoring initialized."
        }
    """
    try:
        data = request.get_json()
        text_input = data.get('text', '').strip()
        
        if not text_input:
            return jsonify({
                'success': False,
                'error': 'Text input required'
            }), 400
        
        # Log text input received
        write_proof(ProofEvents.TEXT_INPUT_RECEIVED, {
            'text': text_input[:100],
            'source': 'api'
        })
        
        # Parse text to structured data
        onboarding_event = onboard_from_text(text_input)
        
        # Log parsed result
        write_proof(ProofEvents.ONBOARDING_PARSED, {
            'app_name': onboarding_event['app_name'],
            'runtime_type': onboarding_event['runtime_type'],
            'env': onboarding_event['env']
        })
        
        # Return success response
        return jsonify({
            'success': True,
            'app_name': onboarding_event['app_name'],
            'env': onboarding_event['env'],
            'runtime_type': onboarding_event['runtime_type'],
            'state': onboarding_event['state'],
            'message': f"Application '{onboarding_event['app_name']}' onboarded successfully. Monitoring initialized.",
            'expected_behavior': 'Observation → NOOP → Explanation',
            'onboarding_event': onboarding_event
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## VERIFICATION CHECKLIST

### ✅ Requirements Verification

- [ ] **Accepts ONE text input** - Simple string like "This is my backend service"
- [ ] **Converts to structured data** - app_name, env, state='newly_onboarded'
- [ ] **Passes into agent runtime** - Via perception or direct decision
- [ ] **FIRST behavior is Observation → NOOP → Explain** - Forced NOOP, no actions
- [ ] **Agent does NOT take action** - No restart, scale, etc.
- [ ] **Agent logs WHY it did nothing** - Clear explanation in logs
- [ ] **No RL decision for onboarding** - skip_rl=True prevents RL call
- [ ] **No NLP/ML** - Simple keyword matching only
- [ ] **Simple and readable** - Reviewer-friendly code

### ✅ Demo Testing

```python
# Test 1: Backend service
text = "This is my backend service"
result = onboard_from_text(text)
assert result['app_name'] == 'backend-service'
assert result['runtime_type'] == 'backend'
assert result['env'] == 'dev'
assert result['state'] == 'newly_onboarded'

# Test 2: Frontend app
text = "my frontend ui"
result = onboard_from_text(text)
assert result['runtime_type'] == 'frontend'

# Test 3: Agent runtime behavior
# Feed onboarding_event to agent
# Verify: decision['action'] == 'noop'
# Verify: decision['source'] == 'onboarding_policy'
# Verify: decision['skip_rl'] == True
```

### ✅ Logging Verification

Expected log output:
```
🆕 Onboarding detected: backend-service in dev
TEXT_INPUT_RECEIVED: {"text": "This is my backend service"}
ONBOARDING_PARSED: {"app_name": "backend-service", "runtime_type": "backend"}
ONBOARDING_NOOP_FORCED: {"decision": "noop", "reason": "Onboarding policy"}
DECISION: NOOP (onboarding_policy)
EXPLANATION: "New application 'backend-service' onboarded to dev. Monitoring initialized. No action required."
```

---

## WHY THIS APPROACH IS CORRECT

1. **Demo Simplicity:** No complex NLP, just keyword matching
2. **Safety First:** Always NOOP for new apps
3. **Deterministic:** Same input → same output
4. **No RL Pollution:** Onboarding doesn't pollute RL training data
5. **Clear Separation:** Onboarding policy separate from operational decisions
6. **Reviewer Friendly:** Easy to understand and verify
7. **Production Path:** Can later replace with real NLP if needed

---

## SUMMARY

**Files to Create:**
1. `core/text_input_onboarding.py` - Text parser
2. `api/text_onboarding_endpoint.py` - API endpoint (optional)

**Files to Modify:**
1. `agent_runtime.py` - Add onboarding NOOP policy in `_decide()`
2. `core/proof_logger.py` - Add onboarding proof events

**Expected Demo Flow:**
```
User Input: "This is my backend service"
     ↓
Parser: {app_name: 'backend-service', state: 'newly_onboarded'}
     ↓
Agent Runtime SENSE: Detects new app
     ↓
Agent Runtime DECIDE: Forces NOOP (no RL call)
     ↓
Agent Runtime ACT: Execute NOOP
     ↓
Agent Runtime EXPLAIN: "New application onboarded. Monitoring initialized. No action required."
```

**Status:** Ready for implementation ✅
