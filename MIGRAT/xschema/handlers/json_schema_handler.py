"""
JSON Schema Handler for xSchema framework.
Extracted from xData handlers for schema-specific operations.
"""

import json
import re
from typing import Any, Dict, Type, Union

from src.xlib.xdata.core.base_handler import aBaseHandler
from src.xlib.xschema.legacy.schema_handler import aSchemaHandler


def _map_python_type_to_json_schema(python_type: Type) -> str:
    """Map Python types to JSON Schema types."""
    type_mapping = {
        str: "string",
        int: "integer", 
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null"
    }
    return type_mapping.get(python_type, "string")


def _get_json_format_from_python_type(python_type: Type) -> str:
    """Get JSON format from Python type."""
    format_mapping = {
        str: "string",
        int: "integer",
        float: "number", 
        bool: "boolean"
    }
    return format_mapping.get(python_type, "string")


def _map_json_schema_to_python_type(json_type: str) -> Type:
    """Map JSON Schema types to Python types."""
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None)
    }
    return type_mapping.get(json_type, str)


class JSONBaseHandler(aBaseHandler):
    """Provides common functionality for all JSON-based handlers."""
    
    title = "JSON"
    description = "JavaScript Object Notation"
    main_extension = "json"
    all_extensions = ["json"]
    mime_types = ["application/json", "text/json"]
    
    @staticmethod
    def _is_plausible_json(content_str: str) -> bool:
        """Check if content looks like JSON."""
        content_str = content_str.strip()
        return (content_str.startswith('{') and content_str.endswith('}')) or \
               (content_str.startswith('[') and content_str.endswith(']'))
    
    @staticmethod
    def _parse_json_content(content: Union[str, bytes]) -> Dict[Any, Any]:
        """Parse JSON content."""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return json.loads(content)
    
    @staticmethod
    def _serialize_json_content(data: Dict[Any, Any], **kwargs: Any) -> str:
        """Serialize data to JSON."""
        return json.dumps(data, indent=2, sort_keys=True, **kwargs)
    
    @staticmethod
    def _convert_value_from_json(value: Any) -> Any:
        """Convert JSON value to Python value."""
        if isinstance(value, dict):
            return {k: JSONBaseHandler._convert_value_from_json(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [JSONBaseHandler._convert_value_from_json(v) for v in value]
        else:
            return value


class _JSONSchemaDraft7Worker:
    """Internal worker to handle JSON Schema Draft 7 validation and mapping."""
    
    DRAFT_7_META_SCHEMA = "http://json-schema.org/draft-07/schema#"
    
    @staticmethod
    def _map_json_type_to_xschema(json_type: str) -> str:
        """Map JSON Schema types to xSchema types."""
        type_mapping = {
            "string": "string",
            "integer": "integer", 
            "number": "number",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
            "null": "null"
        }
        return type_mapping.get(json_type, "string")
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse JSON Schema Draft 7 content."""
        try:
            schema = json.loads(content)
            
            # Ensure it has the correct meta-schema
            if '$schema' not in schema:
                schema['$schema'] = _JSONSchemaDraft7Worker.DRAFT_7_META_SCHEMA
                
            return schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize JSON Schema Draft 7."""
        # Ensure proper formatting
        if '$schema' not in schema:
            schema['$schema'] = _JSONSchemaDraft7Worker.DRAFT_7_META_SCHEMA
            
        return json.dumps(schema, indent=2, sort_keys=True)
    
    @staticmethod
    def validate(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate data against JSON Schema Draft 7."""
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return True
        except Exception:
            return False


class _JSONSchemaOpenAPIWorker:
    """Internal worker to handle OpenAPI JSON Schema validation and mapping."""
    
    OPENAPI_SCHEMA_FORMATS = ["openapi", "swagger"]
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse OpenAPI schema content."""
        try:
            schema = json.loads(content)
            
            # Extract the actual schema from OpenAPI structure
            if 'components' in schema and 'schemas' in schema['components']:
                # This is an OpenAPI 3.x document
                return schema['components']['schemas']
            elif 'definitions' in schema:
                # This is a Swagger 2.x document
                return schema['definitions']
            else:
                # Assume it's already a schema
                return schema
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid OpenAPI schema: {e}")
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize OpenAPI schema."""
        return json.dumps(schema, indent=2, sort_keys=True)


# --- Enhanced Schema Handler with Composite Pattern -------------------------

class JSONSchemaHandler(JSONBaseHandler, aSchemaHandler):
    """
    A composite schema handler for JSON.
    
    This handler acts as a dispatcher. It inspects the schema content to
    determine the specific JSON schema variant (Draft 7, OpenAPI, etc.) and then
    delegates the parsing and validation to an internal, specialized worker.
    """
    
    title = "JSON Schema (Composite)"
    description = "Handles various JSON schema formats like Draft 7, OpenAPI, and custom schemas"
    main_extension = "json"
    all_extensions = ["json"]
    mime_types = ["application/schema+json", "application/json"]
    detection_priority = 50
    format_category = "schema"
    
    @staticmethod
    def _get_worker(schema_content: str):
        """Determine which worker should handle this schema content."""
        try:
            schema_dict = json.loads(schema_content)
            
            # Check for OpenAPI indicators first
            if any(key in schema_dict for key in ['openapi', 'swagger', 'info']):
                return _JSONSchemaOpenAPIWorker
            
            # Check for specific JSON Schema draft
            if schema_dict.get('$schema'):
                if 'draft-07' in schema_dict['$schema']:
                    return _JSONSchemaDraft7Worker
            
            # Default to Draft 7 for standard JSON schemas
            return _JSONSchemaDraft7Worker
            
        except json.JSONDecodeError:
            # If we can't parse it, default to Draft 7
            return _JSONSchemaDraft7Worker

    @staticmethod
    def parse_schema(schema_content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Parse schema content using the appropriate worker."""
        content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
        worker = JSONSchemaHandler._get_worker(content_str)
        return worker.parse(content_str)

    @staticmethod
    def serialize_schema(schema: Dict[str, Any], **kwargs: Any) -> str:
        """Serialize schema using the appropriate worker."""
        # For serialization, we can specify the format or default to Draft 7
        format_type = kwargs.get('format', 'draft7')
        
        if format_type.lower() in ['openapi', 'swagger']:
            worker = _JSONSchemaOpenAPIWorker
        else:
            worker = _JSONSchemaDraft7Worker
        
        return worker.serialize(schema)

    @staticmethod
    def validate_data(data: Any, schema: Dict[str, Any], **kwargs: Any) -> bool:
        """Validate data against schema using the appropriate worker."""
        # Use Draft 7 worker for validation by default (most comprehensive)
        return _JSONSchemaDraft7Worker.validate(data, schema)

    @staticmethod
    def generate_schema(data: Any, **kwargs: Any) -> Dict[str, Any]:
        """Generate a JSON Schema from sample data with intelligent type inference."""
        def infer_schema_for_value(value: Any, key_name: str = None) -> Dict[str, Any]:
            """Recursively infer schema for a value with enhanced type detection."""
            if isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                schema = {"type": "integer"}
                if value >= 0:
                    schema["minimum"] = 0
                return schema
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                schema = {"type": "string"}
                
                # Add format constraints based on patterns
                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                    schema["format"] = "email"
                elif re.match(r'^https?://', value):
                    schema["format"] = "uri"
                elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                    schema["format"] = "date"
                elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                    schema["format"] = "date-time"
                elif re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', value):
                    schema["format"] = "uuid"
                
                return schema
            elif isinstance(value, list):
                if not value:
                    return {"type": "array", "items": {}}
                
                # Infer schema from first item
                item_schema = infer_schema_for_value(value[0])
                return {"type": "array", "items": item_schema}
            elif isinstance(value, dict):
                properties = {}
                required = []
                
                for k, v in value.items():
                    properties[k] = infer_schema_for_value(v, k)
                    # Consider all fields required for now
                    required.append(k)
                
                schema = {"type": "object", "properties": properties}
                if required:
                    schema["required"] = required
                
                return schema
            else:
                return {"type": "string"}
        
        # Generate the schema
        schema = infer_schema_for_value(data)
        
        # Add metadata
        schema["$schema"] = _JSONSchemaDraft7Worker.DRAFT_7_META_SCHEMA
        schema["title"] = kwargs.get('title', 'Generated Schema')
        schema["description"] = kwargs.get('description', 'Auto-generated JSON Schema')
        
        return schema

    @staticmethod
    def can_handle_schema(schema_content: Union[str, bytes]) -> bool:
        """Check if this handler can handle the given schema content."""
        try:
            content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
            schema_dict = json.loads(content_str)
            
            # Check for JSON Schema indicators
            if '$schema' in schema_dict:
                return True
            
            # Check for OpenAPI/Swagger indicators
            if any(key in schema_dict for key in ['openapi', 'swagger', 'info']):
                return True
            
            # Check for basic schema structure
            if 'type' in schema_dict or 'properties' in schema_dict:
                return True
                
            return False
            
        except (json.JSONDecodeError, TypeError):
            return False

    # --- Base Handler Interface Implementation ---

    @staticmethod
    def parse(content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Base interface implementation."""
        return JSONSchemaHandler.parse_schema(content, **kwargs)

    @staticmethod
    def serialize(data: Dict[str, Any], **kwargs: Any) -> str:
        """Base interface implementation."""
        return JSONSchemaHandler.serialize_schema(data, **kwargs)

    @staticmethod
    def can_handle(content: Union[str, bytes]) -> bool:
        """Base interface implementation."""
        return JSONSchemaHandler.can_handle_schema(content)

    @staticmethod
    def is_binary_format() -> bool:
        """Check if this is a binary format."""
        return False

    @staticmethod
    def supports_feature(feature: str) -> bool:
        """Check if this handler supports a specific feature."""
        supported_features = {
            'validation': True,
            'schema_generation': True,
            'format_detection': True,
            'openapi': True,
            'swagger': True,
            'draft7': True,
            'draft6': False,
            'draft4': False,
            'draft3': False
        }
        return supported_features.get(feature, False)
