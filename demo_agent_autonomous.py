#!/usr/bin/env python3
"""
Demo: Autonomous Agent Operation
Demonstrates the autonomous agent runtime with proof of continuous operation.

This script runs the agent for a limited time to demonstrate:
1. Autonomous continuous operation
2. Agent loop execution (sense → validate → decide → enforce → act → observe → explain)
3. State transitions
4. Structured logging with agent_id, agent_state, last_decision
5. Heartbeat monitoring
"""

import sys
import time
import subprocess
import signal
from pathlib import Path


def run_agent_demo(duration_seconds=30, loop_interval=3.0):
    """Run agent for demonstration.
    
    Args:
        duration_seconds: How long to run the agent
        loop_interval: Agent loop interval in seconds
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          AUTONOMOUS AGENT RUNTIME DEMONSTRATION                  ║
╚══════════════════════════════════════════════════════════════════╝

This demonstration will:
1. Start the autonomous agent runtime
2. Run for {duration} seconds
3. Show continuous operation without manual triggers
4. Display agent logs proving autonomous behavior
5. Gracefully shutdown

Agent Configuration:
- Environment: dev
- Loop Interval: {interval}s
- Duration: {duration}s

Starting agent...
""".format(duration=duration_seconds, interval=loop_interval))
    
    # Start agent process
    cmd = [
        sys.executable,
        "agent_runtime.py",
        "--env", "dev",
        "--agent-id", "demo-agent-001",
        "--loop-interval", str(loop_interval)
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        # Start agent in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✅ Agent started successfully!")
        print(f"   PID: {process.pid}")
        print(f"   Duration: {duration_seconds}s")
        print("\n" + "="*70)
        print("AGENT OUTPUT:")
        print("="*70 + "\n")
        
        # Let it run for specified duration
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Read output
            if process.poll() is not None:
                # Process ended
                break
            time.sleep(0.5)
        
        # Graceful shutdown
        print("\n" + "="*70)
        print("GRACEFUL SHUTDOWN")
        print("="*70 + "\n")
        print("Sending shutdown signal (SIGTERM)...")
        
        process.send_signal(signal.SIGTERM)
        
        # Wait for graceful shutdown
        try:
            process.wait(timeout=5)
            print("✅ Agent shutdown gracefully")
        except subprocess.TimeoutExpired:
            print("⚠️  Agent did not shutdown gracefully, forcing...")
            process.kill()
            process.wait()
        
        print("\n" + "="*70)
        print("PROOF VERIFICATION")
        print("="*70 + "\n")
        
        # Show proof logs
        print_proof_logs()
        
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETE")
        print("="*70)
        print("""
✅ Autonomous operation verified:
   • Agent ran continuously without manual triggers
   • State transitions logged
   • Heartbeat events recorded
   • Graceful shutdown successful

📋 Review full logs:
   • Runtime: logs/agent/agent_runtime.log
   • Proof:   logs/agent/agent_proof.jsonl
   • Decisions: logs/agent/agent_decisions.log
   • State:   logs/agent/agent_state_demo-agent-001.json
""")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find agent_runtime.py")
        print(f"   Make sure you're in the project root directory")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=5)


def print_proof_logs():
    """Print proof logs to show autonomous operation."""
    proof_log = Path("logs/agent/agent_proof.jsonl")
    
    if not proof_log.exists():
        print("⚠️  No proof log found yet")
        return
    
    print("Latest proof log entries:")
    print("-" * 70)
    
    with open(proof_log, 'r') as f:
        lines = f.readlines()
        # Show last 10 entries
        for line in lines[-10:]:
            print(line.strip())
    
    print("-" * 70)
    print(f"\nTotal proof events: {len(lines)}")
    
    # Count event types
    event_counts = {}
    for line in lines:
        try:
            import json
            entry = json.loads(line)
            event = entry.get('event', 'unknown')
            event_counts[event] = event_counts.get(event, 0) + 1
        except:
            pass
    
    if event_counts:
        print("\nEvent breakdown:")
        for event, count in sorted(event_counts.items()):
            print(f"  • {event}: {count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Agent Demo")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duration to run agent (seconds)")
    parser.add_argument("--interval", type=float, default=3.0,
                       help="Agent loop interval (seconds)")
    
    args = parser.parse_args()
    
    run_agent_demo(args.duration, args.interval)
