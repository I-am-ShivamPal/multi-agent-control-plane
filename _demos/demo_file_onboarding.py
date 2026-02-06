#!/usr/bin/env python3
"""
Demo: File-Based Onboarding Perception
Demonstrates autonomous onboarding perception from watched file.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.perception_adapters import OnboardingInputAdapter


def demo_file_based_onboarding():
    """Demo: File-based onboarding perception."""
    print("="*70)
    print("FILE-BASED ONBOARDING PERCEPTION DEMO")
    print("="*70)
    print()
    
    # Clean up any existing file
    watch_file = "onboarding_requests.jsonl"
    if Path(watch_file).exists():
        os.remove(watch_file)
    
    # Create adapter
    adapter = OnboardingInputAdapter(watch_file=watch_file)
    
    print(f"[1] Created file watcher for: {watch_file}")
    print(f"    File created: {Path(watch_file).exists()}")
    print()
    
    # Simulate adding onboarding requests to file
    print("[2] Simulating onboarding requests arriving...")
    
    requests = [
        {"app_id": "billing-service", "description": "handles invoices", "env": "prod"},
        {"app_id": "search-service", "description": "handles queries", "env": "stage"},
        {"app_id": "auth-service", "description": "handles authentication", "env": "prod"}
    ]
    
    # Write requests to file (simulates external system/user adding them)
    with open(watch_file, 'w', encoding='utf-8') as f:
        for req in requests:
            f.write(json.dumps(req) + '\n')
            print(f"    Added: {req['app_id']}")
    
    print(f"    Total requests written to file: {len(requests)}")
    print()
    
    # First perception (should detect all 3)
    print("[3] Perception Loop 1: Detecting new entries...")
    perceptions = adapter.perceive()
    
    print(f"    Perceptions detected: {len(perceptions)}")
    for i, p in enumerate(perceptions, 1):
        print(f"    {i}. Type: {p.type}, Source: {p.source}, App: {p.data['app_id']}")
    print(f"    Processed count: {adapter.get_processed_count()}")
    print()
    
    # Second perception (should detect nothing - already processed)
    print("[4] Perception Loop 2: Checking for new entries...")
    perceptions = adapter.perceive()
    
    print(f"    Perceptions detected: {len(perceptions)}")
    print(f"    (No new entries - already processed)")
    print(f"    Processed count: {adapter.get_processed_count()}")
    print()
    
    # Add a new request while agent is running
    print("[5] Simulating new request arriving during runtime...")
    new_request = {"app_id": "notification-service", "description": "handles notifications"}
    adapter.add_onboarding_request(new_request)
    print(f"    Added: {new_request['app_id']}")
    print()
    
    # Third perception (should detect the new one)
    print("[6] Perception Loop 3: Detecting newly arrived entry...")
    perceptions = adapter.perceive()
    
    print(f"    Perceptions detected: {len(perceptions)}")
    for i, p in enumerate(perceptions, 1):
        print(f"    {i}. Type: {p.type}, Source: {p.source}, App: {p.data['app_id']}")
    print(f"    Processed count: {adapter.get_processed_count()}")
    print()
    
    # Show file contents
    print("[7] Final file contents:")
    with open(watch_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        print(f"    Line {i}: {line.strip()}")
    print()
    
    print("RESULT: File-based onboarding perception working!")
    print("  - Agent polls file every loop")
    print("  - Only new entries are detected")
    print("  - Processed entries are tracked")
    print("  - Source logged as 'file_watcher'")
    print()


def demo_invalid_entries():
    """Demo: Handling invalid JSON entries."""
    print("="*70)
    print("INVALID ENTRY HANDLING DEMO")
    print("="*70)
    print()
    
    watch_file = "onboarding_test_invalid.jsonl"
    if Path(watch_file).exists():
        os.remove(watch_file)
    
    adapter = OnboardingInputAdapter(watch_file=watch_file)
    
    print("[1] Writing mixed valid/invalid entries...")
    
    # Write mixed entries
    with open(watch_file, 'w', encoding='utf-8') as f:
        f.write('{"app_id": "valid-service", "description": "valid entry"}\n')
        f.write('invalid json line\n')  # Invalid JSON
        f.write('{"description": "missing app_id"}\n')  # Missing required field
        f.write('{"app_id": "another-valid", "description": "also valid"}\n')
        f.write('\n')  # Empty line
    
    print("    Line 1: Valid entry")
    print("    Line 2: Invalid JSON (should skip with warning)")
    print("    Line 3: Missing app_id (should skip with warning)")
    print("    Line 4: Valid entry")
    print("    Line 5: Empty (should skip silently)")
    print()
    
    print("[2] Perceiving entries...")
    perceptions = adapter.perceive()
    
    print(f"    Valid perceptions: {len(perceptions)} (expected: 2)")
    for i, p in enumerate(perceptions, 1):
        print(f"    {i}. App: {p.data['app_id']}")
    print(f"    Total processed (including invalid): {adapter.get_processed_count()}")
    print()
    
    print("RESULT: Invalid entries handled gracefully!")
    print("  - Invalid JSON skipped with warning")
    print("  - Missing required fields skipped with warning")
    print("  - Empty lines skipped silently")
    print("  - Valid entries processed normally")
    print()
    
    # Cleanup
    os.remove(watch_file)


def main():
    """Run all demonstrations."""
    demo_file_based_onboarding()
    print("\n")
    demo_invalid_entries()
    
    print("="*70)
    print("SUMMARY: FILE-BASED ONBOARDING PERCEPTION")
    print("="*70)
    print()
    print("Onboarding is now TRUE environmental perception:")
    print()
    print("  Before: Programmatic calls (adapter.add_onboarding_request())")
    print("  After:  File-based polling (onboarding_requests.jsonl)")
    print()
    print("How it works:")
    print("  1. External system/user writes to onboarding_requests.jsonl")
    print("  2. Agent polls file every loop")
    print("  3. New entries detected and converted to perceptions")
    print("  4. Processed entries tracked (won't re-process)")
    print("  5. Logged with source='file_watcher'")
    print()
    print("File format (JSONL):")
    print('  {"app_id": "service-name", "description": "what it does"}')
    print()
    print("PERCEPTION IS NOW AUTONOMOUS!")
    print()


if __name__ == "__main__":
    main()
