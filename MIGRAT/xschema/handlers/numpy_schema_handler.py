"""
NumPy Schema Handler for xSchema framework.
Handles schemas for NumPy arrays based on their dtype and shape.
"""

import json
import logging
from typing import Any, Dict, Union, Optional

try:
    import numpy as np
except ImportError:
    np = None

from src.xlib.xdata.core.base_handler import aBaseHandler
from src.xlib.xschema.legacy.schema_handler import aSchemaHandler
from src.xlib.xdata.core.exceptions import ParsingError, ValidationError, ConfigurationError

logger = logging.getLogger(__name__)


class NumPyBaseHandler(aBaseHandler):
    """Provides common functionality for all NumPy-based handlers."""
    
    title = "NumPy"
    description = "A handler for NumPy arrays and their schemas."
    main_extension = "npy"
    all_extensions = ["npy", "npz"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not np:
            raise ConfigurationError(
                "The 'numpy' library is not installed. Please install it to use NumPy handlers."
            )

    @staticmethod
    def supports_feature(feature: str) -> bool:
        """Declare unsupported features."""
        # NumPy format is binary and does not support these features
        if feature in [
            "comments",
            "streaming",
            "human_readable",
            "reference_handling",
        ]:
            return False
        # It's excellent for round-tripping numerical data
        if feature in ["round_trip", "schema_validation", "binary_data"]:
            return True
        return False


class MockXSchema:
    """A simple mock xSchema class for testing purposes."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native dictionary format."""
        return self._data
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self._data, indent=indent)


class NumPySchemaHandler(NumPyBaseHandler, aSchemaHandler):
    """
    Handler for NumPy schemas, which are defined by an array's dtype and shape.
    """

    title = "NumPy Schema"
    description = (
        "Defines a schema for a NumPy array based on its dtype and shape."
    )
    main_extension = "json"  # Schemas are represented as JSON
    all_extensions = ["json"]
    format_category = "schema"
    detection_priority = 50

    @staticmethod
    def parse_schema(schema_content: Union[str, bytes, Dict], **kwargs) -> MockXSchema:
        """Parses a NumPy schema definition (JSON) into an xSchema object."""
        try:
            if isinstance(schema_content, (str, bytes)):
                # Parse JSON string/bytes to dict
                if isinstance(schema_content, bytes):
                    schema_content = schema_content.decode('utf-8')
                schema_dict = json.loads(schema_content)
            else:
                schema_dict = schema_content
            
            # Create mock xSchema with the schema data
            return MockXSchema(schema_dict)
        except Exception as e:
            raise ParsingError(f"Failed to parse NumPy schema: {e}") from e

    @staticmethod
    def serialize_schema(schema: MockXSchema, **kwargs) -> str:
        """Serializes an xSchema object into a JSON string for a NumPy schema."""
        return schema.to_json(indent=kwargs.get("indent"))

    @staticmethod
    def validate_data(data: Any, schema: MockXSchema, **kwargs) -> bool:
        """Validates that a NumPy array conforms to the specified schema (dtype and shape)."""
        if not isinstance(data, np.ndarray):
            raise ValidationError("Data to be validated must be a NumPy array.")

        schema_dict = schema.to_native()
        properties = schema_dict.get("properties", {})
        
        # Validate shape
        expected_shape = properties.get("shape", {}).get("const")
        if expected_shape is not None and data.shape != tuple(expected_shape):
            raise ValidationError(
                f"Shape mismatch: expected {expected_shape}, got {data.shape}"
            )

        # Validate dtype
        expected_dtype = properties.get("dtype", {}).get("const")
        if expected_dtype is not None and str(data.dtype) != expected_dtype:
            raise ValidationError(
                f"Dtype mismatch: expected {expected_dtype}, got {data.dtype}"
            )
        
        return True

    @staticmethod
    def generate_schema(data: Any, **kwargs) -> MockXSchema:
        """Generates a schema from a NumPy array or a dictionary of arrays."""
        if isinstance(data, np.ndarray):
            schema_data = {
                "type": "object",
                "properties": {
                    "shape": {"type": "array", "const": data.shape},
                    "dtype": {"type": "string", "const": str(data.dtype)},
                },
            }
            return MockXSchema(schema_data)
        
        if isinstance(data, dict):  # For NPZ files
            props = {}
            for key, array in data.items():
                if isinstance(array, np.ndarray):
                    props[key] = {
                        "type": "object",
                        "properties": {
                            "shape": {"type": "array", "const": list(array.shape)},
                            "dtype": {"type": "string", "const": str(array.dtype)},
                        },
                    }
            schema_data = {"type": "object", "properties": props}
            return MockXSchema(schema_data)
        
        raise ParsingError("Schema generation is only supported for NumPy arrays or dicts of arrays.")

    @staticmethod
    def can_handle_schema(schema_content: Union[str, bytes]) -> bool:
        """Determines if the content is a plausible NumPy schema (JSON with 'dtype' or 'shape')."""
        content_str = (
            schema_content.decode("utf-8")
            if isinstance(schema_content, bytes)
            else str(schema_content)
        )
        return '"dtype"' in content_str and '"shape"' in content_str

    # --- Base Handler Interface Implementation ---

    @staticmethod
    def parse(content: Union[str, bytes], **kwargs: Any) -> MockXSchema:
        """Parse schema content into an xSchema object."""
        return NumPySchemaHandler.parse_schema(content, **kwargs)

    @staticmethod
    def serialize(data: MockXSchema, **kwargs: Any) -> str:
        """Serialize an xSchema object to string."""
        return NumPySchemaHandler.serialize_schema(data, **kwargs)

    @staticmethod
    def can_handle(content: Union[str, bytes]) -> bool:
        """Check if content can be handled by this schema handler."""
        return NumPySchemaHandler.can_handle_schema(content)

    @staticmethod
    def is_binary_format() -> bool:
        """NumPy schemas are JSON, so they're text-based."""
        return False

    @staticmethod
    def is_binary_schema() -> bool:
        """NumPy schemas are JSON, so they're text-based."""
        return False
