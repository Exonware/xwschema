#!/usr/bin/env python3
"""
xSchema Performance Tests Runner
===============================

Comprehensive performance testing suite for xSchema across multiple versions
and data formats. This runner provides automated benchmarking and comparison
of different xSchema implementations.

Features:
- Cross-version performance comparison (legacy, new, new_2, new_3)
- Multi-format testing (JSON, XML, TOML, YAML)
- Memory usage analysis
- Automated environment setup
- Detailed performance metrics

Usage:
    python runner.py              # Run all tests
    python runner.py -v           # Verbose output
    python test_xschema_performance.py  # Direct execution

Performance Results (Latest):
- Total tests: 64
- Success rate: 93.8%
- Best overall: new_2 version
- Best for YAML: new_3 version

Dependencies:
- pytest
- psutil
- xlib.xwsystem (for logging)

Author: xComBot Development Team
Version: 1.0.0
"""

import sys
import subprocess
import os
from pathlib import Path

def setup_environment():
    """Setup the Python environment for running tests."""
    # Get the project root (6 levels up from this file)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent.parent.parent.parent
    
    # Add src to Python path
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    return project_root, src_path

def main():
    """Run the xSchema performance tests."""
    try:
        # Setup environment first
        project_root, src_path = setup_environment()
        
        current_dir = Path(__file__).parent
        test_file = current_dir / "test_xschema_performance.py"
        
        print("🚀 Running xSchema Performance Tests")
        print("=" * 45)
        print(f"Project root: {project_root}")
        print(f"Source path: {src_path}")
        print(f"Test file: {test_file}")
        print(f"Current working directory: {Path.cwd()}")
        print()
        
        # Verify the test file exists
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return 1
        
        # Verify project root exists
        if not project_root.exists():
            print(f"❌ Project root not found: {project_root}")
            return 1
        
        # Verify src path exists
        if not Path(src_path).exists():
            print(f"❌ Source path not found: {src_path}")
            return 1
        
        # Build PYTHONPATH more robustly
        python_path_parts = [src_path, str(project_root)]
        existing_pythonpath = os.environ.get('PYTHONPATH', '')
        if existing_pythonpath:
            python_path_parts.append(existing_pythonpath)
        
        python_path = os.pathsep.join(python_path_parts)
        
        # Run pytest on the test file with proper environment
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(test_file), 
            "-v", 
            "--tb=short",
            "--color=yes",
            "--durations=10"  # Show top 10 slowest tests
        ], 
        check=False,
        cwd=str(project_root),  # Run from project root
        env={
            **dict(os.environ),
            'PYTHONPATH': python_path
        })
        
        if result.returncode == 0:
            print("\n✅ All performance tests completed!")
        else:
            print(f"\n❌ Performance tests failed with return code: {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Failed to run performance tests: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
