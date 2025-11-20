"""
pytest configuration for xSchema performance tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import available xSchema versions
schema_versions = {}

try:
    from src.xlib.xschema.legacy.facade import xSchema as LegacySchema
    schema_versions['legacy'] = LegacySchema
except ImportError:
    pass

try:
    from src.xlib.xschema.new.facade import xSchema as NewSchema
    schema_versions['new'] = NewSchema
except ImportError:
    pass

try:
    from src.xlib.xschema.new_2.facade import xSchema as New2Schema
    schema_versions['new_2'] = New2Schema
except ImportError:
    pass

try:
    from src.xlib.xschema.new_3.facade import xSchema as New3Schema
    schema_versions['new_3'] = New3Schema
except ImportError:
    pass


@pytest.fixture(scope="session")
def all_schema_versions():
    """Get all available schema versions."""
    return schema_versions


@pytest.fixture(scope="session")
def current_schema_version():
    """Get the current schema version."""
    try:
        from src.xlib.xschema import __version__
        return __version__
    except ImportError:
        return "unknown"


@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture."""
    import psutil
    return psutil.Process()


@pytest.fixture
def simple_schema():
    """Simple schema for performance tests."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"}
        },
        "required": ["name", "age"]
    }


@pytest.fixture
def simple_data():
    """Simple data for performance tests."""
    return {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }


@pytest.fixture
def complex_schema():
    """Complex schema for performance tests."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"}
                }
            },
            "contacts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "value": {"type": "string"}
                    }
                }
            }
        }
    }


@pytest.fixture
def complex_data():
    """Complex data for performance tests."""
    return {
        "id": 1,
        "name": "Jane Smith",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        },
        "contacts": [
            {"type": "email", "value": "jane@example.com"},
            {"type": "phone", "value": "555-1234"}
        ]
    }


def generate_large_schema(size: int):
    """Generate a large schema with specified number of properties."""
    schema = {
        "type": "object",
        "properties": {}
    }
    
    for i in range(size):
        schema["properties"][f"field_{i}"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        }
    
    return schema


def generate_large_data(size: int):
    """Generate large data matching the schema."""
    data = {}
    for i in range(size):
        data[f"field_{i}"] = f"value_{i}"
    
    return data
