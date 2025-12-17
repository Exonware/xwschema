#!/usr/bin/env python3
"""
#exonware/xwschema/tests/0.core/runner.py

Core test runner for xwschema
Auto-discovers and runs core tests with colored output and Markdown logging.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
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

# Try to import reusable utilities from xwsystem
try:
    from exonware.xwsystem.utils.test_runner import TestRunner
    USE_XWSYSTEM_UTILS = True
except ImportError:
    USE_XWSYSTEM_UTILS = False
    # Fallback implementation
    import subprocess
    from pathlib import Path
    
    class TestRunner:
        """Fallback TestRunner without xwsystem utilities."""
        def __init__(self, library_name: str, layer_name: str, description: str, test_dir: Path, markers: list[str] = None):
            self.library_name = library_name
            self.layer_name = layer_name
            self.description = description
            self.test_dir = test_dir
            self.markers = markers or []
        
        def run(self) -> int:
            """Run tests using pytest."""
            cmd = [sys.executable, "-m", "pytest", str(self.test_dir), "-v", "--tb=short", "-x"]
            if self.markers:
                cmd.extend(["-m", " or ".join(self.markers)])
            result = subprocess.run(cmd)
            return result.returncode

if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwschema",
        layer_name="0.core",
        description="Core Tests - Fast, High-Value Checks (20% tests for 80% value)",
        test_dir=Path(__file__).parent,
        markers=["xwschema_core"]
    )
    sys.exit(runner.run())

