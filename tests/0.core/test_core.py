"""
Core functionality tests for xwschema

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025
"""

import pytest
# from exonware.xwschema import YourMainClass  # Uncomment and modify as needed

@pytest.mark.xwschema_core
class TestCore:
    """Test core functionality."""
    
    def test_import(self):
        """Test that the library can be imported."""
        try:
            from exonware import xwschema
            assert True
        except ImportError:
            pytest.fail("Could not import exonware.xwschema")
    
    def test_convenience_import(self):
        """Test that the convenience import works."""
        try:
            from exonware.xwschema import XWSchema
            assert True
        except ImportError:
            pytest.fail("Could not import XWSchema")
    
    def test_version_info(self):
        """Test that version information is available."""
        from exonware import xwschema
        
        assert hasattr(xwschema, '__version__')
        assert hasattr(xwschema, '__author__')
        assert hasattr(xwschema, '__email__')
        assert hasattr(xwschema, '__company__')
        
        # Verify values are strings
        assert isinstance(xwschema.__version__, str)
        assert isinstance(xwschema.__author__, str)
        assert isinstance(xwschema.__email__, str)
        assert isinstance(xwschema.__company__, str)
    
    def test_sample_functionality(self, sample_data):
        """Sample test using fixture data."""
        # Replace this with actual tests for your library
        assert sample_data["test_data"] == "sample"
        assert len(sample_data["numbers"]) == 5
        assert sample_data["nested"]["key"] == "value"
