#!/usr/bin/env python3
"""
#exonware/xwschema/tests/runner.py

Main test runner for xwschema - Production Excellence Edition
Orchestrates all test layer runners with Markdown output logging.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025

Usage:
    python tests/runner.py                # Run all tests
    python tests/runner.py --core         # Run only core tests
    python tests/runner.py --unit         # Run only unit tests
    python tests/runner.py --integration  # Run only integration tests
    python tests/runner.py --advance      # Run only advance tests (v1.0.0+)
    python tests/runner.py --security     # Run only security tests
    python tests/runner.py --performance  # Run only performance tests

Output:
    - Terminal: Colored, formatted output with emojis
    - File: docs/tests/TEST_<timestamp>_SUMMARY.md (Markdown-friendly format)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding

# Try to import reusable utilities from xwsystem
try:
    from exonware.xwsystem.utils.test_runner import (
        DualOutput,
        format_path,
        print_header,
        print_section,
        print_status
    )
    USE_XWSYSTEM_UTILS = True
except ImportError:
    USE_XWSYSTEM_UTILS = False
    # Fallback implementations if xwsystem not available
    class DualOutput:
        """Fallback DualOutput without colors."""
        def __init__(self, output_file: Path):
            self.output_file = output_file
            self.markdown_lines = []
        
        def print(self, text: str, markdown_format: str = None, color: str = None, emoji: str = None):
            display_text = f"{emoji} {text}" if emoji else text
            print(display_text)
            if markdown_format:
                self.markdown_lines.append(markdown_format)
            else:
                cleaned = text.replace("="*80, "---")
                if emoji:
                    cleaned = f"{emoji} {cleaned}"
                self.markdown_lines.append(cleaned)
        
        def save(self, header_info: dict = None):
            header = f"""# Test Runner Output

**Library:** xwschema  
**Generated:** {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}  
**Runner:** Main Orchestrator

---

"""
            content = header + "\n".join(self.markdown_lines) + "\n"
            self.output_file.write_text(content, encoding='utf-8')
    
    def format_path(path: Path) -> str:
        return str(path.resolve())
    
    def print_header(title: str, output=None):
        print("=" * 80)
        print(f"🎯 {title}")
        print("=" * 80)
    
    def print_section(title: str, output=None):
        print(f"\n📋 {title}")
    
    def print_status(success: bool, message: str, output=None):
        emoji = '✅' if success else '❌'
        print(f"{emoji} {message}")


def run_sub_runner(runner_path: Path, description: str, output: DualOutput) -> int:
    """Run a sub-runner and return exit code."""
    separator = "="*80
    output.print(separator, f"\n## {description}\n", emoji='📂')
    output.print(f"Starting: {description}", f"**Status:** Running...", color='info', emoji='▶️')
    output.print(f"Runner Path: {format_path(runner_path)}", f"**Runner Path:** `{format_path(runner_path)}`", color='info', emoji='📍')
    output.print(separator, "")
    
    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=runner_path.parent,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'  # Replace invalid chars instead of crashing
    )
    
    # Print sub-runner output
    if result.stdout:
        output.print(result.stdout, f"```\n{result.stdout}\n```")
    if result.stderr:
        output.print(result.stderr, f"**Errors:**\n```\n{result.stderr}\n```", color='error')
    
    # Status
    if result.returncode == 0:
        output.print(f"{description} PASSED", f"\n**Result:** ✅ PASSED", color='success', emoji='✅')
    else:
        output.print(f"{description} FAILED", f"\n**Result:** ❌ FAILED", color='error', emoji='❌')
    
    return result.returncode


def main():
    """Main test runner function following GUIDE_TEST.md."""
    # Setup output logger
    test_dir = Path(__file__).parent
    reports_dir = test_dir.parent / "docs" / "tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = reports_dir / f"TEST_{timestamp}_SUMMARY.md"
    output = DualOutput(output_file)
    
    # Add src to Python path for testing
    src_path = test_dir.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Header using reusable utility
    print_header("xwschema Test Runner - Production Excellence Edition", output)
    
    # Print paths
    output.print(f"Test Directory: {format_path(test_dir)}", 
                f"**Test Directory:** `{format_path(test_dir)}`",
                color='info', emoji='📂')
    output.print(f"Output File: {format_path(output_file)}",
                f"**Output File:** `{format_path(output_file)}`",
                color='info', emoji='📝')
    output.print(f"Source Path: {format_path(src_path)}",
                f"**Source Path:** `{format_path(src_path)}`",
                color='info', emoji='🔧')
    
    # Parse arguments
    args = sys.argv[1:]
    
    # Define sub-runners (support both old and new directory names)
    core_runner = test_dir / "0.core" / "runner.py"
    if not core_runner.exists():
        core_runner = test_dir / "core" / "runner.py"
    
    unit_runner = test_dir / "1.unit" / "runner.py"
    if not unit_runner.exists():
        unit_runner = test_dir / "unit" / "runner.py"
    
    integration_runner = test_dir / "2.integration" / "runner.py"
    if not integration_runner.exists():
        integration_runner = test_dir / "integration" / "runner.py"
    
    advance_runner = test_dir / "3.advance" / "runner.py"
    
    exit_codes = []
    
    # Determine which tests to run
    if "--core" in args:
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Core Tests", output))
    
    elif "--unit" in args:
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Unit Tests", output))
    
    elif "--integration" in args:
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Integration Tests", output))
    
    elif "--advance" in args:
        if advance_runner.exists():
            exit_codes.append(run_sub_runner(advance_runner, "Advance Tests", output))
        else:
            msg = "Advance tests not available (requires v1.0.0)"
            output.print(msg, f"\n> ⚠️ {msg}", color='warning', emoji='⚠️')
    
    elif "--security" in args or "--performance" in args or "--usability" in args or "--maintainability" in args or "--extensibility" in args:
        # Forward to advance runner if exists
        if advance_runner.exists():
            result = subprocess.run(
                [sys.executable, str(advance_runner)] + args,
                encoding='utf-8',
                errors='replace'
            )
            exit_codes.append(result.returncode)
        else:
            msg = "Advance tests not available (requires v1.0.0)"
            output.print(msg, f"\n> ⚠️ {msg}", color='warning', emoji='⚠️')
    
    else:
        # Run all tests in sequence
        print_section("Running All Test Layers", output)
        output.print("Execution Order: 0.core → 1.unit → 2.integration → 3.advance", 
                    "**Execution Order:** 0.core → 1.unit → 2.integration → 3.advance",
                    color='info', emoji='🚀')
        
        # Core tests
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Layer 0: Core Tests", output))
        
        # Unit tests
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Layer 1: Unit Tests", output))
        
        # Integration tests
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Layer 2: Integration Tests", output))
        
        # Advance tests (if available)
        if advance_runner.exists():
            exit_codes.append(run_sub_runner(advance_runner, "Layer 3: Advance Tests", output))
    
    # Print summary using reusable utility
    print_section("TEST EXECUTION SUMMARY", output)
    
    total_runs = len(exit_codes)
    passed = sum(1 for code in exit_codes if code == 0)
    failed = total_runs - passed
    
    output.print(f"Total Layers: {total_runs}", f"- **Total Layers:** {total_runs}", color='info')
    output.print(f"Passed: {passed}", f"- **Passed:** {passed} ✅", color='success', emoji='✅')
    output.print(f"Failed: {failed}", f"- **Failed:** {failed} {'❌' if failed > 0 else ''}", 
                color='error' if failed > 0 else 'info', emoji='❌' if failed > 0 else 'ℹ️')
    
    # Final status using reusable utility
    all_passed = all(code == 0 for code in exit_codes)
    print_status(all_passed, "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED", output)
    
    # Save output
    if USE_XWSYSTEM_UTILS:
        output.save({
            'library': 'xwschema',
            'layer': 'main',
            'description': 'Main Orchestrator - Hierarchical Test Execution'
        })
    else:
        output.save()
    
    output.print(f"\nTest results saved to: {format_path(output_file)}", 
                f"\n**Results saved to:** `{format_path(output_file)}`",
                color='info', emoji='💾')
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
