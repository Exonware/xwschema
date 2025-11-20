"""
xSchema Core Tests Configuration
===============================

Common fixtures and configuration for xSchema core tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import all versions
try:
    from src.xlib.xschema import xSchema
    from src.xlib.xschema import __version__ as current_version
except ImportError as e:
    current_version = None

# Import individual versions for testing - handle each one separately
schema_versions = {}

# Try legacy version
try:
    from src.xlib.xschema.legacy.facade import xSchema as LegacySchema
    schema_versions['legacy'] = LegacySchema
except ImportError:
    pass

# Try new version
try:
    from src.xlib.xschema.new.facade import xSchema as NewSchema
    schema_versions['new'] = NewSchema
except ImportError:
    pass

# Try new_2 version
try:
    from src.xlib.xschema.new_2.facade import xSchema as New2Schema
    schema_versions['new_2'] = New2Schema
except ImportError:
    pass

# Try new_3 version
try:
    from src.xlib.xschema.new_3.facade import xSchema as New3Schema
    schema_versions['new_3'] = New3Schema
except ImportError:
    pass


@pytest.fixture(scope="session")
def all_schema_versions():
    """Get all available schema versions for testing."""
    return schema_versions


@pytest.fixture(scope="session")
def current_schema_version():
    """Get the current schema version."""
    return current_version


@pytest.fixture
def test_data_dir():
    """Get the test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_schema():
    """Sample JSON schema for testing."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "active": {"type": "boolean"},
            "profile": {
                "type": "object",
                "properties": {
                    "bio": {"type": "string"},
                    "location": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["id", "name", "email"]
    }


@pytest.fixture
def sample_data():
    """Sample data that should validate against the schema."""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "active": True,
        "profile": {
            "bio": "Software developer",
            "location": "San Francisco",
            "skills": ["Python", "JavaScript", "React"]
        }
    }


@pytest.fixture
def invalid_data():
    """Sample data that should fail validation."""
    return {
        "id": "not_an_integer",
        "name": 123,  # Should be string
        "email": "invalid_email",
        "age": -5,  # Below minimum
        "active": "not_boolean"
    }
