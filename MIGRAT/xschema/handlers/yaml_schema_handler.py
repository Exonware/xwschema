"""
YAML Schema Handler for xSchema framework.
Extracted from xData handlers for schema-specific operations.
"""

import yaml
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


class YAMLBaseHandler(aBaseHandler):
    """Provides common functionality for all YAML-based handlers."""
    
    title = "YAML"
    description = "YAML Ain't Markup Language"
    main_extension = "yaml"
    all_extensions = ["yaml", "yml"]
    mime_types = ["application/x-yaml", "text/yaml", "text/x-yaml"]
    
    @staticmethod
    def _is_plausible_yaml(content_str: str) -> bool:
        """Check if content looks like YAML."""
        content_str = content_str.strip()
        
        # Check for YAML indicators
        if content_str.startswith('---'):
            return True
        if ':' in content_str and ('\n' in content_str or content_str.count(':') == 1):
            return True
        if content_str.startswith('- ') or content_str.startswith('['):
            return True
            
        return False
    
    @staticmethod
    def _parse_yaml_content(content: Union[str, bytes]) -> Dict[Any, Any]:
        """Parse YAML content."""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return yaml.safe_load(content)
    
    @staticmethod
    def _serialize_yaml_content(data: Dict[Any, Any], **kwargs: Any) -> str:
        """Serialize data to YAML."""
        return yaml.dump(data, default_flow_style=False, indent=2, **kwargs)
    
    @staticmethod
    def _convert_value_from_yaml(value: Any) -> Any:
        """Convert YAML value to Python value."""
        if isinstance(value, dict):
            return {k: YAMLBaseHandler._convert_value_from_yaml(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [YAMLBaseHandler._convert_value_from_yaml(v) for v in value]
        else:
            return value


class _YAMLJSONSchemaWorker:
    """Internal worker to handle JSON Schema in YAML format."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse JSON Schema content in YAML format."""
        try:
            schema = yaml.safe_load(content)
            
            # Ensure it has the correct meta-schema if not present
            if '$schema' not in schema:
                schema['$schema'] = "http://json-schema.org/draft-07/schema#"
                
            return schema
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML Schema: {e}")
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize JSON Schema to YAML format."""
        # Ensure proper formatting
        if '$schema' not in schema:
            schema['$schema'] = "http://json-schema.org/draft-07/schema#"
            
        return yaml.dump(schema, default_flow_style=False, indent=2)
    
    @staticmethod
    def validate(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate data against JSON Schema in YAML format."""
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return True
        except Exception:
            return False


class _YAMLKwalifySchemaWorker:
    """Internal worker to handle Kwalify schema format."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse Kwalify schema content."""
        try:
            kwalify_schema = yaml.safe_load(content)
            return _YAMLKwalifySchemaWorker._convert_kwalify_to_jsonschema(kwalify_schema)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid Kwalify schema: {e}")
    
    @staticmethod
    def _convert_kwalify_to_jsonschema(kwalify_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Kwalify schema to JSON Schema format."""
        if not isinstance(kwalify_schema, dict):
            return {"type": "string"}
        
        jsonschema = {"type": "object"}
        
        if "mapping" in kwalify_schema:
            properties = {}
            required = []
            
            for key, value in kwalify_schema["mapping"].items():
                if isinstance(value, dict):
                    if "type" in value:
                        properties[key] = _YAMLKwalifySchemaWorker._convert_kwalify_type_to_jsonschema(value)
                    else:
                        properties[key] = _YAMLKwalifySchemaWorker._convert_kwalify_to_jsonschema(value)
                else:
                    properties[key] = {"type": "string"}
                
                # Check if required
                if isinstance(value, dict) and value.get("required", False):
                    required.append(key)
            
            jsonschema["properties"] = properties
            if required:
                jsonschema["required"] = required
        
        elif "sequence" in kwalify_schema:
            jsonschema["type"] = "array"
            if isinstance(kwalify_schema["sequence"], dict):
                jsonschema["items"] = _YAMLKwalifySchemaWorker._convert_kwalify_to_jsonschema(kwalify_schema["sequence"])
            else:
                jsonschema["items"] = {"type": "string"}
        
        elif "type" in kwalify_schema:
            return _YAMLKwalifySchemaWorker._convert_kwalify_type_to_jsonschema(kwalify_schema)
        
        return jsonschema
    
    @staticmethod
    def _convert_kwalify_type_to_jsonschema(kwalify_type: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Kwalify type to JSON Schema type."""
        kwalify_type_name = kwalify_type.get("type", "str")
        
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "map": "object",
            "seq": "array"
        }
        
        jsonschema_type = type_mapping.get(kwalify_type_name, "string")
        result = {"type": jsonschema_type}
        
        # Add constraints
        if "pattern" in kwalify_type:
            result["pattern"] = kwalify_type["pattern"]
        if "length" in kwalify_type:
            result["minLength"] = kwalify_type["length"]
            result["maxLength"] = kwalify_type["length"]
        if "range" in kwalify_type:
            range_val = kwalify_type["range"]
            if isinstance(range_val, dict):
                if "min" in range_val:
                    result["minimum"] = range_val["min"]
                if "max" in range_val:
                    result["maximum"] = range_val["max"]
        
        return result
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize schema to Kwalify format."""
        # For now, serialize as JSON Schema in YAML format
        # Full Kwalify conversion would be more complex
        return yaml.dump(schema, default_flow_style=False, indent=2)


# --- Enhanced Schema Handler with Composite Pattern -------------------------

class YAMLSchemaHandler(YAMLBaseHandler, aSchemaHandler):
    """
    A composite schema handler for YAML.
    
    This handler acts as a dispatcher. It inspects the schema content to
    determine the specific YAML schema variant (JSON Schema in YAML, Kwalify, etc.) and then
    delegates the parsing and validation to an internal, specialized worker.
    """
    
    title = "YAML Schema (Composite)"
    description = "Handles various YAML schema formats like JSON Schema in YAML and Kwalify schemas"
    detection_priority = 60
    format_category = "schema"
    
    @staticmethod
    def _get_worker(schema_content: str):
        """Determine which worker should handle this schema content."""
        try:
            schema_dict = yaml.safe_load(schema_content)
            
            # Check for JSON Schema indicators
            if any(key in schema_dict for key in ['$schema', 'properties', 'items']):
                return _YAMLJSONSchemaWorker
            
            # Check for Kwalify indicators
            if any(key in schema_dict for key in ['mapping', 'sequence']) or schema_dict.get('type') in ['str', 'int', 'map', 'seq']:
                return _YAMLKwalifySchemaWorker
            
            # Default to JSON Schema worker
            return _YAMLJSONSchemaWorker
            
        except yaml.YAMLError:
            # If we can't parse it, default to JSON Schema
            return _YAMLJSONSchemaWorker

    @staticmethod
    def parse_schema(schema_content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Parse schema content using the appropriate worker."""
        content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
        worker = YAMLSchemaHandler._get_worker(content_str)
        return worker.parse(content_str)

    @staticmethod
    def serialize_schema(schema: Dict[str, Any], **kwargs: Any) -> str:
        """Serialize schema using the appropriate worker."""
        # For serialization, we can specify the format or default to JSON Schema
        format_type = kwargs.get('format', 'jsonschema')
        
        if format_type.lower() in ['kwalify']:
            worker = _YAMLKwalifySchemaWorker
        else:
            worker = _YAMLJSONSchemaWorker
        
        return worker.serialize(schema)

    @staticmethod
    def validate_data(data: Any, schema: Dict[str, Any], **kwargs: Any) -> bool:
        """Validate data against schema using the appropriate worker."""
        # Use JSON Schema worker for validation by default (most comprehensive)
        return _YAMLJSONSchemaWorker.validate(data, schema)

    @staticmethod
    def generate_schema(data: Any, **kwargs: Any) -> Dict[str, Any]:
        """Generate a YAML schema from sample data with intelligent type inference."""
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
                elif len(value) > 100:
                    schema["description"] = "Long text field"
                
                if key_name and 'id' in key_name.lower():
                    schema["description"] = "Identifier field"
                
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
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
        schema["title"] = kwargs.get('title', 'Generated Schema')
        schema["description"] = kwargs.get('description', 'Auto-generated YAML Schema')
        
        return schema

    @staticmethod
    def can_handle_schema(schema_content: Union[str, bytes]) -> bool:
        """Check if this handler can handle the given schema content."""
        try:
            content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
            schema_dict = yaml.safe_load(content_str)
            
            # Check for JSON Schema indicators
            if '$schema' in schema_dict:
                return True
            
            # Check for Kwalify indicators
            if any(key in schema_dict for key in ['mapping', 'sequence']):
                return True
            
            # Check for basic schema structure
            if 'type' in schema_dict or 'properties' in schema_dict:
                return True
                
            return False
            
        except (yaml.YAMLError, TypeError):
            return False

    # --- Base Handler Interface Implementation ---

    @staticmethod
    def parse(content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Base interface implementation."""
        return YAMLSchemaHandler.parse_schema(content, **kwargs)

    @staticmethod
    def serialize(data: Dict[str, Any], **kwargs: Any) -> str:
        """Base interface implementation."""
        return YAMLSchemaHandler.serialize_schema(data, **kwargs)

    @staticmethod
    def can_handle(content: Union[str, bytes]) -> bool:
        """Base interface implementation."""
        return YAMLSchemaHandler.can_handle_schema(content)

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
            'jsonschema': True,
            'kwalify': True,
            'yaml_schema': True
        }
        return supported_features.get(feature, False)
