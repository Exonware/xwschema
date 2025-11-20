"""
TOML Schema Handler for xSchema framework.
Extracted from xData handlers for schema-specific operations.
"""

import json
import re
import tomllib
from typing import Any, Dict, List, Type, Union

from src.xlib.xdata.core.base_handler import aBaseHandler
from src.xlib.xschema.legacy.schema_handler import aSchemaHandler


class TOMLBaseHandler(aBaseHandler):
    """Provides common functionality for all TOML-based handlers."""
    
    title = "TOML"
    description = "Tom's Obvious Minimal Language"
    main_extension = "toml"
    all_extensions = ["toml"]
    mime_types = ["application/toml", "text/toml"]
    
    @staticmethod
    def _is_plausible_toml(content_str: str) -> bool:
        """Check if content looks like TOML."""
        content_str = content_str.strip()
        
        # Check for TOML indicators
        if '=' in content_str and not content_str.startswith('{'):
            return True
        if '[' in content_str and ']' in content_str:
            return True
        if any(line.strip().startswith('#') for line in content_str.split('\n')):
            return True
            
        return False
    
    @staticmethod
    def _parse_toml_content(content: Union[str, bytes]) -> Dict[Any, Any]:
        """Parse TOML content."""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return tomllib.loads(content)
    
    @staticmethod
    def _serialize_toml_content(data: Dict[Any, Any], **kwargs: Any) -> str:
        """Serialize data to TOML."""
        import tomli_w
        return tomli_w.dumps(data, **kwargs)
    
    @staticmethod
    def _prepare_for_toml_serialization(data: Any) -> Any:
        """Prepare data for TOML serialization."""
        if isinstance(data, dict):
            return {k: TOMLBaseHandler._prepare_for_toml_serialization(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [TOMLBaseHandler._prepare_for_toml_serialization(v) for v in data]
        else:
            return data
    
    @staticmethod
    def _convert_value_from_toml(value: Any) -> Any:
        """Convert TOML value to Python value."""
        if isinstance(value, dict):
            return {k: TOMLBaseHandler._convert_value_from_toml(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [TOMLBaseHandler._convert_value_from_toml(v) for v in value]
        else:
            return value
    
    @staticmethod
    def _detect_toml_schema_type(data: Dict[Any, Any]) -> str:
        """Detect the type of TOML configuration."""
        if not isinstance(data, dict):
            return "unknown"
        
        # Check for common configuration patterns
        if any(key in data for key in ['package', 'tool', 'build-system']):
            return "python_package"
        elif any(key in data for key in ['server', 'database', 'app', 'config']):
            return "application_config"
        elif any(key in data for key in ['dependencies', 'dev-dependencies']):
            return "dependency_config"
        else:
            return "generic_config"


class _TOMLConfigSchemaWorker:
    """Internal worker to handle configuration-specific TOML validation."""
    
    CONFIG_PATTERNS = {
        'python_package': {
            'required_fields': ['name', 'version'],
            'optional_fields': ['description', 'authors', 'dependencies', 'dev-dependencies']
        },
        'application_config': {
            'required_fields': [],
            'optional_fields': ['server', 'database', 'logging', 'security']
        },
        'dependency_config': {
            'required_fields': [],
            'optional_fields': ['dependencies', 'dev-dependencies', 'optional-dependencies']
        }
    }
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse TOML configuration schema."""
        try:
            config_data = tomllib.loads(content)
            config_type = TOMLBaseHandler._detect_toml_schema_type(config_data)
            return _TOMLConfigSchemaWorker._generate_config_schema(config_data, config_type)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML configuration: {e}")
    
    @staticmethod
    def _generate_config_schema(config_data: Dict[str, Any], config_type: str) -> Dict[str, Any]:
        """Generate a schema for TOML configuration."""
        schema = {
            "type": "object",
            "properties": {},
            "required": _TOMLConfigSchemaWorker.CONFIG_PATTERNS.get(config_type, {}).get('required_fields', []),
            "additionalProperties": True
        }
        
        for key, value in config_data.items():
            schema["properties"][key] = _TOMLConfigSchemaWorker._infer_property_schema(value, key)
        
        return schema
    
    @staticmethod
    def _infer_property_schema(value: Any, key: str) -> Dict[str, Any]:
        """Infer schema for a TOML property."""
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            schema = {"type": "integer"}
            
            # TOML configuration-specific constraints
            if 'port' in key.lower():
                schema.update({"minimum": 1, "maximum": 65535})
            elif any(x in key.lower() for x in ['timeout', 'delay', 'interval']):
                schema["minimum"] = 0
            elif value >= 0:
                schema["minimum"] = 0
            
            return schema
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, str):
            schema = {"type": "string"}
            
            # Add format constraints based on patterns and context
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                schema["format"] = "email"
            elif re.match(r'^https?://', value):
                schema["format"] = "uri"
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                schema["format"] = "date"
            elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                schema["format"] = "date-time"
            
            return schema
        elif isinstance(value, list):
            if not value:
                return {"type": "array", "items": {}}
            
            # Infer schema from first item
            item_schema = _TOMLConfigSchemaWorker._infer_property_schema(value[0], f"{key}_item")
            return {"type": "array", "items": item_schema}
        elif isinstance(value, dict):
            properties = {}
            for k, v in value.items():
                properties[k] = _TOMLConfigSchemaWorker._infer_property_schema(v, k)
            
            return {"type": "object", "properties": properties, "additionalProperties": True}
        else:
            return {"type": "string"}
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize schema to TOML format."""
        return _TOMLConfigSchemaWorker._generate_toml_template(schema)
    
    @staticmethod
    def _generate_toml_template(schema_dict: Dict[str, Any]) -> str:
        """Generate a TOML template from schema."""
        lines = ["# Generated TOML Configuration Template"]
        
        if "properties" in schema_dict:
            for prop_name, prop_schema in schema_dict["properties"].items():
                lines.extend(_TOMLConfigSchemaWorker._generate_property_template(prop_name, prop_schema))
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_property_template(name: str, schema: Dict[str, Any], indent: int = 0) -> List[str]:
        """Generate TOML template for a property."""
        lines = []
        indent_str = "  " * indent
        
        if schema.get("type") == "object" and "properties" in schema:
            lines.append(f"{indent_str}[{name}]")
            for prop_name, prop_schema in schema["properties"].items():
                lines.extend(_TOMLConfigSchemaWorker._generate_property_template(prop_name, prop_schema, indent + 1))
        else:
            example = _TOMLConfigSchemaWorker._generate_example_value(schema)
            comment = f"# {schema.get('description', '')}" if schema.get('description') else ""
            lines.append(f"{indent_str}{name} = {example} {comment}".strip())
        
        return lines
    
    @staticmethod
    def _generate_example_value(schema: Dict[str, Any]) -> str:
        """Generate an example value for a schema."""
        schema_type = schema.get("type", "string")
        
        if schema_type == "string":
            format_type = schema.get("format", "")
            if format_type == "email":
                return '"user@example.com"'
            elif format_type == "uri":
                return '"https://example.com"'
            elif format_type == "date":
                return '"2023-01-01"'
            elif format_type == "date-time":
                return '"2023-01-01T12:00:00Z"'
            else:
                return '"example_value"'
        elif schema_type == "integer":
            return "42"
        elif schema_type == "number":
            return "3.14"
        elif schema_type == "boolean":
            return "true"
        elif schema_type == "array":
            return "[]"
        elif schema_type == "object":
            return "{}"
        else:
            return '""'


class _TOMLJSONSchemaWorker:
    """Internal worker to handle JSON Schema in TOML format."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse JSON Schema content in TOML format."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                schema = json.loads(content)
            else:
                # Parse as TOML
                schema = tomllib.loads(content)
            
            # Ensure it has the correct meta-schema if not present
            if '$schema' not in schema:
                schema['$schema'] = "http://json-schema.org/draft-07/schema#"
                
            return schema
        except (json.JSONDecodeError, tomllib.TOMLDecodeError) as e:
            raise ValueError(f"Invalid TOML Schema: {e}")
    
    @staticmethod
    def serialize(schema: Dict[str, Any]) -> str:
        """Serialize JSON Schema to TOML format."""
        # For now, serialize as JSON since TOML doesn't have a standard schema format
        return json.dumps(schema, indent=2)
    
    @staticmethod
    def validate(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate data against JSON Schema in TOML format."""
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return True
        except Exception:
            return False


# --- Enhanced Schema Handler with Composite Pattern -------------------------

class TOMLSchemaHandler(TOMLBaseHandler, aSchemaHandler):
    """
    A composite schema handler for TOML.
    
    This handler acts as a dispatcher. It inspects the schema content to
    determine the appropriate TOML schema approach (Configuration validation, JSON Schema, etc.) and then
    delegates the parsing and validation to an internal, specialized worker.
    """
    
    title = "TOML Schema (Composite)"
    description = "Handles various TOML schema formats including configuration validation and JSON Schema"
    main_extension = "toml"
    all_extensions = ["toml"]
    mime_types = ["application/toml", "text/toml"]
    detection_priority = 70
    format_category = "schema"
    
    @staticmethod
    def _get_worker(schema_content: str):
        """Determine which worker should handle this schema content."""
        try:
            # Try to detect if it's JSON Schema first
            if schema_content.strip().startswith('{'):
                # JSON format - likely JSON Schema
                schema_dict = json.loads(schema_content)
                if "$schema" in schema_dict or "type" in schema_dict or "properties" in schema_dict:
                    return _TOMLJSONSchemaWorker
            else:
                # TOML format
                schema_dict = tomllib.loads(schema_content)
                
                # Check for JSON Schema indicators in TOML format
                if "$schema" in schema_dict or ("type" in schema_dict and "properties" in schema_dict):
                    return _TOMLJSONSchemaWorker
            
            # Default to configuration schema worker
            return _TOMLConfigSchemaWorker
            
        except Exception:
            # If we can't parse it, default to configuration schema
            return _TOMLConfigSchemaWorker

    @staticmethod
    def parse_schema(schema_content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Parse schema content using the appropriate worker."""
        content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
        worker = TOMLSchemaHandler._get_worker(content_str)
        return worker.parse(content_str)

    @staticmethod
    def serialize_schema(schema: Dict[str, Any], **kwargs: Any) -> str:
        """Serialize schema using the appropriate worker."""
        # For serialization, we can specify the format or default to configuration schema
        format_type = kwargs.get('format', 'config')
        
        if format_type.lower() in ['json', 'jsonschema']:
            worker = _TOMLJSONSchemaWorker
        else:
            worker = _TOMLConfigSchemaWorker
        
        return worker.serialize(schema)

    @staticmethod
    def validate_data(data: Any, schema: Dict[str, Any], **kwargs: Any) -> bool:
        """Validate data against schema using the appropriate worker."""
        # Use JSON Schema worker for validation by default (most comprehensive)
        return _TOMLJSONSchemaWorker.validate(data, schema)

    @staticmethod
    def generate_schema(data: Any, **kwargs: Any) -> Dict[str, Any]:
        """Generate a TOML schema from sample data with intelligent type inference."""
        config_type = TOMLBaseHandler._detect_toml_schema_type(data)
        
        def infer_schema_for_value(value: Any, key_name: str = None) -> Dict[str, Any]:
            """Recursively infer schema for a value with TOML-specific enhancements."""
            if isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                schema = {"type": "integer"}
                
                # TOML configuration-specific constraints
                if key_name and 'port' in key_name.lower():
                    schema.update({"minimum": 1, "maximum": 65535})
                elif key_name and any(x in key_name.lower() for x in ['timeout', 'delay', 'interval']):
                    schema["minimum"] = 0
                elif value >= 0:
                    schema["minimum"] = 0
                
                return schema
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                schema = {"type": "string"}
                
                # Add format constraints based on patterns and context
                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                    schema["format"] = "email"
                elif re.match(r'^https?://', value):
                    schema["format"] = "uri"
                elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                    schema["format"] = "date"
                elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                    schema["format"] = "date-time"
                
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
        schema["title"] = kwargs.get('title', f'Generated {config_type.title()} Schema')
        schema["description"] = kwargs.get('description', f'Auto-generated TOML {config_type} Schema')
        
        return schema

    @staticmethod
    def can_handle_schema(schema_content: Union[str, bytes]) -> bool:
        """Check if this handler can handle the given schema content."""
        try:
            content_str = schema_content.decode('utf-8') if isinstance(schema_content, bytes) else schema_content
            
            # Try JSON format first
            if content_str.strip().startswith('{'):
                schema_dict = json.loads(content_str)
                if "$schema" in schema_dict or "type" in schema_dict or "properties" in schema_dict:
                    return True
            else:
                # Try TOML format
                schema_dict = tomllib.loads(content_str)
                
                # Check for JSON Schema indicators
                if "$schema" in schema_dict:
                    return True
                
                # Check for configuration structure
                if isinstance(schema_dict, dict) and len(schema_dict) > 0:
                    return True
                
            return False
            
        except (json.JSONDecodeError, tomllib.TOMLDecodeError, TypeError):
            return False

    # --- Base Handler Interface Implementation ---

    @staticmethod
    def parse(content: Union[str, bytes], **kwargs: Any) -> Dict[str, Any]:
        """Base interface implementation."""
        return TOMLSchemaHandler.parse_schema(content, **kwargs)

    @staticmethod
    def serialize(data: Dict[str, Any], **kwargs: Any) -> str:
        """Base interface implementation."""
        return TOMLSchemaHandler.serialize_schema(data, **kwargs)

    @staticmethod
    def can_handle(content: Union[str, bytes]) -> bool:
        """Base interface implementation."""
        return TOMLSchemaHandler.can_handle_schema(content)

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
            'config_schema': True,
            'toml_schema': True
        }
        return supported_features.get(feature, False)
