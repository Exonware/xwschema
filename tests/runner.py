#!/usr/bin/env python3
"""
#exonware/xwschema/tests/runner.py
Main test runner for xwschema - Production Excellence Edition
Orchestrates all test layer runners with Markdown output logging.
Company: eXonware.com
Author: eXonware Backend Team
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
    - File: docs/logs/tests/TEST_<timestamp>_SUMMARY.md (Markdown-friendly format)
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
from exonware.xwsystem.utils.test_runner import (
    DualOutput,
    format_path,
    print_header,
    print_section,
    print_status,
    timestamp_for_filename,
)


def run_sub_runner(runner_path: Path, description: str, output: DualOutput) -> int:
    """Run a sub-runner and return exit code."""
    separator = "="*80
    output.print(separator, f"\n## {description}\n", emoji='📂')
    output.print(f"Starting: {description}", f"**Status:** Running...", emoji='▶️')
    output.print(f"Runner Path: {format_path(runner_path)}", f"**Runner Path:** `{format_path(runner_path)}`", emoji='📍')
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
        output.print(result.stderr, f"**Errors:**\n```\n{result.stderr}\n```")
    # Status
    if result.returncode == 0:
        output.print(f"{description} PASSED", f"\n**Result:** ✅ PASSED", emoji='✅')
    else:
        output.print(f"{description} FAILED", f"\n**Result:** ❌ FAILED", emoji='❌')
    return result.returncode


def main():
    """Main test runner function following GUIDE_TEST.md."""
    # Setup output logger
    test_dir = Path(__file__).parent
    reports_dir = test_dir.parent / "docs" / "logs" / "tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = timestamp_for_filename()
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
                emoji='📂')
    output.print(f"Output File: {format_path(output_file)}",
                f"**Output File:** `{format_path(output_file)}`",
                emoji='📝')
    output.print(f"Source Path: {format_path(src_path)}",
                f"**Source Path:** `{format_path(src_path)}`",
                emoji='🔧')
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
            output.print(msg, f"\n> ⚠️ {msg}", emoji='⚠️')
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
            output.print(msg, f"\n> ⚠️ {msg}", emoji='⚠️')
    else:
        # Run all tests in sequence
        print_section("Running All Test Layers", output)
        output.print("Execution Order: 0.core → 1.unit → 2.integration → 3.advance", 
                    "**Execution Order:** 0.core → 1.unit → 2.integration → 3.advance",
                    emoji='🚀')
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
    output.print(f"Total Layers: {total_runs}", f"- **Total Layers:** {total_runs}")
    output.print(f"Passed: {passed}", f"- **Passed:** {passed} ✅", emoji='✅')
    output.print(f"Failed: {failed}", f"- **Failed:** {failed} {'❌' if failed > 0 else ''}", 
                emoji='❌' if failed > 0 else 'ℹ️')
    # Final status using reusable utility
    all_passed = all(code == 0 for code in exit_codes)
    print_status(all_passed, "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED", output)
    # Save output
    output.save({
        'library': 'xwschema',
        'layer': 'main',
        'description': 'Main Orchestrator - Hierarchical Test Execution'
    })
    output.print(f"\nTest results saved to: {format_path(output_file)}", 
                f"\n**Results saved to:** `{format_path(output_file)}`",
                emoji='💾')
    sys.exit(0 if all_passed else 1)
if __name__ == "__main__":
    main()
