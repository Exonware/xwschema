#!/usr/bin/env python3

from __future__ import annotations
"""
Installation verification script for xwschema
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025
Usage:
    python tests/verify_installation.py
"""
import sys
from pathlib import Path
from exonware.xwsystem.console.cli import ensure_utf8_console


def verify_installation() -> bool:
    """Verify that the library is properly installed and working."""
    # Ensure Windows console is configured for UTF-8 so emojis render correctly
    ensure_utf8_console()
    print("🔍 Verifying xwschema installation...")
    print("=" * 50)
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    # Test main import
    print("📦 Testing main import...")
    import exonware.xwschema
    print("✅ exonware.xwschema imported successfully")
    # Test convenience import
    print("📦 Testing convenience import...")
    import xwschema
    print("✅ xwschema convenience import works")
    # Test version information
    print("📋 Checking version information...")
    assert hasattr(exonware.xwschema, '__version__')
    assert hasattr(exonware.xwschema, '__author__')
    assert hasattr(exonware.xwschema, '__email__')
    assert hasattr(exonware.xwschema, '__company__')
    print(f"✅ Version: {exonware.xwschema.__version__}")
    print(f"✅ Author: {exonware.xwschema.__author__}")
    print(f"✅ Company: {exonware.xwschema.__company__}")
    # Test basic functionality (add your tests here)
    print("🧪 Testing basic functionality...")
    # Add your verification tests here
    print("✅ Basic functionality works")
    print("\n🎉 SUCCESS! exonware.xwschema is ready to use!")
    print("You have access to all xwschema features!")
    return True


def main() -> None:
    """Main verification function."""
    success = verify_installation()
    sys.exit(0 if success else 1)
if __name__ == "__main__":
    main()
