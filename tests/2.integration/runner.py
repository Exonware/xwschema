#!/usr/bin/env python3
"""
#exonware/xwschema/tests/2.integration/runner.py
Integration test runner for xwschema
Runs end-to-end scenario tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import sys
from pathlib import Path
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding
# Add src to Python path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwschema",
        layer_name="2.integration",
        description="Integration Tests - End-to-End Scenario Tests",
        test_dir=Path(__file__).parent,
        markers=["xwschema_integration"]
    )
    sys.exit(runner.run())
