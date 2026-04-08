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
import os
from pathlib import Path
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding

def _package_root() -> Path:
    """Folder with pyproject.toml + src/ (any tests/**/runner.py depth)."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / "pyproject.toml").is_file() and (p / "src").is_dir():
            return p
        p = p.parent
    raise RuntimeError("Could not locate package root from " + str(Path(__file__)))


_PKG_ROOT = _package_root()

from exonware.xwsystem.utils.test_runner import TestRunner

if __name__ == "__main__":
    os.chdir(_PKG_ROOT)
    runner = TestRunner(
        library_name="xwschema",
        layer_name="2.integration",
        description="Integration Tests - End-to-End Scenario Tests",
        test_dir=Path(__file__).parent,
        pytest_cwd=_PKG_ROOT,
        markers=["xwschema_integration"]
    )
    sys.exit(runner.run())
