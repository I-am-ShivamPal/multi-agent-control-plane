#!/usr/bin/env python3
"""
Repository Structure Verification Script
Validates that the repository consolidation was successful.
"""

import os
import sys
from pathlib import Path

def check_directory_exists(path, name):
    """Check if a directory exists."""
    if os.path.exists(path) and os.path.isdir(path):
        print(f"✅ {name}: EXISTS at {path}")
        return True
    else:
        print(f"❌ {name}: MISSING at {path}")
        return False

def check_directory_not_exists(path, name):
    """Check that a directory does NOT exist."""
    if not os.path.exists(path):
        print(f"✅ {name}: REMOVED (no longer exists)")
        return True
    else:
        print(f"❌ {name}: STILL EXISTS at {path}")
        return False

def check_file_exists(path, name):
    """Check if a file exists."""
    if os.path.exists(path) and os.path.isfile(path):
        print(f"✅ {name}: EXISTS")
        return True
    else:
        print(f"❌ {name}: MISSING")
        return False

def count_files_in_dir(path, pattern):
    """Count files matching a pattern in a directory."""
    if not os.path.exists(path):
        return 0
    return len(list(Path(path).glob(pattern)))

def main():
    print("=" * 70)
    print("REPOSITORY STRUCTURE VERIFICATION")
    print("=" * 70)
    print()
    
    repo_root = os.getcwd()
    results = []
    
    # 1. Check that duplicate folders are removed
    print("1. CHECKING DUPLICATE REMOVAL")
    print("-" * 70)
    results.append(check_directory_not_exists(
        "Multi-intelligent-agent",
        "Nested Multi-intelligent-agent folder"
    ))
    results.append(check_directory_not_exists(
        "ritesh-rl-api",
        "Separate ritesh-rl-api folder"
    ))
    print()
    
    # 2. Check RL API integration
    print("2. CHECKING RL API INTEGRATION")
    print("-" * 70)
    results.append(check_directory_exists(
        "core/rl",
        "core/rl directory"
    ))
    results.append(check_directory_exists(
        "core/rl/external_api",
        "Ritesh's RL API integration"
    ))
    results.append(check_file_exists(
        "core/rl/external_api/rl_decision_brain.py",
        "RL Decision Brain"
    ))
    results.append(check_file_exists(
        "core/rl/external_api/README.md",
        "RL API README"
    ))
    print()
    
    # 3. Check demo consolidation
    print("3. CHECKING DEMO CONSOLIDATION")
    print("-" * 70)
    results.append(check_directory_exists(
        "_demos",
        "_demos directory"
    ))
    
    demo_count = count_files_in_dir("_demos", "demo_*.py")
    root_demo_count = count_files_in_dir(".", "demo_*.py")
    
    print(f"   Demo files in _demos/: {demo_count}")
    print(f"   Demo files in root: {root_demo_count}")
    
    if root_demo_count == 0:
        print(f"✅ All demo files consolidated into _demos/")
        results.append(True)
    else:
        print(f"❌ Demo files still exist in root directory")
        results.append(False)
    
    results.append(check_file_exists(
        "_demos/README.md",
        "_demos/README.md"
    ))
    print()
    
    # 4. Check UI reorganization
    print("4. CHECKING UI REORGANIZATION")
    print("-" * 70)
    results.append(check_directory_exists(
        "ui",
        "ui directory"
    ))
    results.append(check_directory_exists(
        "ui/dashboards",
        "ui/dashboards (from dashboard/)"
    ))
    results.append(check_directory_exists(
        "ui/web",
        "ui/web"
    ))
    results.append(check_directory_exists(
        "ui/devops",
        "ui/devops (from devops-layer/)"
    ))
    
    # Check old directories are removed
    results.append(check_directory_not_exists(
        "dashboard",
        "Old dashboard/ directory"
    ))
    results.append(check_directory_not_exists(
        "devops-layer",
        "Old devops-layer/ directory"
    ))
    print()
    
    # 5. Check entry points
    print("5. CHECKING ENTRY POINTS")
    print("-" * 70)
    results.append(check_file_exists(
        "agent_runtime.py",
        "Primary entry point (agent_runtime.py)"
    ))
    results.append(check_file_exists(
        "main.py",
        "Legacy entry point (main.py)"
    ))
    results.append(check_file_exists(
        "_demos/demo_run.py",
        "Demo entry point (_demos/demo_run.py)"
    ))
    print()
    
    # 6. Check documentation
    print("6. CHECKING DOCUMENTATION")
    print("-" * 70)
    results.append(check_file_exists(
        "ENTRY_POINT.md",
        "Entry point documentation"
    ))
    results.append(check_file_exists(
        "STRUCTURE.md",
        "Structure documentation"
    ))
    results.append(check_file_exists(
        "README.md",
        "Main README"
    ))
    print()
    
    # 7. Check core directories
    print("7. CHECKING CORE DIRECTORIES")
    print("-" * 70)
    results.append(check_directory_exists("agents", "agents/"))
    results.append(check_directory_exists("core", "core/"))
    results.append(check_directory_exists("orchestrator", "orchestrator/"))
    results.append(check_directory_exists("api", "api/"))
    print()
    
    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    total_checks = len(results)
    passed_checks = sum(results)
    failed_checks = total_checks - passed_checks
    
    print(f"Total Checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {failed_checks}")
    print()
    
    if failed_checks == 0:
        print("🎉 SUCCESS! Repository consolidation is complete.")
        return 0
    else:
        print("⚠️  WARNING! Some checks failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
